# routes/core_push.py
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..runtime.util_cal import cal_interval
from ..runtime.util_config import save_config
from ..runtime.util_errors import ConfigurationError, SessionNotFoundError
from ..runtime.util_models import (
    ErrorsModel,
    GraphMetaModel,
    SessionActionModel,
    StatusModel,
    TaskInjectionModel,
    TerminationInjectionModel,
    WebConfigModel,
)

if TYPE_CHECKING:
    from ..server.core_server import TaskWebServer

logger = logging.getLogger("celestialflow_web.routes")


def _session_error(session_id: str, status_code: int = 409) -> JSONResponse:
    """构造会话不存在时的统一错误响应。

    :param session_id: 请求中携带的任务图实例标识
    :param status_code: HTTP 状态码，push 默认 409、pull 默认 404
    :return: 对应状态码的 JSONResponse
    """
    return JSONResponse(
        content={
            "ok": False,
            "error": "unknown session_id",
            "session_id": session_id,
        },
        status_code=status_code,
    )


def register(router: APIRouter, server: TaskWebServer, config_path: str) -> None:
    """注册所有 push 路由。

    :param router: FastAPI APIRouter 实例
    :param server: TaskWebServer 实例，提供数据存储与配置
    :param config_path: 配置文件路径
    """

    # ==== Frontend Pushes ====
    @router.post("/api/push_config", response_model=None)
    def push_config(data: WebConfigModel) -> dict[str, bool] | JSONResponse:
        """
        保存前端配置

        先落盘成功再提交内存状态，避免落盘失败后服务端已在用未持久化的配置。

        :param data: 前端配置数据
        :return: {"ok": True} 或 JSONResponse({"ok": False, "error": ...}, 500)
        """
        config_raw: Any = data.model_dump(by_alias=True)
        new_config: dict[str, Any] = cast(dict[str, Any], config_raw)
        new_interval: float = cal_interval(
            int(new_config["global"]["refreshInterval"])
        )
        try:
            save_config(new_config, config_path)
        except ConfigurationError as e:
            logger.warning("failed to save config: %s", e)
            return JSONResponse(
                content={"ok": False, "error": "Failed to save config"},
                status_code=500,
            )
        with server.config_lock:
            server.config = new_config
            server.report_interval = new_interval
        return {"ok": True}

    @router.post("/api/push_injection_tasks", response_model=None)
    def push_injection_tasks(
        data: TaskInjectionModel,
    ) -> dict[str, bool] | JSONResponse:
        """
        将前端提交的注入任务按节点覆盖写入目标会话的待执行队列。

        :param data: 注入任务数据（session_id + 节点到任务列表的映射）
        :return: {"ok": True} 或 JSONResponse({"ok": False, "error": ...}, 409)
        """
        try:
            server.add_injection_tasks(data.session_id, data.tasks)
        except SessionNotFoundError:
            return _session_error(data.session_id)
        return {"ok": True}

    @router.post("/api/push_injection_terminations", response_model=None)
    def push_injection_terminations(
        data: TerminationInjectionModel,
    ) -> dict[str, bool] | JSONResponse:
        """
        将前端提交的终止符注入目标追加到目标会话的待执行集合。

        :param data: 终止符注入数据（session_id + 节点名列表）
        :return: {"ok": True} 或 JSONResponse({"ok": False, "error": ...}, 409)
        """
        try:
            server.add_injection_terminations(data.session_id, data.nodes)
        except SessionNotFoundError:
            return _session_error(data.session_id)
        return {"ok": True}

    # ==== Session Lifecycle ====
    @router.post("/api/shutdown_session", response_model=None)
    def shutdown_session(data: SessionActionModel) -> dict[str, bool] | JSONResponse:
        """
        标记目标会话已结束（reporter 停止时通知）。

        :param data: 会话操作数据（session_id）
        :return: {"ok": True} 或 JSONResponse({"ok": False, "error": ...}, 409)
        """
        if not server.shutdown_session(data.session_id):
            return _session_error(data.session_id)
        return {"ok": True}

    @router.post("/api/remove_session", response_model=None)
    def remove_session(data: SessionActionModel) -> dict[str, bool] | JSONResponse:
        """
        彻底移除目标会话并删除其临时错误数据库。

        :param data: 会话操作数据（session_id）
        :return: {"ok": True} 或 JSONResponse({"ok": False, "error": ...}, 404)
        """
        if not server.remove_session(data.session_id):
            return _session_error(data.session_id, status_code=404)
        return {"ok": True}

    # ==== Reporter / Backend Pushes ====
    @router.post("/api/push_graph_meta", response_model=None)
    def push_graph_meta(data: GraphMetaModel) -> dict[str, bool] | JSONResponse:
        """
        更新目标会话的图元信息（图结构 + 节点构建期元信息 + 图分析结果）并推进版本号。

        三者同属构建期冻结信息，随首次 push 一并到达，因此合并为单次原子写入。

        :param data: 图元信息数据
        :return: {"ok": True} 或 JSONResponse({"ok": False, "error": ...}, 409)
        """
        payload = data.model_dump(exclude={"session_id"})
        try:
            server.update_graph_meta_store(data.session_id, payload)
        except SessionNotFoundError:
            return _session_error(data.session_id)
        return {"ok": True}

    @router.post("/api/push_status", response_model=None)
    def push_status(data: StatusModel) -> dict[str, bool] | JSONResponse:
        """
        更新目标会话的各节点运行状态并推进版本号。

        :param data: 节点状态数据
        :return: {"ok": True} 或 JSONResponse({"ok": False, "error": ...}, 409)
        """
        try:
            server.update_status_store(data.session_id, float(data.timestamp), data.status)
        except SessionNotFoundError:
            return _session_error(data.session_id)
        return {"ok": True}

    @router.post("/api/push_errors", response_model=None)
    def push_errors(data: ErrorsModel) -> dict[str, bool] | JSONResponse:
        """
        将错误日志列表写入目标会话的错误数据库。

        :param data: 错误内容数据
        :return: {"ok": True} 或 JSONResponse({"ok": False, "error": ...}, 409)
        """
        try:
            server.update_errors_store(data.session_id, data.errors)
        except SessionNotFoundError:
            return _session_error(data.session_id)
        return {"ok": True}

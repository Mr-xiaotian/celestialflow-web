# routes/core_pull.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..runtime.util_cal import normalize_errors_query
from ..runtime.util_errors import SessionNotFoundError

if TYPE_CHECKING:
    from ..server.core_server import TaskWebServer


def _session_error(graph_id: str) -> JSONResponse:
    """构造会话不存在时的统一 404 响应。

    :param graph_id: 请求中携带的任务图实例标识
    :return: 404 JSONResponse
    """
    return JSONResponse(
        content={
            "ok": False,
            "error": "unknown graph_id",
            "graph_id": graph_id,
        },
        status_code=404,
    )


def register(router: APIRouter, server: TaskWebServer) -> None:
    """注册所有 pull 路由。

    :param router: FastAPI APIRouter 实例
    :param server: TaskWebServer 实例，提供数据存储与配置
    """

    # ==== Reporter / Backend Pulls ====
    @router.get("/api/pull_server_state", response_model=None)
    def pull_server_state(graph_id: str = "") -> dict[str, Any] | JSONResponse:
        """创建或刷新 graph 会话，并返回 reporter 同步决策所需的服务端状态。

        :param graph_id: reporter 当前任务图实例的唯一标识
        :return: {"graph_id": str, "interval": float, "has_graph_meta": bool, "has_status": bool, "alive": bool, "max_event_id_in_fail": int | None}
        """
        if not graph_id:
            return _session_error(graph_id)
        return server.get_server_state(graph_id)

    @router.get("/api/pull_injection", response_model=None)
    def pull_injection(graph_id: str = "") -> dict[str, Any] | JSONResponse:
        """取出并清空指定会话待执行的前端注入任务与终止符。

        :param graph_id: reporter 当前任务图实例的唯一标识
        :return: ``{"tasks": dict[str, list[Any]], "terminations": list[str]}``
        """
        try:
            return server.get_injection(graph_id)
        except SessionNotFoundError:
            return _session_error(graph_id)

    # ==== Sessions ====
    @router.get("/api/pull_sessions")
    def pull_sessions() -> list[dict[str, Any]]:
        """返回服务端当前持有的全部 graph 会话摘要。

        :return: 会话摘要列表，按创建时间倒序
        """
        return server.list_sessions()

    # ==== Frontend Pulls ====
    @router.get("/api/pull_config")
    def pull_config() -> dict[str, Any]:
        """获取前端配置

        :return: 前端配置字典
        """
        return server.get_config()

    @router.get("/api/pull_status", response_model=None)
    def pull_status(graph_id: str = "", known_rev: int = -1) -> dict[str, Any] | JSONResponse:
        """
        返回指定会话各节点运行状态；若版本未变则返回 data=null。

        :param graph_id: 目标任务图实例的唯一标识
        :param known_rev: 客户端已知的版本号
        :return: {"rev": int, "timestamp": float, "data": dict | None}
        """
        try:
            rev, status_timestamp, status_store = server.get_status_snapshot(graph_id)
        except SessionNotFoundError:
            return _session_error(graph_id)
        if known_rev == rev:
            return {"rev": rev, "timestamp": status_timestamp, "data": None}
        return {
            "rev": rev,
            "timestamp": status_timestamp,
            "data": status_store,
        }

    @router.get("/api/pull_graph_meta", response_model=None)
    def pull_graph_meta(graph_id: str = "", known_rev: int = -1) -> dict[str, Any] | JSONResponse:
        """
        返回指定会话的图元信息（结构 + 节点元信息 + 分析）；若版本未变则返回 data=null。

        :param graph_id: 目标任务图实例的唯一标识
        :param known_rev: 客户端已知的版本号
        :return: {"rev": int, "data": dict | None}
        """
        try:
            rev, graph_meta_store = server.get_graph_meta_snapshot(graph_id)
        except SessionNotFoundError:
            return _session_error(graph_id)
        if known_rev == rev:
            return {"rev": rev, "data": None}
        return {"rev": rev, "data": graph_meta_store}

    @router.get("/api/pull_errors", response_model=None)
    def pull_errors(
        graph_id: str = "",
        known_rev: int = -1,
        page: int = 1,
        page_size: int = 10,
        node: str = "",
        keyword: str = "",
        sort_order: str = "newest",
    ) -> dict[str, Any] | JSONResponse:
        """
        返回指定会话的错误日志分页数据；若版本未变则返回 data=null。

        :param graph_id: 目标任务图实例的唯一标识
        :param known_rev: 客户端已知的版本号，默认 -1
        :param page: 页码，默认 1
        :param page_size: 每页大小，默认 10
        :param node: 节点名称过滤，默认 ""
        :param keyword: 关键词过滤，默认 ""
        :param sort_order: 排序方式，支持 newest / oldest
        :return: {"rev": int, "page": int, "page_size": int, "total": int, "total_pages": int, "data": list | None}
        """
        (
            normalized_page,
            normalized_page_size,
            normalized_node,
            normalized_keyword,
            normalized_sort_order,
        ) = normalize_errors_query(page, page_size, node, keyword, sort_order)
        try:
            rev, total, total_pages, page_items = server.get_errors_page(
                graph_id,
                normalized_page,
                normalized_page_size,
                normalized_node,
                normalized_keyword,
                normalized_sort_order,
            )
        except SessionNotFoundError:
            return _session_error(graph_id)

        base = {
            "rev": rev,
            "page": min(normalized_page, total_pages),
            "page_size": normalized_page_size,
            "total": total,
            "total_pages": total_pages,
            "sort_order": normalized_sort_order,
        }
        if known_rev == rev:
            return {**base, "data": None}
        return {**base, "data": page_items}

    @router.get("/api/pull_error_type_counts", response_model=None)
    def pull_error_type_counts(
        graph_id: str = "", known_rev: int = -1, node: str = ""
    ) -> dict[str, Any] | JSONResponse:
        """
        返回指定会话按错误类型聚合后的统计结果；若版本未变则返回 data=null。

        :param graph_id: 目标任务图实例的唯一标识
        :param known_rev: 客户端已知的版本号，默认 -1
        :param node: 节点名称过滤，默认 ""
        :return: {"rev": int, "data": list[dict[str, Any]] | None}
        """
        try:
            rev, items = server.get_error_type_counts(graph_id, node)
        except SessionNotFoundError:
            return _session_error(graph_id)
        if known_rev == rev:
            return {"rev": rev, "data": None}
        return {"rev": rev, "data": items}

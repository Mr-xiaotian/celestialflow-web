# server/core_server.py
from __future__ import annotations

import argparse
import copy
import logging
import os
import tempfile
import threading
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, cast

import uvicorn
from fastapi import (
    FastAPI,
)
from fastapi.staticfiles import (
    StaticFiles,
)
from fastapi.templating import (
    Jinja2Templates,
)

from ..routes import create_router
from ..runtime.util_config import load_config
from ..runtime.util_errors import SessionNotFoundError
from ..runtime.util_models import WebConfigModel
from ..runtime.util_sqlite import (
    append_records,
    connect_db,
    get_max_event_id_in_fail,
    load_records,
    query_error_type_counts,
    query_records,
)

PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PACKAGE_DIR, "config.json")

logger = logging.getLogger("celestialflow_web.server")

static_path = os.path.join(PACKAGE_DIR, "static")
templates_path = os.path.join(PACKAGE_DIR, "templates")


def _empty_graph_meta() -> dict[str, Any]:
    """构造一份空的图元信息缓存，供新建会话初始化。"""
    return {
        "graph": "",
        "graph_mode": "",
        "start_time": 0.0,
        "class_name": "",
        "is_dag": False,
        "nodes": [],
        "edges": {},
        "source_nodes": [],
        "node_meta": {},
    }


class GraphSession:
    """
    单个任务图运行实例在服务端的会话上下文。

    每个会话独占自己的状态缓存、图元信息缓存、错误数据库与待注入队列，
    不同会话之间互不干扰；错误数据库在创建时使用 ``tempfile.mkstemp``
    手动管理文件描述符，避免 Windows 上自动删除与重打开冲突。

    :param session_id: 任务图实例的唯一标识（不透明串）
    :param name: 任务图名称；由 ``push_graph_meta`` 携带的 ``graph`` 补齐，
        未到达前等于 ``session_id``
    """

    def __init__(self, session_id: str, name: str) -> None:
        """
        初始化会话上下文。

        :param session_id: 任务图实例的唯一标识
        :param name: 任务图名称
        """
        self.session_id: str = session_id
        self.name: str = name

        self.status_store: dict[str, dict[str, Any]] = {}
        self.status_timestamp: float = 0.0
        self.graph_meta_store: dict[str, Any] = _empty_graph_meta()
        # 是否收到过对应 store 的写入。用显式标志而非“内容是否为空”判断，
        # 避免空图（无节点）被误判为从未收到图元信息而反复重推。
        self.graph_meta_seen: bool = False
        self.status_seen: bool = False
        self.injection_tasks: dict[str, list[Any]] = {}
        self.injection_terminations: set[str] = set()

        fd, records_db_path = tempfile.mkstemp(
            prefix="celestialflow-web-records-", suffix=".sqlite3"
        )
        os.close(fd)
        self.records_db_path: str = records_db_path
        try:
            conn = connect_db(self.records_db_path)
            conn.close()
        except Exception:
            # 建库失败时回收已创建的临时文件，避免留下无人引用的孤儿文件。
            self._remove_db_files()
            raise

        # 各类 store 的 rev + payload 需要原子读写，避免 pull 读到撕裂快照
        self.status_lock: threading.Lock = threading.Lock()
        self.graph_meta_lock: threading.Lock = threading.Lock()
        self.errors_lock: threading.Lock = threading.Lock()
        self.task_injection_lock: threading.Lock = threading.Lock()

        # 每次 push 时递增，pull 时对比，无变化则返回 null data
        self.store_revs: dict[str, int] = {
            "status": 0,
            "graph_meta": 0,
            "errors": 0,
        }

        self.alive: bool = True
        self.shutdown_reason: str | None = None
        self.created_at: float = time.time()
        self.last_seen: float = self.created_at

    def touch(self) -> None:
        """刷新会话最近活跃时间。"""
        self.last_seen = time.time()

    def summary(self) -> dict[str, Any]:
        """
        返回会话的元信息摘要，供前端会话列表使用。

        :return: 会话摘要字典
        :rtype: dict[str, Any]
        """
        with self.status_lock:
            has_status = self.status_seen
        with self.graph_meta_lock:
            has_graph_meta = self.graph_meta_seen
        return {
            "session_id": self.session_id,
            "name": self.name,
            "alive": self.alive,
            "shutdown_reason": self.shutdown_reason,
            "created_at": self.created_at,
            "last_seen": self.last_seen,
            "has_graph_meta": has_graph_meta,
            "has_status": has_status,
        }

    def close(self) -> None:
        """释放会话占用的临时错误数据库文件（含 WAL 旁路文件）。"""
        self._remove_db_files()

    def _remove_db_files(self) -> None:
        """
        删除临时错误数据库及其 WAL/SHM 旁路文件。

        删除失败（如 Windows 上仍被占用）只记录告警，不向上抛出，
        以免遮蔽调用方的原始异常。
        """
        for suffix in ("", "-wal", "-shm"):
            path = self.records_db_path + suffix
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
            except OSError as e:
                logger.warning("failed to remove session db file %s: %s", path, e)


class TaskWebServer:
    """
    FastAPI Web 服务，提供任务可视化、状态推送和任务注入接口。

    服务端按 ``session_id`` 维护多个 :class:`GraphSession`，允许多个任务图
    运行实例（通常位于不同进程或不同机器）同时上报，前端可在会话之间切换。
    """

    def __init__(
        self, host: str = "0.0.0.0", port: int = 5000, log_level: str = "info"
    ) -> None:
        """
        初始化 FastAPI 应用、会话容器、版本计数器及路由。

        :param host: 绑定主机地址，默认 "0.0.0.0"
        :param port: 绑定端口，默认 5000
        :param log_level: uvicorn 日志级别，默认 "info"
        """
        self.app: FastAPI = FastAPI(lifespan=self._lifespan)
        self.host: str = host
        self.port: int = port
        self.log_level: str = log_level

        if os.path.isdir(static_path):
            self.app.mount("/static", StaticFiles(directory=static_path), name="static")

        self.templates: Jinja2Templates = Jinja2Templates(directory=templates_path)

        # 所有 graph 会话，键为 session_id
        self.sessions: dict[str, GraphSession] = {}

        # 会话列表自身的增删由该锁保护；会话内部状态由各自 store 锁保护
        self.sessions_lock: threading.Lock = threading.Lock()

        # 数据版本号保留全局单调递增：任意会话的 push 都会推进全局 rev，
        # 因此前端切换会话后 known_rev 必然不相等，可直接拿到全量数据。
        self.store_revs: dict[str, int] = {
            "status": 0,
            "graph_meta": 0,
            "errors": 0,
        }
        self.rev_lock: threading.Lock = threading.Lock()

        # 加载配置
        config_raw: Any = WebConfigModel.model_validate(
            load_config(CONFIG_PATH)
        ).model_dump(by_alias=True)
        self.config: dict[str, Any] = cast(dict[str, Any], config_raw)
        self.config_lock: threading.Lock = threading.Lock()
        self.config_path: str = CONFIG_PATH

        # 供 lifespan 关闭阶段反查自身（实例由 uvicorn 持有）。
        self.app.state.server = self

        self._setup_routes()

    @staticmethod
    @asynccontextmanager
    async def _lifespan(app: FastAPI) -> AsyncGenerator[None]:
        """
        应用生命周期钩子：进程退出时释放全部会话的临时数据库文件。

        不使用该钩子时，`tempfile` 创建的会话库会随进程退出残留在磁盘上。

        :param app: FastAPI 应用实例（用于反查 server 实例）
        :return: 异步上下文管理器，退出时为关闭阶段
        :rtype: AsyncGenerator[None]
        """
        yield
        # 关闭阶段：实例由 uvicorn 持有，通过 app.state 反查。
        server: TaskWebServer | None = getattr(app.state, "server", None)
        if server is not None:
            server.close_all_sessions()

    def close_all_sessions(self) -> None:
        """
        移除并释放当前持有的全部会话。

        :return: None
        """
        with self.sessions_lock:
            sessions = list(self.sessions.values())
            self.sessions.clear()
            for session in sessions:
                session.close()

    # ==== Session Lifecycle ====
    def create_session(self, session_id: str) -> GraphSession:
        """
        创建一个新的 graph 会话并登记到会话表。

        若已存在同 `session_id` 的会话则直接返回既有实例，不会重建缓存。
        显示名先以 `session_id` 占位，待 ``push_graph_meta`` 到达后再补齐。

        :param session_id: 任务图实例的唯一标识
        :return: 新建或既有的会话上下文
        :rtype: GraphSession
        """
        with self.sessions_lock:
            existing = self.sessions.get(session_id)
            if existing is not None:
                return existing
            session = GraphSession(session_id=session_id, name=session_id)
            self.sessions[session_id] = session
            return session

    def get_session(self, session_id: str) -> GraphSession | None:
        """
        读取指定会话，不存在时返回 ``None``。

        :param session_id: 任务图实例的唯一标识
        :return: 对应会话或 ``None``
        :rtype: GraphSession | None
        """
        with self.sessions_lock:
            return self.sessions.get(session_id)

    def require_session(self, session_id: str) -> GraphSession:
        """
        读取指定会话，不存在时抛出 :class:`SessionNotFoundError`。

        :param session_id: 任务图实例的唯一标识
        :return: 对应会话
        :rtype: GraphSession
        :raises SessionNotFoundError: 会话不存在时触发
        """
        session = self.get_session(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)
        return session

    def ensure_session(self, session_id: str) -> GraphSession:
        """
        确保指定会话存在并刷新其活跃时间。

        图元信息写入（会话注册入口）时调用：会话不存在时自动创建，
        并以本次写入刷新 :attr:`GraphSession.last_seen`。

        :param session_id: 任务图实例的唯一标识
        :return: 对应会话
        :rtype: GraphSession
        """
        session = self.create_session(session_id)
        session.touch()
        return session

    def list_sessions(self) -> list[dict[str, Any]]:
        """
        返回全部会话的摘要列表，按创建时间倒序排列。

        :return: 会话摘要列表
        :rtype: list[dict[str, Any]]
        """
        with self.sessions_lock:
            sessions = list(self.sessions.values())
        summaries = [session.summary() for session in sessions]
        summaries.sort(key=lambda item: item["created_at"], reverse=True)
        return summaries

    def shutdown_session(self, session_id: str) -> bool:
        """
        标记会话为已结束（reporter 主动通知）。

        会话数据与错误数据库会保留，前端仍可切回查看；重复调用是幂等的。

        :param session_id: 任务图实例的唯一标识
        :return: 是否命中了已存在的会话
        :rtype: bool
        """
        session = self.get_session(session_id)
        if session is None:
            return False
        session.alive = False
        session.shutdown_reason = "reporter_stopped"
        session.touch()
        return True

    def remove_session(self, session_id: str) -> bool:
        """
        彻底移除会话：释放缓存并删除其临时错误数据库文件。

        删除在 `sessions_lock` 内完成，确保没有其它线程能在摘除后、
        删除前拿到该会话引用（否则在途请求会重建已删除的 sqlite 文件）。

        :param session_id: 任务图实例的唯一标识
        :return: 是否移除了一个已存在的会话
        :rtype: bool
        """
        with self.sessions_lock:
            session = self.sessions.pop(session_id, None)
            if session is None:
                return False
            session.close()
        return True

    # ==== Rev Management ====
    def _next_rev(self, key: str) -> int:
        """
        推进并返回全局版本号计数器中指定键的值。

        :param key: 版本号键，可选 ``status`` / ``graph_meta`` / ``errors``
        :return: 推进后的版本号
        :rtype: int
        """
        with self.rev_lock:
            self.store_revs[key] += 1
            return self.store_revs[key]

    # ==== Store Writes ====
    def update_graph_meta_store(self, session_id: str, graph_meta: dict[str, Any]) -> None:
        """
        原子更新指定会话的图元信息缓存（结构 + 节点元信息 + 分析）并推进版本号。

        图元信息写入是会话注册入口：会话不存在时自动创建，并以本次写入刷新活跃时间。

        :param session_id: 任务图实例的唯一标识
        :param graph_meta: 最新图元信息数据
        :return: None
        """
        session = self.ensure_session(session_id)
        with session.graph_meta_lock:
            session.graph_meta_store = copy.deepcopy(graph_meta)
            session.graph_meta_seen = True
            # 图元信息里的 graph 是本会话的权威显示名，到达即补齐。
            name = session.graph_meta_store.get("graph")
            if isinstance(name, str) and name:
                session.name = name
            session.store_revs["graph_meta"] = self._next_rev("graph_meta")

    def update_status_store(
        self, session_id: str, timestamp: float, status: dict[str, dict[str, Any]]
    ) -> None:
        """
        原子更新指定会话的状态快照、时间戳及其版本号。

        内容与上次相同时不替换、不推进版本号：上报方现在每拍无条件推送，
        判重收敛到服务端，未变化的快照不会让前端拿到新 ``rev``
        （即 ``pull_status`` 可继续返回 ``data=null``）。

        会话必须已存在（由图元信息注册）；无论内容是否变化，本次写入都会
        刷新活跃时间。

        :param session_id: 任务图实例的唯一标识
        :param timestamp: 当前状态快照对应的统一时间戳
        :param status: 各节点状态快照
        :return: None
        :raises SessionNotFoundError: 会话不存在时触发
        """
        session = self.require_session(session_id)
        session.touch()
        with session.status_lock:
            if session.status_seen and session.status_store == status:
                return
            session.status_timestamp = timestamp
            session.status_store = copy.deepcopy(status)
            session.status_seen = True
            session.store_revs["status"] = self._next_rev("status")

    def update_errors_store(self, session_id: str, errors: list[dict[str, Any]]) -> None:
        """
        原子更新指定会话的错误缓存及其版本号。

        会话必须已存在（由图元信息注册）；本次写入会刷新活跃时间。

        :param session_id: 任务图实例的唯一标识
        :param errors: 待写入的错误记录列表
        :return: None
        :raises SessionNotFoundError: 会话不存在时触发
        """
        session = self.require_session(session_id)
        session.touch()
        with session.errors_lock:
            _ = append_records(session.records_db_path, errors)
            session.store_revs["errors"] = self._next_rev("errors")

    def add_injection_tasks(self, session_id: str, tasks: dict[str, list[Any]]) -> None:
        """
        将前端提交的注入任务按节点覆盖写入指定会话的待执行队列。

        :param session_id: 任务图实例的唯一标识
        :param tasks: 节点名到任务列表的映射
        :return: None
        :raises SessionNotFoundError: 会话不存在时触发
        """
        session = self.require_session(session_id)
        with session.task_injection_lock:
            for node_name, task_list in tasks.items():
                session.injection_tasks[node_name] = task_list

    def add_injection_terminations(self, session_id: str, nodes: list[str]) -> None:
        """
        将前端提交的终止符注入目标追加到指定会话的待执行集合。

        :param session_id: 任务图实例的唯一标识
        :param nodes: 待注入终止符的节点名列表
        :return: None
        :raises SessionNotFoundError: 会话不存在时触发
        """
        session = self.require_session(session_id)
        with session.task_injection_lock:
            for node_name in nodes:
                session.injection_terminations.add(str(node_name))

    # ==== Store Reads ====
    def get_graph_meta_snapshot(self, session_id: str) -> tuple[int, dict[str, Any]]:
        """
        原子读取指定会话的图元信息缓存快照。

        :param session_id: 任务图实例的唯一标识
        :return: ``(rev, graph_meta_store)``
        :rtype: tuple[int, dict[str, Any]]
        :raises SessionNotFoundError: 会话不存在时触发
        """
        session = self.require_session(session_id)
        with session.graph_meta_lock:
            return (
                session.store_revs["graph_meta"],
                copy.deepcopy(session.graph_meta_store),
            )

    def get_config(self) -> dict[str, Any]:
        """
        读取前端配置。

        :return: 前端配置字典
        :rtype: dict[str, Any]
        """
        with self.config_lock:
            return self.config

    def get_status_snapshot(
        self, session_id: str
    ) -> tuple[int, float, dict[str, dict[str, Any]]]:
        """
        原子读取指定会话的状态缓存快照。

        :param session_id: 任务图实例的唯一标识
        :return: ``(rev, timestamp, status_store)``
        :rtype: tuple[int, float, dict[str, dict[str, Any]]]
        :raises SessionNotFoundError: 会话不存在时触发
        """
        session = self.require_session(session_id)
        with session.status_lock:
            return (
                session.store_revs["status"],
                session.status_timestamp,
                copy.deepcopy(session.status_store),
            )

    def get_errors_snapshot(self, session_id: str) -> tuple[int, list[dict[str, Any]]]:
        """
        原子读取指定会话的错误缓存快照。

        :param session_id: 任务图实例的唯一标识
        :return: ``(rev, errors)``
        :rtype: tuple[int, list[dict[str, Any]]]
        :raises SessionNotFoundError: 会话不存在时触发
        """
        session = self.require_session(session_id)
        with session.errors_lock:
            return session.store_revs["errors"], load_records(session.records_db_path)

    def get_injection(self, session_id: str) -> dict[str, Any]:
        """
        原子取出并清空指定会话的待注入任务与终止符。

        :param session_id: 任务图实例的唯一标识
        :return: ``{"tasks": dict[str, list[Any]], "terminations": list[str]}``
        :rtype: dict[str, Any]
        :raises SessionNotFoundError: 会话不存在时触发
        """
        session = self.require_session(session_id)
        with session.task_injection_lock:
            tasks = copy.deepcopy(session.injection_tasks)
            terminations = sorted(session.injection_terminations)
            session.injection_tasks = {}
            session.injection_terminations = set()
            return {"tasks": tasks, "terminations": terminations}

    def get_errors_page(
        self,
        session_id: str,
        page: int,
        page_size: int,
        node: str,
        keyword: str,
        sort_order: str,
    ) -> tuple[int, int, int, list[dict[str, Any]]]:
        """
        原子读取指定会话的错误缓存版本号与分页结果。

        :param session_id: 任务图实例的唯一标识
        :param page: 请求页码
        :param page_size: 每页大小
        :param node: 节点名称过滤条件
        :param keyword: 关键词过滤条件
        :param sort_order: 排序方式，支持 ``newest`` 或 ``oldest``
        :return: ``(rev, total, total_pages, page_items)``
        :rtype: tuple[int, int, int, list[dict[str, Any]]]
        :raises SessionNotFoundError: 会话不存在时触发
        """
        session = self.require_session(session_id)
        with session.errors_lock:
            rev = session.store_revs["errors"]
            total, total_pages, page_items = query_records(
                session.records_db_path, page, page_size, node, keyword, sort_order
            )
            return rev, total, total_pages, page_items

    def get_error_type_counts(
        self, session_id: str, node: str = ""
    ) -> tuple[int, list[dict[str, Any]]]:
        """
        原子读取指定会话的错误缓存版本号与按错误类型聚合后的统计结果。

        :param session_id: 任务图实例的唯一标识
        :param node: 节点名称过滤条件；为空时统计全部节点
        :return: ``(rev, items)``
        :rtype: tuple[int, list[dict[str, Any]]]
        :raises SessionNotFoundError: 会话不存在时触发
        """
        session = self.require_session(session_id)
        with session.errors_lock:
            rev = session.store_revs["errors"]
            items = query_error_type_counts(session.records_db_path, node=node)
            return rev, items

    def get_max_event_id_in_fail(self, session_id: str) -> int | None:
        """
        原子读取指定会话错误缓存中失败记录的最大 ``event_id``。

        :param session_id: 任务图实例的唯一标识
        :return: 当前缓存中失败记录的最大 ``event_id``；若不存在失败记录则返回 ``None``
        :rtype: int | None
        :raises SessionNotFoundError: 会话不存在时触发
        """
        session = self.require_session(session_id)
        with session.errors_lock:
            return get_max_event_id_in_fail(session.records_db_path)

    # ==== Application Lifecycle ====
    def _setup_routes(self) -> None:
        """
        注册所有 HTTP 路由。

        :return: None
        """
        self.app.include_router(create_router(self))

    def start_server(self) -> None:
        """
        启动 uvicorn 服务并阻塞到进程退出。

        :return: None
        """
        uvicorn.run(self.app, host=self.host, port=self.port, log_level=self.log_level)


def parse_args() -> argparse.Namespace:
    """解析命令行参数：--host、--port、--log-level。"""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="task-web",
        description="CelestialFlow Task Web Monitor Server",
    )

    _ = parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Bind host (default: 0.0.0.0)",
    )

    _ = parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Bind port (default: 5000)",
    )

    _ = parser.add_argument(
        "--log-level",
        default="info",
        type=lambda s: s.lower(),
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Uvicorn log level",
    )

    return parser.parse_args()


def main_entry() -> None:
    """CLI 入口：解析参数并启动 TaskWebServer。"""
    args: argparse.Namespace = parse_args()

    server: TaskWebServer = TaskWebServer(
        host=cast(str, args.host),
        port=cast(int, args.port),
        log_level=cast(str, args.log_level),
    )

    server.start_server()


# 运行入口
if __name__ == "__main__":
    main_entry()

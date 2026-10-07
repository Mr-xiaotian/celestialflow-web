# runtime/util_models.py
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GraphMetaModel(BaseModel):
    """图元信息数据模型：图结构、节点构建期元信息与分析结果"""

    session_id: str = ""
    graph: str = ""
    graph_mode: str = ""
    start_time: float = 0.0
    class_name: str = ""
    is_dag: bool = False
    nodes: list[str] = Field(default_factory=list)
    edges: dict[str, list[str]] = Field(default_factory=dict)
    source_nodes: list[str] = Field(default_factory=list)
    node_meta: dict[str, dict[str, Any]] = Field(default_factory=dict)


class SnapshotModel(BaseModel):
    """状态快照数据模型"""

    session_id: str = ""
    timestamp: float
    snapshot: dict[str, dict[str, Any]]


class ErrorModel(BaseModel):
    """单条错误数据模型"""

    session_id: str = ""
    event_id: int
    node: str = ""
    task_json: Any = None
    error_type: str = ""
    error_message: str = ""
    ts: float = 0.0


class TaskInjectionModel(BaseModel):
    """任务注入请求模型：按 graph 会话投递的 {node_name: [tasklist]} 映射"""

    session_id: str = ""  # 目标任务图会话标识
    tasks: dict[str, list[Any]] = Field(default_factory=dict)  # 节点名到任务列表的映射


class TerminationInjectionModel(BaseModel):
    """终止符注入请求模型：按 graph 会话投递的节点名列表。"""

    session_id: str = ""  # 目标任务图会话标识
    nodes: list[str] = Field(default_factory=list)  # 待注入终止符的节点名列表


class SessionActionModel(BaseModel):
    """会话级操作（shutdown / remove）请求模型"""

    session_id: str = ""  # 目标会话的任务图实例标识


class DashboardConfigModel(BaseModel):
    """仪表盘卡片布局配置模型"""

    left: list[str]
    middle: list[str]
    right: list[str]


class GlobalConfigModel(BaseModel):
    """全局共享配置模型"""

    theme: str
    autoRefreshEnabled: bool = True
    refreshInterval: int
    language: str = "zh-CN"


class DashboardPageConfigModel(BaseModel):
    """仪表盘页面配置模型"""

    historyLimit: int
    structureEdgeLabel: str = "none"
    useTotalPendingInStatus: bool = False
    layout: DashboardConfigModel


class ErrorsPageConfigModel(BaseModel):
    """错误页配置模型"""

    pageSize: int = 10
    sortOrder: str = "newest"
    jumpToInjectionAfterRetry: bool = True
    columns: list[str] = Field(
        default_factory=lambda: [
            "index",
            "event_id",
            "message",
            "node",
            "task",
            "time",
            "retry",
        ]
    )


class InjectionPageConfigModel(BaseModel):
    """注入页配置模型。"""

    showInjectableOnly: bool = True


class WebConfigModel(BaseModel):
    """Web UI 分组配置模型"""

    global_: GlobalConfigModel = Field(alias="global")
    dashboard: DashboardPageConfigModel
    errors: ErrorsPageConfigModel
    injection: InjectionPageConfigModel = Field(
        default_factory=InjectionPageConfigModel
    )

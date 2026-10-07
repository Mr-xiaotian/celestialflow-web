# runtime/util_errors.py
from __future__ import annotations

# ==== 基础异常 ====


class CelestialFlowWebError(Exception):
    """CelestialFlow 所有自定义异常的基类"""

    pass


# ==== 配置与选项 ====


class ConfigurationError(CelestialFlowWebError):
    """配置错误（参数非法、组合不支持等）"""

    pass


# ==== 会话 ====


class SessionNotFoundError(CelestialFlowWebError):
    """请求的 graph 会话不存在（未建立或已被移除）"""

    def __init__(self, session_id: str) -> None:
        """
        初始化会话不存在异常。

        :param session_id: 请求中携带的任务图实例标识
        """
        self.session_id: str = session_id
        super().__init__(f"graph session not found: {session_id!r}")

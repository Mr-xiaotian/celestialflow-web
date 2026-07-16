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

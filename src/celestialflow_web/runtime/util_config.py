# runtime/util_config.py
from __future__ import annotations

import json
import os
import tempfile
from contextlib import suppress
from typing import Any, cast

from .util_errors import ConfigurationError


def load_config(config_path: str) -> dict[str, Any]:
    """
    从指定路径加载并校验前端配置，返回序列化后的字典。

    :param config_path: 配置文件路径
    :return: 配置字典
    :raises ConfigurationError: 配置文件不存在或内容非法时抛出
    """
    if not os.path.exists(config_path):
        raise ConfigurationError(f"config file not found: {config_path}")
    try:
        with open(config_path, encoding="utf-8") as f:
            data: object = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
        raise ConfigurationError(f"failed to load config: {e}") from e
    if not isinstance(data, dict):
        raise ConfigurationError(
            f"config root must be a JSON object, got {type(data).__name__}"
        )
    return cast(dict[str, Any], data)


def save_config(config: dict[str, Any], config_path: str) -> bool:
    """
    将前端配置原子写入 config.json，返回是否成功。

    先写同目录临时文件再 ``os.replace``，避免进程中途退出把原文件截断成非法 JSON。

    :param config: 配置字典
    :param config_path: 配置文件路径
    :return: 是否保存成功
    :raises ConfigurationError: 写入或替换失败时抛出
    """
    directory = os.path.dirname(os.path.abspath(config_path)) or "."
    tmp_path: str | None = None
    try:
        fd, tmp_path = tempfile.mkstemp(
            prefix=".celestialflow-config-", suffix=".tmp", dir=directory
        )
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        os.replace(tmp_path, config_path)
        return True
    except OSError as e:
        raise ConfigurationError(f"failed to save config: {e}") from e
    finally:
        if tmp_path is not None and os.path.exists(tmp_path):
            with suppress(OSError):
                os.remove(tmp_path)

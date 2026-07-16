# runtime 包入口

> 📅 最后更新日期: 2026/07/16

## 作用

`celestialflow_web.runtime` 汇总 Web 服务运行时依赖的工具函数、数据模型和 SQLite 访问函数，对外提供统一导出，供 `server/` 与 `routes/` 调用。

## 公开导出

| 符号 | 来源 | 说明 |
|------|------|------|
| `WebConfigModel` | `util_models.py` | 前端分组配置模型 |
| `append_records` | `util_sqlite.py` | 追加错误记录 |
| `cal_interval` | `util_cal.py` | 将毫秒刷新间隔归一化为秒 |
| `clear_records` | `util_sqlite.py` | 清空错误记录 |
| `connect_db` | `util_sqlite.py` | 打开 SQLite 连接 |
| `get_max_event_id_in_fail` | `util_sqlite.py` | 查询失败记录最大 `event_id` |
| `load_config` | `util_config.py` | 读取并解析 `config.json` |
| `load_records` | `util_sqlite.py` | 加载全部错误记录 |
| `query_error_type_counts` | `util_sqlite.py` | 聚合错误类型计数 |
| `query_records` | `util_sqlite.py` | 分页查询错误记录 |

## `__all__`

```python
__all__ = [
    "WebConfigModel",
    "append_records",
    "cal_interval",
    "clear_records",
    "connect_db",
    "get_max_event_id_in_fail",
    "load_config",
    "load_records",
    "query_error_type_counts",
    "query_records",
]
```

## 使用示例

```python
from celestialflow_web.runtime import WebConfigModel, cal_interval, load_config

config = WebConfigModel.model_validate(load_config("src/celestialflow_web/config.json"))
interval = cal_interval(config.global_.refreshInterval)
print(interval)
```

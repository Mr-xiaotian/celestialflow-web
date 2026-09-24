# src/celestialflow_web/runtime/__init__.py

> 📅 Last Updated: 2026/09/24

## Role

`celestialflow_web.runtime` consolidates the utility functions, data models, and SQLite access functions that the Web service depends on at runtime, exposing a unified export for `server/` and `routes/` to call.

## Public Exports

| Symbol | Source | Description |
|------|------|------|
| `WebConfigModel` | `util_models.py` | Frontend grouped configuration model |
| `append_records` | `util_sqlite.py` | Append error records |
| `cal_interval` | `util_cal.py` | Normalize a millisecond refresh interval to seconds |
| `clear_records` | `util_sqlite.py` | Clear error records |
| `connect_db` | `util_sqlite.py` | Open a SQLite connection |
| `get_max_event_id_in_fail` | `util_sqlite.py` | Query the maximum `event_id` among failed records |
| `load_config` | `util_config.py` | Read and parse `config.json` |
| `load_records` | `util_sqlite.py` | Load all error records |
| `query_error_type_counts` | `util_sqlite.py` | Aggregate error type counts |
| `query_records` | `util_sqlite.py` | Paginated query of error records |

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

## Usage Example

```python
from celestialflow_web.runtime import WebConfigModel, cal_interval, load_config

config = WebConfigModel.model_validate(load_config("src/celestialflow_web/config.json"))
interval = cal_interval(config.global_.refreshInterval)
print(interval)
```

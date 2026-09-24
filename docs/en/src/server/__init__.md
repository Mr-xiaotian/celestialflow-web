# src/celestialflow_web/server/__init__.py

> 📅 Last Updated: 2026/09/24

## Role

`celestialflow_web.server` is the Web service entry subpackage. It currently only exports `TaskWebServer`, so that external code can import it through a stable path.

## Public Exports

| Symbol | Source | Description |
|------|------|------|
| `TaskWebServer` | `core_server.py` | The main Web service class, encapsulating the FastAPI application, state cache, and route registration |

## `__all__`

```python
__all__ = [
    "TaskWebServer",
]
```

## Usage Example

```python
from celestialflow_web.server import TaskWebServer

server = TaskWebServer(host="127.0.0.1", port=5005, log_level="info")
server.start_server()
```

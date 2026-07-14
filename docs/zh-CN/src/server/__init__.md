# server 包入口

> 📅 最后更新日期: 2026/07/14

## 作用

`celestialflow_web.server` 是 Web 服务入口子包，目前只负责导出 `TaskWebServer`，供外部通过稳定路径导入。

## 公开导出

| 符号 | 来源 | 说明 |
|------|------|------|
| `TaskWebServer` | `core_server.py` | Web 服务主类，封装 FastAPI 应用、状态缓存与路由注册 |

## `__all__`

```python
__all__ = [
    "TaskWebServer",
]
```

## 使用示例

```python
from celestialflow_web.server import TaskWebServer

server = TaskWebServer(host="127.0.0.1", port=5005, log_level="info")
server.start_server()
```

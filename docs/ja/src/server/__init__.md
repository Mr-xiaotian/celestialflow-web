# src/celestialflow_web/server/__init__.py

> 📅 最終更新日: 2026/09/24

## 役割

`celestialflow_web.server` は Web サービス入口のサブパッケージで、現在は `TaskWebServer` をエクスポートすることのみを担当し、外部が安定したパスを通じてインポートできるようにします。

## 公開エクスポート

| シンボル | 出所 | 説明 |
|------|------|------|
| `TaskWebServer` | `core_server.py` | Web サービスメインクラス。FastAPI アプリ、状態キャッシュ、ルート登録をカプセル化 |

## `__all__`

```python
__all__ = [
    "TaskWebServer",
]
```

## 使用例

```python
from celestialflow_web.server import TaskWebServer

server = TaskWebServer(host="127.0.0.1", port=5005, log_level="info")
server.start_server()
```

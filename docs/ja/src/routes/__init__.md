# src/celestialflow_web/routes/__init__.py

> 📅 最終更新日: 2026/09/24

## 役割

`__init__.py`（すなわち `celestialflow_web.routes` パッケージ入口）は、Web API ルーティングを組み立てる出発点です。`APIRouter` を作成し、**Pull**（データ取得）と **Push**（データプッシュ）の2つのサブルートモジュールを登録するとともに、ルートパスのページ入口を登録します。

現在のディレクトリ構造では、取得とプッシュの実装ファイルはそれぞれ次の場所にあります：

| ファイル | 役割 |
|------|------|
| `core_pull.py` | すべての GET 取得エンドポイントを登録 |
| `core_push.py` | すべての POST プッシュエンドポイントを登録 |

## コア関数

### `create_router(server: TaskWebServer) -> APIRouter`

組み立て済みの `APIRouter` インスタンスを作成して返し、FastAPI アプリがマウントできるようにします。

| パラメータ | 型 | 説明 |
|------|------|------|
| `server` | `TaskWebServer` | タスク Web サーバーインスタンス。ルートはこの参照を通じてデータストアや設定などの共有状態にアクセスします |

**登録されるルート：**

| パス | メソッド | 説明 |
|------|------|------|
| `/` | `GET` | ページ入口。`templates/index.html` を返します |
| `/api/pull_*` | `GET` | Pull ルートモジュールが登録するすべての取得エンドポイント |
| `/api/push_*` | `POST` | Push ルートモジュールが登録するすべてのプッシュエンドポイント |

**登録順序：**

```
┌──────────────────────────────────────┐
│  APIRouter                           │
│                                      │
│  1. GET  /          (index.html)     │
│  2. GET  /api/pull_*                 │
│  3. POST /api/push_*                 │
└──────────────────────────────────────┘
```

すべてのルートは同じ `TaskWebServer` インスタンスを共有するため、Push ルートがデータを更新すると Pull ルートが最新状態を返せるようになります。

## 使用例

```python
from celestialflow_web.routes import create_router
from celestialflow_web.server.core_server import TaskWebServer

server = TaskWebServer(...)
router = create_router(server)

# FastAPI アプリにマウント
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
```

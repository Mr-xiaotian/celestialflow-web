# src/celestialflow_web/routes/__init__.py

> 📅 Last Updated: 2026/09/24

## Role

`__init__.py` (that is, the entry point of the `celestialflow_web.routes` package) is the assembly starting point for all Web API routes. It creates an `APIRouter` and registers the two sub-route modules **Pull** (data pulling) and **Push** (data pushing) into it, while also registering the page entry for the root path.

According to the current directory structure, the pull and push implementation files are located respectively at:

| File | Role |
|------|------|
| `core_pull.py` | Registers all GET pull endpoints |
| `core_push.py` | Registers all POST push endpoints |

## Core Functions

### `create_router(server: TaskWebServer) -> APIRouter`

Creates and returns a fully assembled `APIRouter` instance for the FastAPI application to mount.

| Parameter | Type | Description |
|------|------|------|
| `server` | `TaskWebServer` | The task Web server instance; routes access shared state such as the data store and configuration through this reference |

**Registered routes:**

| Path | Method | Description |
|------|------|------|
| `/` | `GET` | Page entry, returns `templates/index.html` |
| `/api/pull_*` | `GET` | All pull endpoints registered by the Pull route module |
| `/api/push_*` | `POST` | All push endpoints registered by the Push route module |

**Registration order:**

```
┌──────────────────────────────────────┐
│  APIRouter                           │
│                                      │
│  1. GET  /          (index.html)     │
│  2. GET  /api/pull_*                 │
│  3. POST /api/push_*                 │
└──────────────────────────────────────┘
```

All routes share the same `TaskWebServer` instance, so once a Push route updates the data, the Pull routes can return the latest state.

## Usage Example

```python
from celestialflow_web.routes import create_router
from celestialflow_web.server.core_server import TaskWebServer

server = TaskWebServer(...)
router = create_router(server)

# Mount to the FastAPI application
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
```

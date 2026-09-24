# src/celestialflow_web/server/core_server.py

> 📅 Last Updated: 2026/09/24

The TaskWeb module provides a lightweight Web server based on FastAPI, used to monitor and manage the running of task graphs in real time. It acts as a relay station between `TaskReporter` (backend) and the Web UI (frontend).

## How to Start

### Starting from the Command Line

```bash
# Listen on 0.0.0.0:5000 by default
celestialflow-web

# Specify the port
celestialflow-web --port 5005

# Specify the host and port
celestialflow-web --host 127.0.0.1 --port 5005

# Specify the log level
celestialflow-web --log-level debug
```

### Command-Line Arguments

| Argument | Default | Description |
|------|--------|------|
| `--host` | `0.0.0.0` | Listen address |
| `--port` | `5000` | Listen port |
| `--log-level` | `info` | Log level (critical/error/warning/info/debug/trace) |

### Starting in Code

```python
from celestialflow_web import TaskWebServer

server = TaskWebServer(host="127.0.0.1", port=5005, log_level="info")
server.start_server()
```

### CLI Entry Point

`core_server.py` also provides command-line entry functions:

- `parse_args()` — parses the `--host`, `--port`, and `--log-level` arguments; `--log-level` is restricted to `critical` / `error` / `warning` / `info` / `debug` / `trace`.
- `main_entry()` — constructs a `TaskWebServer` from the parsed arguments and calls `start_server()`.

The command-line tool `celestialflow-web` is registered from `main_entry`.

## Feature Interface

Visit `http://localhost:5000` (or the specified port) to see the Web UI.

### Main Panels

| Panel | Function |
|------|------|
| **Dashboard** | Real-time status overview of the task graph (structure visualization (Mermaid graph), node count, succeeded/failed/backlog task counts, line charts) |
| **Errors** | Real-time error log list |
| **Task Injection** | Dynamically inject tasks through the Web interface |

### Theme Support

- Supports day/night theme switching
- Theme settings are persisted to the backend `config.json`

## API Endpoints (RESTful)

TaskWeb provides a series of RESTful APIs for `TaskReporter` to call and for the frontend to use. All endpoints are prefixed with `/api/`, pull endpoints use the `pull_` naming, and push endpoints use the `push_` naming.

### Pull Endpoints (GET /api/pull_*)

The pull endpoints that support the `known_rev` mechanism (`pull_status`, `pull_graph_meta`, `pull_errors`, `pull_error_type_counts`) return `data: null` when the server-side data version is unchanged, to save bandwidth; `pull_config`, `pull_injection`, and `pull_server_state` do not use the `known_rev` mechanism and return the full data every time (among them, `pull_server_state` calls `sync_graph_context`, which has side effects).

| Endpoint | Return structure (data field) | Description |
|------|--------------------|------|
| `pull_config` | `dict` | Get global configuration such as theme, language, and refresh rate |
| `pull_graph_meta` | `dict[str, Any]` | Get graph meta information (graph structure + node construction-time meta information + graph analysis result) |
| `pull_status` | `dict[str, dict[str, Any]]` | Get the real-time running metrics of each node and a unified timestamp |
| `pull_errors` | `list[dict]` | Pull error logs in pages, supporting node/keyword filtering and sorting |
| `pull_error_type_counts` | `list[dict[str, Any]]` | Statistics aggregated by error type, supporting node filtering |
| `pull_injection` | `{"tasks": dict[str, list[Any]], "terminations": list[str]}` | For TaskGraph to pull the pending injection task queue and terminations (tasks grouped by node name, cleared after reading) |
| `pull_server_state` | `dict[str, Any]` | Get the server-side state required for Reporter synchronization (interval/is_current_graph/has_graph_meta/max_event_id_in_fail) |

### Push Endpoints (POST /api/push_*)

Mainly called by `TaskReporter`, used to report backend running status.

| Endpoint | Data model | Description |
|------|---------|------|
| `push_config` | `WebConfigModel` | Called by the frontend, saves user settings |
| `push_status` | `StatusModel` | Reports a node status snapshot + current timestamp |
| `push_graph_meta` | `GraphMetaModel` | Reports graph meta information (graph structure + node construction-time meta information + analysis result); returns 409 when `graph_id` does not match |
| `push_errors` | `ErrorsModel` | Directly pushes error content and writes it to SQLite |
| `push_injection_tasks` | `TaskInjectionModel` | Frontend submits a task injection request |
| `push_injection_terminations` | `TerminationInjectionModel` | Frontend submits a termination injection request |

## Data Models (Pydantic)

> For the complete model definitions, see `util_models.md`; only the core fields are listed here.

### GraphMetaModel

```python
class GraphMetaModel(BaseModel):
    graph_id: str = ""  # Graph instance identifier, used for graph context validation on the Reporter side
    nodes: list[str] = Field(default_factory=list)  # List of node names
    edges: dict[str, list[str]] = Field(
        default_factory=dict
    )  # Edge dictionary, keyed by source node name with a list of target node names as values
    source_nodes: list[str] = Field(default_factory=list)  # List of source nodes
    node_meta: dict[str, dict[str, Any]] = Field(
        default_factory=dict
    )  # Node construction-time meta information, keyed by node name
    analysis: dict[str, Any] | None = None  # Graph analysis result
```

### StatusModel

```python
class StatusModel(BaseModel):
    graph_id: str = ""  # Graph instance identifier
    timestamp: float  # Unified sampling timestamp
    status: dict[str, dict[str, Any]]  # Keys are node names, values are node status dictionaries
```

### ErrorsModel

```python
class ErrorsModel(BaseModel):
    graph_id: str = ""  # Graph instance identifier
    errors: list[dict[str, Any]]  # List of error records, written directly to the SQLite database
```

### TaskInjectionModel

```python
class TaskInjectionModel(RootModel[dict[str, list[Any]]]):
    """Task injection request model, in the format {node_name: [tasklist]}."""
```

> The request body is directly a mapping from node names to task lists. Example:
> `{"StageA": [task1, task2], "StageB": [task3]}`

### TerminationInjectionModel

```python
class TerminationInjectionModel(RootModel[list[str]]):
    """Termination injection request model, in the format [node_name, ...]."""
```

> The request body is directly a list of node names. Example:
> `["StageA", "StageB"]`

### WebConfigModel

The configuration uses a nested grouped structure.

```python
class GlobalConfigModel(BaseModel):
    theme: str
    autoRefreshEnabled: bool = True
    refreshInterval: int
    language: str = "zh-CN"


class DashboardConfigModel(BaseModel):
    left: list[str]
    middle: list[str]
    right: list[str]


class DashboardPageConfigModel(BaseModel):
    historyLimit: int
    showStructureEdgeDelta: bool = False
    useTotalPendingInStatus: bool = False
    layout: DashboardConfigModel


class ErrorsPageConfigModel(BaseModel):
    pageSize: int = 10
    sortOrder: str = "newest"
    jumpToInjectionAfterRetry: bool = True
    columns: list[str] = Field(
        default_factory=lambda: [
            "index",
            "event_id",
            "message",
            "stage",
            "task",
            "time",
            "retry",
        ]
    )


class InjectionPageConfigModel(BaseModel):
    showInjectableOnly: bool = True


class WebConfigModel(BaseModel):
    global_: GlobalConfigModel = Field(alias="global")
    dashboard: DashboardPageConfigModel
    errors: ErrorsPageConfigModel
    injection: InjectionPageConfigModel = Field(
        default_factory=InjectionPageConfigModel
    )
```

## Configuration Management

The configuration of the Web service is persisted in the package at `src/celestialflow_web/config.json`.

- `load_config()` — reads and validates through `WebConfigModel` at startup; if `config.json` does not exist, throws `ConfigurationError` directly and does not start with hard-coded defaults.
- `save_config(config, config_path)` — saves the configuration to a JSON file, thread-safe (guaranteed by the `config_lock` in the upper-level `push_config` route)
- `cal_interval(refresh_interval)` — converts a millisecond refresh interval to seconds, clamped to `[1.0, 60.0]`
- **Synchronization mechanism**: When the frontend updates `refreshInterval`, the backend `report_interval` is automatically synchronized, thereby affecting the push frequency of `TaskReporter`.

## Integration with TaskGraph

### Enabling in TaskGraph

```python
from celestialflow import TaskGraph, TaskStage


def process(x: int) -> int:
    return x * 2


stage_a = TaskStage("StageA", process, execution_mode="thread")
graph = TaskGraph(name="DemoGraph")
graph.set_stages(stages=[stage_a])
graph.set_reporter(True, host="127.0.0.1", port=5005)
init_tasks = {stage_a.get_name(): [1, 2, 3]}
graph.start_graph(init_tasks)
```

### Data Flow

```
TaskGraph                         TaskWeb                    Browser
    |                                |                          |
    |--- push_graph_meta ---------->|--- Dashboard ----------->|
    |--- push_status --------------->|                          |
    |                                |                          |
    |--- push_errors --------------->|---- Errors ------------->|
    |                                |                          |
    |<-- pull_injection -------------|<--- Inject Tasks --------|
    |<-- pull_server_state ----------|<--- Reporter Sync -------|
    |                                |                          |
```

## Error Handling

### SQLite Persistence

Error records are written directly to the SQLite database via `append_records`, supporting efficient queries and pagination. The SQLite database file is created with manually managed file descriptors using `tempfile.mkstemp` (to avoid the conflict between automatic deletion and file reopening of `NamedTemporaryFile` on Windows).

### Task Injection Concurrency Safety

The `injection_tasks` dictionary and the `injection_terminations` set are protected by `task_injection_lock`; writes by `push_injection_tasks` / `push_injection_terminations` and reads (including clearing) by `pull_injection` are all performed inside the lock, avoiding races. Task injection uses **overwrite** semantics: new tasks with the same node name overwrite the old task list; termination injection uses **set** semantics: duplicate node names are deduplicated.

## Notes

1. **Port conflict**: Make sure the specified port is not occupied.
2. **Firewall**: For remote access, configure firewall rules.
3. **HTTPS**: For production, it is recommended to use a reverse proxy (such as Nginx) to add HTTPS.
4. **Authentication**: The current version has no built-in authentication; for production, it is recommended to add an authentication layer.

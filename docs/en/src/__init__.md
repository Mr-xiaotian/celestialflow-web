# src/celestialflow_web/__init__.py

> 📅 Last Updated: 2026/09/24

The `celestialflow_web` package provides a standalone Web monitoring interface for CelestialFlow. Built on FastAPI and native TypeScript, it supports task status visualization, error tracking, task injection, and frontend configuration persistence.

## Module Overview

The package root currently exports only one public object:

| Exported Symbol | Source | Description |
|---------|------|------|
| `TaskWebServer` | `celestialflow_web.server.core_server` | FastAPI Web service entry class |

The runtime structure has been split into three backend subpackages:

| Subpackage | Role |
|------|------|
| `server/` | Service entry and application lifecycle management |
| `runtime/` | Configuration, models, SQLite, and parameter normalization utilities |
| `routes/` | Pull / Push route registration |

## File Description

### Core Backend Components

1. **server/core_server.py** (`TaskWebServer`)
   - **Role**: The Web core server, managing data caching, version control (known_rev), and API routes.
   - **Key features**: State aggregation, configuration persistence, paginated error queries, and task injection relay.

2. **routes/**
   - **Role**: Assembles the home page, the Pull API, and the Push API.

3. **runtime/**
   - **Role**: Provides `config.json` read/write, Pydantic models, SQLite operations, and parameter normalization utilities.

### Core Frontend Components

The frontend TypeScript source files are located in `src/celestialflow_web/static/ts/`, and after being compiled to JS they are loaded by `templates/index.html`:

1. **main.ts** — Global entry point and polling coordination
2. **utils.ts** — Common utility functions
3. **i18n.ts** — Internationalization support
4. **web_config.ts** — Configuration management logic + card DOM injection (calls `ensureAllCards()` at module load)
5. **loaders.ts** — Data layer: status/graph meta fetching, version guards, and local derivation
6. **util_estimators.ts** — Graph-level derived metric estimation (global pending workload, estimated remaining time)
7. **types.d.ts** — Frontend/backend contract type declarations (types only, produces no JS)
8. **dashboard_statuses.ts** — Renders dynamic node cards, showing real-time performance metrics and progress bars for each stage
9. **dashboard_structure.ts** — Renders the task graph topology based on Mermaid.js, supporting dynamic node coloring
10. **dashboard_history.ts** — Maintains multi-metric historical series and renders progress line charts using Chart.js
11. **dashboard_summary.ts** — Rendering and updating of the global statistics dashboard
12. **dashboard_analysis.ts** — Display of topology analysis information
13. **dashboard_error_types.ts** — Error type distribution doughnut chart and legend
14. **errors.ts** — Paginated display and in-depth filtering of error logs
15. **injection.ts** — Manages the manual task injection UI, supporting batch injection for multiple nodes
16. **layout_editor.ts** — Card layout editor (depends on web_config's CARD_TEMPLATES/PANEL_SELECTOR_MAP)

## Architecture Highlights

### Client-side History Accumulation
To significantly reduce the frequency of frontend-backend communication, historical trend data is no longer pushed in full by the backend. Instead, the frontend accumulates and maintains it in browser memory based on consecutive status snapshots (Status Snapshot).

### Incremental Pull Mechanism
All pull endpoints (`pull_*`) support the `known_rev` mechanism. The actual payload is transferred only when the backend data version changes; otherwise, only the version number is returned, greatly saving polling bandwidth.

### Configuration Persistence
At startup, the backend reads the `config.json` bundled in the package and validates it through `WebConfigModel`; after the frontend changes settings, the backend writes the latest configuration back to the same file.

## Usage Patterns

### Starting the Server
```bash
# Run the command-line tool directly
celestialflow-web --port 5000
```

### Task Injection Example
```python
import requests

# Overwrite the pending injection tasks for a specified node (format: {node_name: [task_list]})
requests.post(
    "http://localhost:5000/api/push_injection_tasks",
    json={"Stage_A": [{"id": 1, "data": "payload"}]},
)
```

## Usage Examples

### Basic Example of Creating and Starting TaskWebServer

```python
from celestialflow_web import TaskWebServer

# Create a server instance
server = TaskWebServer(
    host="127.0.0.1",  # Listen address
    port=5000,  # Listen port
    log_level="info",  # Log level
)

# Start the server (a blocking call that keeps running)
server.start_server()
```

After starting, visit `http://127.0.0.1:5000` in a browser to see the Web UI monitoring dashboard.

### Example of Working with the CelestialFlow Runtime

```python
from celestialflow import TaskGraph, TaskStage
from celestialflow.persistence import LogInlet
from celestialflow.observability import TaskReporter
import asyncio

from celestialflow_web import TaskWebServer


async def main():
    # 1. Start the Web server first (running in a background thread)
    server = TaskWebServer(host="127.0.0.1", port=5000, log_level="info")
    # In an actual production environment, server.start_server() blocks;
    # this is only illustrating how the reporter works together with the server

    # 2. Create a task graph
    def process(x: int) -> int:
        return x * 2

    graph = TaskGraph(name="DemoGraph", schedule_mode="eager")
    stage = TaskStage("Processor", process, execution_mode="thread")
    graph.set_stages([stage])

    # 3. Create and start TaskReporter
    log_inlet = LogInlet()
    reporter = TaskReporter(
        host="127.0.0.1",
        port=5000,
        task_graph=graph,
        log_inlet=log_inlet,
    )
    reporter.start()

    # 4. Execute tasks
    graph.start_graph({stage.get_name(): range(50)})

    # 5. Stop the reporter
    reporter.stop()


asyncio.run(main())
```

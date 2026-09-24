# src/celestialflow_web/runtime/util_models.py

> 📅 Last Updated: 2026/09/24

## Role

The `celestialflow_web.runtime.util_models` module defines all the Pydantic data models used by the Web module, for data validation, serialization, and API request/response type constraints.

## Model List

### GraphMetaModel

The graph meta information data model, which jointly carries the graph structure (nodes / edges / source nodes), node construction-time meta information (`node_meta`), and the graph analysis result (`analysis`).

| Field | Type | Default | Description |
|------|------|--------|------|
| `graph_id` | `str` | `""` | Graph instance identifier, used for graph context validation on the Reporter side |
| `nodes` | `list[str]` | `[]` | List of node names |
| `edges` | `dict[str, list[str]]` | `{}` | Edge dictionary, keyed by source node name with a list of target node names as values |
| `source_nodes` | `list[str]` | `[]` | List of source node (entry node) names |
| `node_meta` | `dict[str, dict[str, Any]]` | `{}` | Node construction-time meta information dictionary, keyed by node name |
| `analysis` | `dict[str, Any] \| None` | `None` | Graph analysis result dictionary |

### StatusModel

The node status data model, representing the running status of each node.

| Field | Type | Description |
|------|------|------|
| `graph_id` | `str` | Graph instance identifier, defaults to `""` |
| `timestamp` | `float` | Timestamp of the status data (Unix) |
| `status` | `dict[str, dict[str, Any]]` | Mapping from node name to status dictionary |

### ErrorsModel

The error content data model, containing the full list of error records.

| Field | Type | Description |
|------|------|------|
| `graph_id` | `str` | Graph instance identifier, defaults to `""` |
| `errors` | `list[dict[str, Any]]` | List of error records, each item being an error dictionary; written directly to the SQLite database |

### TaskInjectionModel

The task injection request model, used to dynamically insert new tasks into a running task graph.

> This model inherits from `RootModel[dict[str, list[Any]]]`; the request body is directly a dictionary in the `{node_name: [task_list]}` format and no longer contains separate fields such as `node`/`task_datas`/`timestamp`.

| Root Value Type | Description |
|----------|------|
| `dict[str, list[Any]]` | Keys are node names, and values are the lists of task data to be injected for that node |

**Request body example:**

```json
{
  "StageA": [{"id": 1, "value": 42}, {"id": 2, "value": 99}],
  "StageB": [{"id": 3, "value": 55}]
}
```

### TerminationInjectionModel

The termination injection request model, used to inject target termination nodes into a running task graph.

> This model inherits from `RootModel[list[str]]`; the request body is directly a list of node name strings and no longer contains other wrapper fields.

| Root Value Type | Description |
|----------|------|
| `list[str]` | List of node names to be injected with terminations |

**Request body example:**

```json
[
  "StageA",
  "StageB"
]
```

### DashboardConfigModel

The dashboard layout configuration model, defining the frontend panel card layout.

| Field | Type | Description |
|------|------|------|
| `left` | `list[str]` | List of card types to display in the left panel |
| `middle` | `list[str]` | List of card types to display in the middle panel |
| `right` | `list[str]` | List of card types to display in the right panel |

### GlobalConfigModel

The global shared configuration model (nested under `WebConfigModel.global_`).

| Field | Type | Default | Description |
|------|------|--------|------|
| `theme` | `str` | — | UI theme (e.g. `"light"`, `"dark"`) |
| `autoRefreshEnabled` | `bool` | `True` | Whether automatic refresh is enabled |
| `refreshInterval` | `int` | — | Page data refresh interval (ms) |
| `language` | `str` | `"zh-CN"` | Interface language |

### DashboardPageConfigModel

The dashboard page configuration model (nested under `WebConfigModel.dashboard`).

| Field | Type | Default | Description |
|------|------|--------|------|
| `historyLimit` | `int` | — | Maximum number of history records |
| `showStructureEdgeDelta` | `bool` | `False` | Whether to show structure graph edge deltas |
| `useTotalPendingInStatus` | `bool` | `False` | Whether node pending parameters use the global estimate |
| `layout` | `DashboardConfigModel` | — | Three-column card layout definition for the dashboard |

### ErrorsPageConfigModel

The errors page configuration model (nested under `WebConfigModel.errors`).

| Field | Type | Default | Description |
|------|------|--------|------|
| `pageSize` | `int` | `10` | Number of items per page on the errors page |
| `sortOrder` | `str` | `"newest"` | Default sort order (`"newest"` / `"oldest"`) |
| `jumpToInjectionAfterRetry` | `bool` | `True` | Whether to jump to the injection page after a task retry |
| `columns` | `list[str]` | `["index", "event_id", "message", "stage", "task", "time", "retry"]` | Column definition and display order of the errors page table (controlled by the column editor in the settings panel) |

### InjectionPageConfigModel

The injection page configuration model (nested under `WebConfigModel.injection`).

| Field | Type | Default | Description |
|------|------|--------|------|
| `showInjectableOnly` | `bool` | `True` | Whether to show only injectable nodes |

### WebConfigModel

The Web UI global configuration model (nested grouped structure).

| Field | Type | Default | Description |
|------|------|--------|------|
| `global_` | `GlobalConfigModel` | — | Global shared configuration (JSON alias is `"global"`) |
| `dashboard` | `DashboardPageConfigModel` | — | Dashboard page configuration |
| `errors` | `ErrorsPageConfigModel` | — | Errors page configuration |
| `injection` | `InjectionPageConfigModel` | `InjectionPageConfigModel()` | Injection page configuration |

The configuration uses a nested grouped structure: `theme`, `refreshInterval`, `language`, etc. live in `GlobalConfigModel` (the JSON key is `"global"`); `historyLimit`, `showStructureEdgeDelta`, etc. live in `DashboardPageConfigModel`; `pageSize`, `sortOrder`, etc. live in `ErrorsPageConfigModel`.

## Usage Examples

### Data Validation and Serialization

```python
from celestialflow_web.runtime.util_models import (
    WebConfigModel,
    GlobalConfigModel,
    DashboardPageConfigModel,
    DashboardConfigModel,
    ErrorsPageConfigModel,
    InjectionPageConfigModel,
    TaskInjectionModel,
)

# --- WebConfigModel usage (nested structure) ---
# Because `global` is a Python reserved word, WebConfigModel can only be constructed via model_validate()
# or Pydantic's alias path; directly using WebConfigModel(global_=...) will fail because
# model_config does not enable populate_by_name (only during the __init__ stage).
config = WebConfigModel.model_validate(
    {
        "global": GlobalConfigModel(
            theme="dark",
            autoRefreshEnabled=True,
            refreshInterval=5000,
            language="zh-CN",
        ).model_dump(),
        "dashboard": DashboardPageConfigModel(
            historyLimit=20,
            showStructureEdgeDelta=False,
            useTotalPendingInStatus=False,
            layout=DashboardConfigModel(
                left=["mermaid"],
                middle=["status"],
                right=["progress"],
            ),
        ).model_dump(),
        "errors": ErrorsPageConfigModel(
            pageSize=10,
            sortOrder="newest",
            jumpToInjectionAfterRetry=True,
            columns=["index", "event_id", "message", "stage", "task", "time", "retry"],
        ).model_dump(),
        "injection": InjectionPageConfigModel(
            showInjectableOnly=True,
        ).model_dump(),
    }
)
print(f"Theme: {config.global_.theme}")
print(f"Dashboard layout: {config.dashboard.layout.model_dump()}")

# Serialize to a dictionary (by_alias=True turns global_ into "global")
config_dict = config.model_dump(by_alias=True)

# Create from a dictionary
restored = WebConfigModel.model_validate(config_dict)

# --- TaskInjectionModel usage ---
injection = TaskInjectionModel(
    StageA=[{"id": 1, "value": 42}, {"id": 2, "value": 99}],
    StageB=[{"id": 3, "value": 55}],
)
print(f"Number of injected nodes: {len(injection.root)}")
for node_name, tasks in injection.root.items():
    print(f"  {node_name}: {len(tasks)} tasks")
```

> Note: `TaskInjectionModel` is `RootModel[dict[str, list[Any]]]`; the request body is directly a mapping dictionary from node names to task lists, and no longer wraps fields such as `node`/`task_datas`.

### Error Data Handling

```python
from celestialflow_web.runtime.util_models import ErrorsModel

# Error content
content = ErrorsModel(
    graph_id="graph-001",
    errors=[
        {"error_type": "ValueError", "error_message": "Invalid input"},
        {"error_type": "TimeoutError", "error_message": "Connection lost"},
    ],
)
print(f"Number of errors: {len(content.errors)}")
```

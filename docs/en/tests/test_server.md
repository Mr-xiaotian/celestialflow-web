# tests/test_server.py

> 📅 Last Updated: 2026/09/24

## Role

Verifies the RESTful API provided by `celestialflow_web.server.core_server`, ensuring that the Web dashboard can correctly display graph status, pull configuration, inject tasks, and browse error logs, while also verifying the isolation of snapshot data.

## Core Test Target

- `TaskWebServer`: The monitoring and interaction server implemented based on FastAPI.

## Key Test Scenarios

### Snapshot Isolation
- `test_store_snapshot_methods_return_isolated_copies`: Verifies that the server's snapshot methods return deep copies, so modifying the return value does not affect the internal store.

### Static Asset Rendering
- `test_index_page`: Verifies that the home page `/` correctly returns an HTML page containing the `dashboard` container.
- `test_entry_module_reaches_every_built_artifact`: Verifies that the home page references only one ESM entry `main.js`, and that this entry can reach all build artifacts along the import graph, avoiding dead modules that no one imports.
- `test_card_injecting_module_evaluates_before_dashboards`: Verifies that `web_config` precedes the `dashboard_*` modules in module evaluation order (card DOM injection happens before the `getElementById` that depends on it).

### Configuration Pulling
- `test_config_api`: Verifies that the runtime parameters required by the frontend (refresh rate, theme, etc.) can be fetched correctly.

### Server-side State
- `test_server_state_api`: Verifies the server-side synchronization state pulled by the reporter, including the polling interval, the current graph identifier, the graph meta readiness state (`has_graph_meta`), and the failed event watermark.

### Status Synchronization (Rev Mechanism)
- `test_status_push_pull`:
  - Verifies that `push_status` can successfully save a snapshot.
  - Verifies that `pull_status` supports incremental updates: when `known_rev` matches the server's current version, it returns empty data to save bandwidth.

### Graph Meta Information Synchronization
- `test_graph_meta_push_pull`: Verifies that `push_graph_meta` / `pull_graph_meta` can fully preserve the graph structure, node construction-time meta information, and analysis result, and do not re-deliver when `known_rev` hits.

### Task Injection
- `test_task_injection`: Verifies that tasks injected through the POST endpoint can be correctly staged and consumed by the scheduler through the GET endpoint, and are cleared after consumption.
- `test_task_injection_overwrites_tasklist_per_node`: Verifies that a new push updates the task list node by node rather than appending.
- `test_task_injection_requires_tasklist_mapping`: Verifies that an illegal payload (non-list value) returns 422.
- `test_termination_injection_requires_string_array`: Verifies that the termination injection endpoint requires the request body to be an array of strings, otherwise returns 422.

### Error Type Aggregation
- `test_get_error_type_counts_returns_grouped_stats`: Verifies all-node error type aggregate statistics, returning counts grouped by `error_type`.
- `test_get_error_type_counts_supports_node_filter`: Verifies error type aggregation filtered by node (`stage`).
- `test_pull_error_type_counts`: Verifies that the `/api/pull_error_type_counts` HTTP endpoint supports all-node aggregation, single-node filtering, and returns `data: null` on a `known_rev` cache hit.

### Error Management
- `test_errors_pagination`:
  - Verifies batch pushing of error records.
  - Verifies the pagination logic: checks `total_pages`, `total`, and the number of items on the current page.
  - Verifies the node (`node`) filtering logic.
  - Verifies the keyword (`keyword`) filtering logic.
  - Verifies sorting (`sort_order`): supports both `newest` and `oldest`.
- `test_push_errors_appends_for_same_graph`: Under the same `graph_id`, multiple error pushes only append and do not overwrite.
- `test_push_errors_duplicate_append_is_idempotent`: Repeatedly pushing the same `event_id` does not produce duplicate rows.
- `test_newer_graph_replaces_previous_graph_context`: When a new `graph_id` arrives, the old error cache is cleared.
- `test_stale_graph_pushes_are_ignored`: After switching to a new graph, late pushes from the old graph should not pollute the current cache.
- `test_push_errors_meta_route_removed`: `/api/push_errors_meta` has been removed, and accessing it returns 404.

## Test Coverage Matrix

| Test Function | Coverage Target |
|----------|----------|
| `test_store_snapshot_methods_return_isolated_copies` | Snapshots return deep copies |
| `test_index_page` | Home page HTML rendering |
| `test_entry_module_reaches_every_built_artifact` | ESM entry can reach all build artifacts |
| `test_card_injecting_module_evaluates_before_dashboards` | `web_config` is evaluated before the dashboard modules |
| `test_config_api` | `/api/pull_config` configuration pulling |
| `test_server_state_api` | `/api/pull_server_state` server-side state |
| `test_push_errors_meta_route_removed` | The old endpoint has been removed |
| `test_status_push_pull` | Status push and incremental pull |
| `test_graph_meta_push_pull` | Graph meta information push and incremental pull |
| `test_task_injection` | Task and termination injection, consumption, and clearing |
| `test_task_injection_overwrites_tasklist_per_node` | Per-node overwrite of the task list |
| `test_task_injection_requires_tasklist_mapping` | Task injection parameter validation |
| `test_termination_injection_requires_string_array` | Termination injection parameter validation |
| `test_errors_pagination` | Error pagination, filtering, and sorting |
| `test_push_errors_appends_for_same_graph` | Error appending for the same graph |
| `test_push_errors_duplicate_append_is_idempotent` | Idempotent duplicate pushes |
| `test_newer_graph_replaces_previous_graph_context` | New graph context switching |
| `test_stale_graph_pushes_are_ignored` | Ignoring stale pushes |
| `test_get_error_type_counts_returns_grouped_stats` | All-node error type aggregation |
| `test_get_error_type_counts_supports_node_filter` | Error type aggregation filtered by node |
| `test_pull_error_type_counts` | Error type aggregation API (cache hit) |

## Test Focus

- **Rev version control**: Ensures the efficiency of the frontend refresh logic, avoiding redundant data transfer.
- **Pagination accuracy**: Verifies the backend's offset calculation when handling error records.
- **Task consistency**: Ensures that injected tasks are correctly cleared after being pulled and consumed, preventing duplicate processing.
- **Snapshot isolation**: Ensures that data obtained by the frontend does not become inconsistent due to internal state mutations.
- **Parameter validation**: Verifies that the injection endpoints return 422 for illegal payloads, preventing downstream processing of erroneous data.
- **Error type aggregation**: Verifies that `/api/pull_error_type_counts` can aggregate statistics grouped by `error_type`, supports all-node and per-node filtering, and works with the Rev mechanism to achieve cache hits.
- **Utility method**: `get_error_type_counts` is a pure utility method at the server layer, and its return value can be used directly by the dashboard to display the error distribution.

## How to Run

```bash
# Run everything
uv run pytest tests/test_server.py -v

# Run only the status synchronization tests
uv run pytest tests/test_server.py -k "status" -v

# Run only the task injection tests
uv run pytest tests/test_server.py -k "injection" -v

# Run only the error management tests
uv run pytest tests/test_server.py -k "errors" -v

# Run only the configuration pulling tests
uv run pytest tests/test_server.py -k "config" -v

# Run only the error type aggregation tests
uv run pytest tests/test_server.py -k "error_type" -v
```

## Important Details

- Uses `FastAPI TestClient` for simulated requests and does not actually start a port listener.
- The snapshot isolation tests operate directly on the `web_server` fixture (provided by `conftest.py`), while other tests use the `client` fixture.
- The tests create a new server instance before each function runs.

## Notes

- The Web service is the visualization window of CelestialFlow.
- The related implementation is located in `src/celestialflow_web/server/core_server.py`.

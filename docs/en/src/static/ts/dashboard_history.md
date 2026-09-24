# src/celestialflow_web/static/ts/dashboard_history.ts

> 📅 Last Updated: 2026/09/24

Manages the maintenance of per-node multi-metric history data and the initialization and redrawing of the line chart. History data is accumulated entirely on the frontend through status snapshots, without relying on a dedicated backend API.

## Type Definitions

```typescript
/** Metric field keys that the history chart supports switching between */
type HistoryMetricKey =
  | "tasks_processed"
  | "tasks_succeeded"
  | "tasks_failed"
  | "tasks_duplicated"
  | "tasks_pending"
  | "total_tasks_pending"
  | "delta_tasks_processed"
  | "delta_tasks_succeeded"
  | "delta_tasks_failed"
  | "delta_tasks_duplicated";

/** A single node's history sample point at a given moment */
type NodeHistoryPoint = {
  timestamp: number;
  tasks_processed: number;
  tasks_succeeded: number;
  tasks_failed: number;
  tasks_duplicated: number;
  tasks_pending: number;
  total_tasks_pending: number;
};

  type NodeHistory = NodeHistoryPoint[];

type ThemeColors = {
  text: string;   // Axis and legend text color
  grid: string;   // Grid line color
  border: string; // Axis border color
};
```

## Global Variables

| Variable | Type | Description |
|------|------|------|
| `nodeHistories` | `Record<string, NodeHistory>` | History data series maintained locally for each node |
| `progressChart` | `ChartInstance \| null` | Chart.js line chart instance |
| `hiddenNodes` | `Set<string>` | Set of nodes manually hidden by the user in the legend (kept only for the page lifetime, **not persisted**) |
| `currentHistoryMetric` | `HistoryMetricKey` | Metric currently displayed by the chart, default `"tasks_processed"` |
| `metricDots` | `NodeListOf<HTMLLabelElement>` | All `.metric-dot` label elements, used to switch the displayed metric |

## Helper Functions

### `getColor(index: number): string`

Reads a predefined theme color from a CSS variable by index, used to distinguish the lines of different nodes. Cycles through 9 colors with modulo.

| Index | CSS variable | Description |
|-------|---------|------|
| 0 | `--cornflower-500` | Cornflower blue |
| 1 | `--jade-500` | Jade green |
| 2 | `--marigold-500` | Marigold yellow |
| 3 | `--crimson-500` | Crimson |
| 4 | `--violet-500` | Violet |
| 5 | `--rose-500` | Rose |
| 6 | `--jade-400` | Jade green (light) |
| 7 | `--sky-500` | Sky blue |
| 8 | `--amber-500` | Amber |

### `getHistoryMetricLabelKey(metric: HistoryMetricKey): string`

Maps a `HistoryMetricKey` to an i18n translation key.

| Input | Output |
|------|------|
| `tasks_processed` | `chart.metric.processed` |
| `tasks_succeeded` | `chart.metric.succeeded` |
| `tasks_failed` | `chart.metric.failed` |
| `tasks_duplicated` | `chart.metric.duplicated` |
| `tasks_pending` | `chart.metric.pending` |
| `total_tasks_pending` | `chart.metric.pendingGlobal` |
| `delta_tasks_processed` | `chart.metric.deltaProcessed` |
| `delta_tasks_succeeded` | `chart.metric.deltaSucceeded` |
| `delta_tasks_failed` | `chart.metric.deltaFailed` |
| `delta_tasks_duplicated` | `chart.metric.deltaDuplicated` |

### `updateHistoryMetricButtons(): void`

Iterates over `metricDots`, adds the `.active` class to the matching `<label>` based on `currentHistoryMetric`, and removes it from the rest.

### `updateChartAxisLabels(): void`

Updates the line chart's X/Y axis title text, mapping them respectively to "Time" in the current language and the corresponding metric name.

---

## Core Logic Functions

### `initHistoryChart(): void`

Initializes (or rebuilds) the Chart.js line chart instance.

- If an instance already exists, calls `destroy()` first to destroy it
- Calls `getChartThemeColors()` to read the current theme's text color, grid color, and axis color
- Configures the legend click event: toggles node show/hide and syncs it to the `hiddenNodes` Set
- **Disables animation** (`animation: false`) to improve real-time refresh performance
- Interaction mode is `index`, `intersect: false`

### `updateChartTheme(): void`

Updates the line chart's color scheme (text color, grid line color, axis color); called after a theme switch, without needing to rebuild the instance.

### `updateChartData(): void`

Based on `currentHistoryMetric`, calls `extractProgressData()` to write the corresponding metric data from `nodeHistories` into the line chart and refresh it. Also syncs `legendItem.hidden` to ensure the legend rendering matches `hiddenNodes`.

### `appendStatusSnapshotToHistory(timestamp, statuses, estimates, previousStatuses = {}): boolean`

Core logic: appends a history point based on the latest status snapshot. `estimates` is the graph-level derived value from the same round as `statuses` (used to record `total_tasks_pending`), and `previousStatuses` is used to detect node restarts.

- **Reset detection**: if a node's `start_time` changes (restart) or `tasks_processed` goes backward (rollback), clears that node's history.
- **Deduplication**: if the timestamp is the same, updates the last point; otherwise appends a new point.
- **Trimming**: all modifications are constrained by `getCurrentHistoryLimit()`.
- **Return value**: `boolean` — whether the history data changed.

### `extractProgressData(histories, metric): Record<string, Array<{x: number; y: number}>>`

Converts the locally maintained `nodeHistories` mapping into an array of Chart.js-compatible `{x, y}` coordinate points.

- **Cumulative mode**: directly reads the raw field values of the sample points.
- **Delta mode (delta)**: when `metric` starts with `delta_`, computes the difference between adjacent sample points divided by the time difference to get a per-second rate. The first point is forced to `y = 0`.

### `trimNodeHistories(): boolean`

Trims the number of history points maintained locally on the frontend based on `webConfig.dashboard.historyLimit`. Returns a boolean indicating whether the history data changed.

### `getCurrentHistoryLimit(): number`

Gets the current limit on the number of points retained for the history curve. Prefers `webConfig.dashboard.historyLimit`, and defaults to `20` when invalid.

### `getChartThemeColors(): ThemeColors`

Reads the chart's text, grid line, and border colors under the current theme (dark/light) from CSS variables.

| Theme | Text color | Grid color | Border color |
|------|--------|--------|--------|
| Light | `--carbon-900` | `--carbon-200` | `--carbon-300` |
| Dark | `--carbon-200` | `--carbon-600` | `--carbon-500` |

---

## Metric Switcher (module-level auto-execution)

```typescript
function initHistoryMetricSwitcher() { ... }
initHistoryMetricSwitcher(); // executed immediately at module level
```

`initHistoryMetricSwitcher()` is called automatically in the module scope, **not invoked proactively by `main.ts`**. It is responsible for:

1. Syncing the active style of the `metricDots` buttons
2. Binding click events to switch `currentHistoryMetric`, then update the axis titles and redraw

## Data Flow

```mermaid
flowchart LR
    subgraph "loaders.ts"
        LS[loadStatuses]
    end
    subgraph "dashboard_history.ts"
        AS[appendStatusSnapshotToHistory]
        NH[nodeHistories]
        EC[extractProgressData]
        UC[updateChartData]
        CH[Chart.js instance]
    end
    LS -->|timestamp + statuses| AS
    AS --> NH
    NH --> EC
    EC -->|{x, y} coordinates| UC
    UC --> CH
```

## Usage Examples

```typescript
// Manually construct history data and render it
const mockHistory: Record<string, NodeHistory> = {
  "Processor": [
    { timestamp: 1000, tasks_processed: 10, tasks_succeeded: 9, tasks_failed: 1, tasks_duplicated: 0, tasks_pending: 90, total_tasks_pending: 120 },
    { timestamp: 1005, tasks_processed: 25, tasks_succeeded: 23, tasks_failed: 1, tasks_duplicated: 1, tasks_pending: 75, total_tasks_pending: 105 },
  ],
};

// nodeHistories = mockHistory;
// currentHistoryMetric = "tasks_succeeded";
// updateChartData();  // render to the line chart

// Update chart colors after a theme switch
// updateChartTheme();

// Manually trim history data
// webConfig.dashboard.historyLimit = 10;
// if (trimNodeHistories()) updateChartData();
```

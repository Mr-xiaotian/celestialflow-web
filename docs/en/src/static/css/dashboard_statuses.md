# src/celestialflow_web/static/css/dashboard_statuses.css

> 📅 Last Updated: 2026/09/24

Handles the layout and style definition of the dashboard node status cards, including the statistics grid, the four-segment progress bar, and the dynamic border colors based on node status.

> Note: Build-time metadata such as the node running mode/concurrency comes from `node_meta` in the graph metadata, and is rendered by `dashboard_statuses.ts` via `.stat-value`; this CSS file introduces no new selectors.

## Layout Structure

### Statistics Grid (`.stat-grid`)
- Uses a `grid` layout, fixed to two columns.
- Used to display core metrics such as success, pending, error, and duplicate.

### Node Card (`.node-card`)
- Uses a rounded card design (`border-radius: 1rem`).
- **Status border**: A 3px wide status bar is set on the left, with the color changing dynamically based on the node's running status:
  - `.status-running`: Uses `--cornflower-400` (blue), indicating it is running.
  - `.status-stopped`: Uses `--carbon-400` (gray), indicating it has stopped.
  - Default: Uses `--carbon-300`, indicating it has not started.

## Progress Bar Rendering (`.progress-bar`)

The progress bar consists of four segments (`.progress-segment`), each corresponding to a different task status color:

| Class Name | Corresponding Metric | Light Mode Color | Dark Mode Color |
|------|----------|--------------|--------------|
| `.seg-success` | Success | `--jade-400` | `--jade-700` |
| `.seg-error` | Error | `--crimson-400` | `--crimson-700` |
| `.seg-duplicate` | Duplicate | `--marigold-400` | `--marigold-700` |
| `.seg-pending` | Pending | `--carbon-300` | `--carbon-600` |

## Time Estimate Area (`.time-estimate`)

- Uses a monospace font (`monospace`) to ensure alignment.
- The `.elapsed` series of class names is used to color the individual digit segments of the elapsed time (success, error, duplicate).

## Interaction Effects

- **Click feedback**:
  - `.error-clickable`: The error count item shows a pointer cursor (`pointer`), hinting that it is clickable for navigation.

## Responsive Design

- When the width is less than `2048px`, `#dashboard-grid` switches to a single-column layout.
- Automatically handles the wrapping logic for long titles.

# src/celestialflow_web/static/css/dashboard_analysis.css

> 📅 Last Updated: 2026/09/24

Handles the style definition of the "Graph Analysis Info" card in the lower-left corner of the dashboard.

> Note: The graph-level execution mode (`graphMode`) field replaces the removed `scheduleMode`, and is rendered by `dashboard_analysis.ts` via `.analysis-value`; this CSS file introduces no new selectors.

## Layout Design (`.analysis-info`)

- **Structure**: Uses a vertical `flex` layout to display the key-value list.
- **Font**: Uses a small font (`0.75rem`) to accommodate more metadata.

## Data Row Styles (`.analysis-row`)

- **Left-right alignment**: The label name is on the left, and the specific value is on the right.
- **Status colors (`.analysis-value`)**:
  - `.ok`: Green (`--jade-600`), indicating it meets expectations (e.g., is a DAG).
  - `.warn`: Red (`--crimson-600`), indicating a potential risk (e.g., a cycle exists).

## Related Modules

- Data rendering is handled by `dashboard_analysis.ts`, which dynamically assigns the `ok` or `warn` class based on the analysis result returned by the backend (whether it is a DAG, the graph-level execution mode `graphMode`, etc.).

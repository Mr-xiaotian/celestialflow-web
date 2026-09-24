# src/celestialflow_web/static/css/dashboard_history.css

> 📅 Last Updated: 2026/09/24

Handles the styles of the control area above the node metric history chart (Chart.js), including the metric toggle button group.

## Layout Design (`.progress-card-header`)

- **Structure**: Uses a `flex` layout, with the card title on the left and the metric switcher on the right.
- **Adaptive**: Enables `flex-wrap: wrap` to automatically wrap on narrow screens.

## Metric Switcher (`.metric-indicators`)

- **Container**: `flex` layout, `flex-wrap: wrap`, centered arrangement, `gap: 1rem`.
- **Toggle buttons (`.metric-dot`)**:
  - Each button contains a color dot (`.dot`) and a text label (`.label`).
  - **Default state**: `opacity: 0.55`, de-emphasizing unselected metrics.
  - **Hover state**: `opacity: 0.8`.
  - **Active state (`.active`)**: `opacity: 1`, light gray background (`--carbon-100`), `--carbon-700` in dark mode.
  - **Trend metrics (`.dot.delta`)**: Hollow circle (`background: transparent`, only the border is colored), used to distinguish delta-type metrics from cumulative-type metrics.
- **Separator (`.metric-sep`)**: A `1px` wide vertical line, used to separate the cumulative metric group from the trend metric group.

## Related Modules

- The actual line chart is rendered into the canvas by `dashboard_history.ts` together with Chart.js; its internal colors (text, axis lines) are read from CSS variables in the TS code and set on the Chart.js instance.
- Metric switching is automatically bound by `initHistoryMetricSwitcher()` (module-level execution).

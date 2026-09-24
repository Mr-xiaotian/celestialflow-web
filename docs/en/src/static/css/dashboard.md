# src/celestialflow_web/static/css/dashboard.css

> 📅 Last Updated: 2026/09/24

Handles the core three-column layout architecture of the dashboard page.

## Layout Architecture (`.three-column-container`)

The dashboard uses a wide-screen three-column design, structuring the page with a `flex` layout:

- **Left panel (`.left-panel`)**: 25%. Usually holds the "Structure Graph" and "Graph Analysis Info" cards.
- **Middle panel (`.middle-panel`)**: 40%. The core area, used to display the "Node Running Status" card grid.
- **Right panel (`.right-panel`)**: 25%. Holds the "Node Metric Trends (Line Chart)" and "Overall Status Summary" cards.

## Page Display Logic

- **Tab switching**: Uses `.tab-content` and `.tab-content.active` together with JS to instantly switch between different feature pages (Dashboard / Errors / Injection).

## Dashboard Shared Tooltip System

Multiple dashboard cards reuse a unified tooltip style to provide supplementary explanations next to metric labels:

| Selector | Description |
|--------|------|
| `.stat-label-row` | A horizontal inline flex arrangement of the label and the tooltip trigger, `gap: 0.3rem` |
| `.tooltip-anchor` | The tooltip popup anchor container, `position: relative`, holding the trigger button and the bubble |
| `.tooltip-trigger` | The tooltip button, `1rem` circular, border `1px solid --carbon-300`, `cursor: help`, adapted for dark mode |
| `.tooltip-bubble` | The tooltip bubble, absolutely positioned below the anchor, dark background with white text, maximum width limited, shown on hover or focus; inverted in dark mode |

## Responsive Adaptation

- **Single-column fallback**: When the width is less than `2048px`, the layout automatically switches from a horizontal three-column layout to a vertical single-column flow layout, and all panels automatically fill 100% width, ensuring metrics remain readable on small-screen devices.

# src/celestialflow_web/static/css/dashboard_error_types.css

> 📅 Last Updated: 2026/09/24

Handles the style definition of the dashboard's "Error Type Distribution" panel, which uses a doughnut chart plus a legend to show the proportion of error types under each node.

## Panel Container (`.error-types-card`)

Serves as the root container of the entire error type panel; all internal child styles are scoped within it through nested rules.

### Panel Header (`.error-types-card-header`)

Uses a `flex` layout with `space-between` alignment: on the left is the title `.card-title` (already defined uniformly in `dashboard.css`), and on the right is the node filter dropdown.

### Node Filter (`.error-type-node-filter`)

- Minimum width `9rem`, rounded button style.
- The border uses `--carbon-300`, switching to `--carbon-600` in dark mode.
- In dark mode, the background and text colors are inverted to maintain visual consistency.

### Total Count (`.error-type-total`)

- Located below the panel header, font size `0.9rem`, gray text.
- Automatically switches to a light color in dark mode.

## Chart Area

### Chart Shell (`.error-type-chart-shell`)

- Uses a centered `flex` layout, minimum height `13rem`.
- Serves as the container for the Chart.js doughnut chart, providing stable drawing space.

### Chart Canvas (`#error-type-chart`)

- Fixes the width and height to `min(100%, 13rem)` via the ID selector, using `!important` to override the size automatically computed by Chart.js.
- Ensures the chart always stays square and does not exceed the container at different panel widths.

## Legend (`.error-type-legend`)

A vertically arranged legend list, using `flex-direction: column` and `0.5rem` spacing.

### Legend Row (`.error-type-legend-row`)

Each row contains three items: a color dot, the error type name, and the count:

| Child Element | Class Name | Description |
|--------|------|------|
| Color dot | `.error-type-legend-color` | A `0.8rem × 0.8rem` circle, `border-radius: 50%`, with the background color set dynamically by JS |
| Type name | `.error-type-legend-label` | `flex: 1`, supports automatic wrapping of long text (`word-break: break-word`) |
| Count value | `.error-type-legend-count` | Right-aligned, tabular figure font (`tabular-nums`), for easy value comparison |

The legend row background is `--carbon-50` light gray, switching to `--carbon-800` dark in dark mode.

## Dark Mode Adaptation

All selectors involving text colors, background colors, and border colors provide dark mode styles through `.dark-theme &` nested rules, uniformly using the Carbon color family:

| Element | Light Mode | Dark Mode |
|------|---------|---------|
| Filter background | `--white` | `--carbon-800` |
| Filter border | `--carbon-300` | `--carbon-600` |
| Filter/legend text | `--carbon-800` | `--carbon-100` |
| Auxiliary text (total, count) | `--carbon-600` | `--carbon-300` |
| Legend row background | `--carbon-50` | `--carbon-800` |

## Related Modules

- The panel's overall layout (card rounded corners, shadow, title style) is defined uniformly by `dashboard.css`.
- The chart data and interaction logic are driven by `dashboard_error_types.ts`, which re-renders the Chart.js doughnut chart and updates the legend when the node filter switches.

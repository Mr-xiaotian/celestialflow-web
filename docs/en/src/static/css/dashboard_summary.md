# src/celestialflow_web/static/css/dashboard_summary.css

> 📅 Last Updated: 2026/09/24

Handles the style definition of the "Overall Status Summary" panel in the lower-right corner of the dashboard, using vivid statistics cards to display global running metrics.

## Layout Structure (`.summary-grid`)

- Uses a `grid` layout, fixed to two columns.
- Each grid cell contains one `.summary-item`.

## Statistics Cards (`.summary-item`)

Each statistics item is assigned a different theme color based on its semantics, including a background color (`.summary-item`) and a value text color (`.summary-value`):

| Statistics Item | Class Name | Primary Color | Semantics |
|--------|------|--------|------|
| **Total Successful Tasks** | `.success` | `Jade` (green) | Tasks completed successfully |
| **Total Pending Tasks** | `.pending` | `Carbon` (gray) | Waiting to be processed in the queue |
| **Total Error Tasks** | `.error` | `Crimson` (red) | Processing failed, needs attention |
| **Total Duplicate Tasks** | `.duplicate` | `Marigold` (orange) | Hit the deduplication logic |
| **Active Nodes** | `.nodes` | `Cornflower` (blue) | The number of Stages currently running |
| **Total Remaining Time** | `.remain` | `Violet` (purple) | Global progress estimate |

## Style Features

- **Visual hierarchy**: The value uses a `2rem` bold font, and the label uses a `0.75rem` gray small font.
- **Dark mode**: Automatically switches the background color to a dark tone (such as the `900` series) and the text color to a light tone (such as the `300` series) to ensure contrast.
- **Interaction hint**: 
  - When the total error count is greater than 0, `.summary-value.error-clickable` shows a pointer cursor, guiding the user to click through to view error details.

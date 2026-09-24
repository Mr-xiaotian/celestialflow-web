# src/celestialflow_web/static/css/errors.css

> 📅 Last Updated: 2026/09/24

Handles the style definition of the search box, filters, data table, and pagination controls under the "Error Logs" tab.

## Search and Filtering (`.filter-container`)

- **Layout**: Uses a `flex` layout, showing the title on the left and the search input and node dropdown filter on the right.
- **Search box (`.error-search-input`)**:
  - Has a smooth transition effect (`transition: all 0.2s`).
  - **Focus state**: When focused, the border color deepens and the background color changes slightly to provide visual feedback.

## Data Table (`#errors-table`)

- **Structure**: A standard HTML table, but it automatically converts to a card flow layout on mobile/narrow screens.
- **Cell styles**:
  - `.error-id`: Displays the ID in a gray tone, reducing visual noise.
  - `.error-cell`: Specifically used to display the error repr, using a monospace font (`monospace`) and a red tone (`Crimson`). To prevent overly long error messages from breaking the layout, `max-width: 40ch` is set and truncated with an ellipsis (`ellipsis`).
  - `.retry-link`: The "Retry" action link in an error row, `--cornflower-600` text color, with the underline deepened on hover or focus, and `--cornflower-300` in dark mode.
  - `.retry-disabled`: The placeholder text when retry is not possible, `--carbon-400` gray text, with no interaction feedback, and `--carbon-500` in dark mode.

## Pagination Controls (`.pager-container`)

- **Page number links (`.pager-link`)**: Support hover highlighting.
- **Pager buttons (`.pager-btn`)**:
  - Include "Previous Page" and "Next Page" icon buttons.
  - **Disabled state**: On the first or last page, the button turns gray and is not clickable (`cursor: not-allowed`).

## Responsive Design

- **Table to cards**: When the width is less than `2048px`, the table `thead` is hidden, and each `tr` row becomes an independent card block with a rounded border.
- **Pseudo-element labels**: The table column names are injected into the card via `::before { content: attr(data-label) }`, so mobile users can still identify the meaning of the data.
- **Error expansion**: In card mode, the truncation limit of `.error-cell` is removed (`white-space: normal`), switching to automatic wrapping to show more details.

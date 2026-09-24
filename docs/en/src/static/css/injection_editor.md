# src/celestialflow_web/static/css/injection_editor.css

> 📅 Last Updated: 2026/09/24

Handles the style definition of the editor on the right side of the task injection page, including the JSON input area, validation messages, and the action button group.

## Editor Container (`.injection-editor-card`)

- Uses a vertical flex layout with a fixed `gap: 1rem`.

## Editor Header (`.editor-header`)

- **Layout**: `flex` left-right distribution, with the description text + current node info on the left and the action button group on the right.
- `.editor-node-meta`: Allows shrinking under narrow widths (`min-width: 0`).
- `.editor-caption`: A small description text above the "Current Node" title, `0.75rem`, gray tone (`--carbon-500`).

## Current Node Info (`.editor-node-row`)

- The row layout of the node name and the "Edited" label on the right, supporting `flex-wrap: wrap`.
- `.current-node-name`: The currently selected node name, `1rem`, `font-weight: 600`.

## Button Styles (`.btn-small`, `.btn-select`, `.btn-clear`)

| Selector | Purpose | Background Color | Text Color |
|--------|------|--------|--------|
| `.btn-small` | Generic small button | — | — |
| `.btn-select` | Validate/format button | `--cornflower-50` (light) / `--cornflower-700` (dark) | `--cornflower-700` (light) / `--carbon-100` (dark) |
| `.btn-clear` | Clear draft button | `--carbon-100` (light) / `--carbon-600` (dark) | `--carbon-700` (light) / `--carbon-100` (dark) |

- **Disabled state**: `opacity: 0.6`, `cursor: not-allowed`.

## JSON Input Area (`.json-input-section`)

- **JSON header (`.json-header`)**: The top row with the label left-aligned.
- **JSON label (`.json-label`)**: `0.75rem`, `font-weight: 500`.
- **JSON editor (`.json-textarea`)**:
  - Monospace font (`Monaco, Menlo, monospace`), `min-height: 20rem`, supports vertical resizing.
  - The border becomes `--cornflower-400` on focus.
  - Disabled state: `--carbon-50` background, `--carbon-400` text.

## Validation Message (`.validation-message`)

| State | CSS Class | Color |
|------|--------|------|
| Success | `.validation-success` | `--jade-600` (light) / `--jade-400` (dark) |
| Failure | `.validation-error` | `--crimson-600` (light) / `--crimson-400` (dark) |
| Neutral | `.validation-neutral` | `--carbon-500` (light) / `--carbon-400` (dark) |

- `min-height: 1.25rem`, `font-size: 0.75rem`, located below the JSON editor.

## Editor Bottom Button Group (`.editor-actions`)

- `flex` layout, `gap: 0.75rem`, `flex-wrap: wrap`.

## Related Modules

- The interaction logic is driven by functions such as `renderCurrentNodeEditor()`, `validateCurrentDraft()`, and `formatCurrentDraft()` in `injection.ts`.

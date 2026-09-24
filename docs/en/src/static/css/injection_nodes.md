# src/celestialflow_web/static/css/injection_nodes.css

> 📅 Last Updated: 2026/09/24

Handles the style definition of the node browsing list on the left side of the task injection page, including node items, the selected state, the disabled state, and the "Edited" label.

## Node List Container (`.node-list`)

- Vertical flex layout, `gap: 0.5rem`.
- `max-height: 30rem`, with vertical scrolling when exceeded (`overflow-y: auto`).

## Node Item (`.node-item`)

- **Layout**: `flex` left-right distribution (node info + right-side label), `gap: 0.75rem`.
- **Base style**: Rounded `0.75rem`, border `1px solid --carbon-200`.
- **Hover effect**: The background lightens (`--carbon-50`), the border turns blue (`--cornflower-300`), and it shifts up slightly by `-1px`.
- **Dark mode**: Background `--carbon-700`, `--carbon-600` on hover.

| CSS Class | Description |
|--------|------|
| `.node-item` | Base node item style |
| `.node-item.active-node` | The currently selected node: blue border (`--cornflower-500`) + light blue background (`--cornflower-50`) |
| `.disabled-node` | Non-injectable node: `opacity: 0.55`, `cursor: not-allowed`, `pointer-events: none` |

## Node Info Area (`.node-info`)

- `min-width: 0`, `flex: 1`, allowing text to shrink in narrow spaces.

## Node Name (`.node-name`)

- `font-weight: 600`, `word-break: break-all`.
- Light mode `--carbon-800`, dark mode `--carbon-100`.

## "Edited" Label (`.node-side-tag`)

- `inline-flex`, `flex-shrink: 0`.
- Capsule-shaped (`border-radius: 999px`), with small padding.
- Light mode: blue background (`--cornflower-100`) + blue text (`--cornflower-700`).
- Dark mode: dark blue background (`--cornflower-800`) + light blue text (`--cornflower-100`).

## Related Modules

- The node list is dynamically rendered by `renderNodeList()` in `injection.ts`.
- The selection logic is driven by `selectNode()`, implementing highlighting by toggling the `.active-node` class.
- The filter logic of the "Show only injectable nodes" toggle refers to `isInjectableNode()`.

# src/celestialflow_web/static/css/base.css

> 📅 Last Updated: 2026/09/24

Handles the system's global base styles, dark mode switching, common components (cards, tabs, badges), the responsive base layout, and the card layout editor modal styles.

## Global Basics

- **Reset**: Unifies the box model (`border-box`) and sets the default font stack.
- **Background and colors**: Defines the body background color in light (`--carbon-50`) and dark (`--carbon-900`) modes.
- **Container**: `.container` limits the maximum content width to `1200px` and centers it horizontally.

## Core Component Styles

### Header and Navigation (`header`)
- **Control panel (`.control-panel`)**: Contains the refresh interval selector, the settings gear, and the theme toggle button; in dark mode, all non-settings buttons inside use a carbon background and border.
- **Refresh control container (`.refresh-container`)**: Lays out the refresh interval label and the dropdown selector horizontally, with `gap: 0.5rem`.
- **Settings button (`.btn-settings`)**: Transparent background, no border, with hover and `focus-visible` feedback, adapted for dark mode.
- **Settings panel (`.settings-panel`)**: Absolutely positioned, floating below the gear; a rounded white card that uses a `--carbon-800` background in dark mode. Its children include:
  - `.settings-header`: The header, with the title and close button at the two ends and a bottom divider.
  - `.settings-title`: The title text, `0.85rem`, `font-weight: 600`.
  - `.settings-close`: The close button, transparent background, changes color on hover.
  - `.settings-body`: The main content container, `padding: 0.5rem 0.75rem`.
  - `.settings-status`: The status hint area, separated by a top border, `0.75rem`.
  - `.settings-status-success` / `.settings-status-error`: Success/failure text colors.
  - `.settings-item`: A single settings entry, arranging the label and selector with `grid`.
  - `.settings-toggle`: The toggle checkbox, right-aligned.
  - `.settings-divider` / `.settings-divider-label`: The group divider and its label.
  - `.settings-empty`: The empty-state hint, centered gray text.
  - `.settings-item-center`: A center-aligned settings entry, commonly used for action buttons.
- **Theme toggle button (`#theme-toggle`)**: Absolutely positioned on the right side of the header, a rounded pill button that changes color on hover; on narrow screens it is changed to `position: static`, `order: 3` in `@media (max-width: 2048px)`.

### Tab System (`.tabs`)
- Implements horizontally arranged tab navigation, supporting the `.active` class to highlight the currently selected module (Dashboard, Error Logs, Task Injection).

### Common Card (`.card`)
- Has a unified rounded background (`1rem`) and shadow effect.
- **Hover feedback**: On hover, it produces a slight upward shift (`translateY(-2px)`).

## Utility Classes

- **Color classes**: Provides quick coloring classes such as `.text-success` (green), `.text-error` (red), `.text-pending` (gray), `.text-duplicate` (orange).
- **Delta classes**: The `.text-delta-*` series is used in the dashboard to display lighter-colored metric change values.
- **Hidden**: The `.hidden` class is used to quickly control element visibility from JS.
- **Small font**: `.text-sm` sets `font-size: 0.75rem`.
- **Carbon text**: `.text-carbon` colors text with `--carbon-400`.

## Empty Placeholder (`.empty-placeholder`)

Used as a centered text placeholder when data is empty; defaults to `text-align: center`, `color: --carbon-400`, `padding: 2rem`, `font-size: 1rem`, and becomes lighter in dark mode.

## Common Tip Section (`.tip-section`)

An informational tip bar reused across pages, with a themed border on the left:

| Selector | Description |
|--------|------|
| `.tip-section` | The tip bar container, `--cornflower-50` background, a `4px` solid border on the left, `border-radius` rounded only on the right side |
| `.tip-content` | The inner horizontal flex layout, with the icon and text center-aligned |
| `.tip-icon` | The tip icon, `1.25rem` square, `color: --cornflower-500`, with `0.75rem` of space on the right |
| `.tip-text` | The tip body, `0.75rem`, light `--cornflower-600` / dark `--carbon-300` |

## Modal Overlay (`.overlay`)

- **`.overlay`**: A fixed-position full-screen semi-transparent black overlay (`rgba(0,0,0,0.4)`), `z-index: 200`, centered flex layout, used to host modal windows such as the card layout editor.
- **`.overlay.hidden`**: Sets the overlay to `display: none`, working with JS to control popup visibility.

## Card Layout Editor (`.layout-editor` series)

The card layout editor floats above the overlay as a modal window and supports drag-and-drop reordering of the three-column dashboard cards. Main sub-selectors:

| Selector | Description |
|--------|------|
| `.layout-editor` | The editor's main container: a rounded white card, `max-width: 700px`, vertical flex layout |
| `.dark-theme .layout-editor` | Uses a `--carbon-800` background in dark mode |
| `.layout-editor-header` | The title bar: title on the left, close button on the right |
| `.layout-editor-title` | The title text: `1.1rem`, `font-weight: 600` |
| `.layout-editor-columns` | The three-column grid area: `grid-template-columns: repeat(3, 1fr)`, vertically scrollable |
| `.layout-column` | A single column container: a vertical flex column |
| `.layout-column-header` | The column title: centered, underlined with a divider, small font |
| `.layout-column-dropzone` | The drag-and-drop dropzone: dashed border, minimum height `120px`, vertically arranged flex cards |
| `.layout-column-dropzone.drag-over` | Highlight while dragging over: blue border + light blue background |
| `.layout-card` | A draggable card item: gray rounded background, `cursor: grab`, `user-select: none` |
| `.layout-card:hover` | Hover lift and shadow effect |
| `.layout-card.dragging` | Semi-transparent while dragging (`opacity: 0.5`) |
| `.layout-card-name` | The card name text: `0.8rem`, `font-weight: 500` |
| `.layout-card-handle` | The drag handle: the ⠿ character, `color: --carbon-400` |
| `.layout-unused` | The unused card pool area: located below the three columns |
| `.layout-unused-header` | The unused pool title: `0.75rem`, gray |
| `.layout-unused .layout-column-dropzone` | The unused pool dropzone: arranged horizontally (`flex-direction: row`), minimum height `40px` |
| `.layout-editor-footer` | The bottom button bar: right-aligned, top divider |
| `.btn-layout-save` | The save button: blue fill, occupying `80%` width |
| `.btn-layout-reset` | The reset button: gray outline, occupying `20%` width |
| `.btn-layout-editor` | The entry button in the settings panel: blue fill, rounded |
| `.error-columns-shell` | The two-column grid container of the error log page's field editor (`grid-template-columns: repeat(2, minmax(0, 1fr))`) |
| `.error-columns-editor` | Style overrides inside the error log page's field editor: the bottom buttons become `auto` width with `min-width: 7rem`; the dropzone gets `min-height: 16rem` |
| `.dark-theme .btn-layout-save` / `.dark-theme .btn-layout-reset` | The unified dark styles of the above two buttons in dark mode (`--carbon-700` background, `--carbon-200` text, `--carbon-600` border) |

## Responsive Rules

### `@media (max-width: 2048px)`

The following adjustments are triggered when the viewport width is ≤ 2048px:
- The `h1` title width is set to `100%` to prevent long titles from overflowing
- The `#theme-toggle` theme toggle button is changed to `position: static`, `order: 3`, adapting to the control bar reflow on narrow screens
- `.error-columns-shell` switches to a single column (`grid-template-columns: 1fr`), adapting to the single-column display of the error log page's field editor on narrow screens
- `.settings-panel` becomes a fixed centered popup layer `4rem` from the top (full-width adaptation on mobile)

## Dark Mode Adaptation

Uses the `.dark-theme` class as the root node marker. In this mode, the system automatically adjusts the following properties:
- Background color and primary text color.
- The background and border colors of cards and the settings panel.
- The background and border of form controls (select, button).
- Some semantic text colors (such as the text color of the pending state).

# src/celestialflow_web/static/ts/layout_editor.ts

> 📅 Last Updated: 2026/09/24

## Purpose

`layout_editor.ts` is the frontend module for the dashboard **card layout editor**. It provides a drag-and-drop interface in a floating window (overlay), letting users freely adjust which cards each of the dashboard's left, middle, and right columns contains, and persists the result to `config.json`.

The editor uses [SortableJS](https://sortablejs.github.io/Sortable/) to implement cross-region drag-and-drop sorting, supporting dragging between the three columns and the "unused card pool".

---

## Global Constants and State

### `DEFAULT_WEB_CONFIG.dashboard.layout` (from `web_config.ts`)

The default three-column card layout config, defining the factory card assignment (`resetLayout()` uses it):

```javascript
{
  left:   ["mermaid", "analysis"],
  middle: ["status"],
  right:  ["progress", "error-types", "summary"],
}
```

### `originalLayout`

The layout snapshot (`{ left, middle, right }`) saved when the layout editor is opened, used to restore unsaved drag changes when closing with `restore=true`.

| Column | Default cards | Description |
|------|----------|------|
| `left` | mermaid, analysis | Graph rendering + topology analysis |
| `middle` | status | Node status table |
| `right` | progress, error-types, summary | Progress + error type distribution + global summary |

---

## Core Functions

### `renderCard(cardId: string): HTMLElement`

Creates a draggable card DOM element.

| Parameter | Type | Description |
|------|------|------|
| `cardId` | `string` | Card identifier (such as `"mermaid"`, `"status"`) |

**Returns:** a `<div>` element with the `.layout-card` CSS class, storing a `data-card-id` attribute and a drag handle.

```html
<div class="layout-card" data-card-id="mermaid">
  <span class="layout-card-name">Graph rendering</span>
  <span class="layout-card-handle" aria-hidden="true">⠿</span>
</div>
```

The card name is looked up in `CARD_META[cardId]` for a localized display name; if not found, it falls back to the raw `cardId`.

---

### `openLayoutEditor()`

Opens the layout editor and renders the current layout.

**Flow:**

```
┌────────────────────────────────────────┐
│  1. Show the overlay                   │
│  2. Read webConfig.dashboard.layout    │
│  3. Save a copy to originalLayout      │
│  4. Render the left/middle/right columns│
│  5. Render the unused card pool        │
│  6. Call initSortable() to enable dragging│
└────────────────────────────────────────┘
```

The unused card pool contains all cards in `ALL_CARD_IDS` that are not referenced by the three columns.

---

### `closeLayoutEditor(restore: boolean = true)`

Closes the layout editor.

| Parameter | Type | Default | Description |
|------|------|--------|------|
| `restore` | `boolean` | `true` | Whether to restore the original layout. When `true`, undoes all unsaved drag changes; when `false`, keeps the current in-memory state |

**Behavior:**
- `restore=true` (default): overwrites `webConfig.dashboard.layout` with `originalLayout`, and calls `applyConfig()` to refresh the dashboard. This is the behavior when clicking the close button or clicking the overlay.
- `restore=false`: hides the overlay but does not restore the data. This is the behavior called after a successful save.

---

### `initSortable()`

Initializes SortableJS, enabling cross-region dragging in the four drop zones.

**Regions involved:**

| ID | Description |
|----|------|
| `layout-dropzone-left` | Left column dropzone |
| `layout-dropzone-middle` | Middle column dropzone |
| `layout-dropzone-right` | Right column dropzone |
| `layout-dropzone-unused` | Unused card pool |

**SortableJS configuration:**

| Config item | Value | Description |
|--------|-----|------|
| `group` | `"dashboard-layout"` | Shared group name; the four regions can be dragged between each other |
| `animation` | `150` | Drag animation duration (ms) |
| `ghostClass` | `"dragging"` | Placeholder CSS class while dragging |
| `dragClass` | `"dragging"` | CSS class of the card itself while dragging |

---

### `destroySortableInstances(): void`

Destroys all currently mounted Sortable instances before redrawing the drop zones, avoiding duplicate listeners and instance leaks.

---

### `syncLayout()`

Synchronizes the current three-column card order in the DOM back to `webConfig.dashboard`.

**Flow:**
1. Iterate over the `left`, `middle`, `right` drop zones
2. Read `data-card-id` from each zone's `.layout-card` elements
3. Write them into `webConfig.dashboard.layout` as ordered arrays

> This function **does not persist**; it only updates the in-memory structure. Persistence is done by `saveLayout()`.

---

### `saveLayout()`

Saves the layout and refreshes the dashboard.

**Flow:**

```
┌───────────────────────────────────┐
│  1. syncLayout()                  │
│  2. await saveWebConfig()         │
│     ├─ Success → applyConfig()    │
│     │         closeLayoutEditor(false)
│     └─ Failure → show save error  │
└───────────────────────────────────┘
```

`saveWebConfig()` persists `webConfig` to `config.json` via `POST /api/push_config`.

---

### `resetLayout()`

Resets the layout to the default layout.

**Flow:**

1. Reset `webConfig.dashboard.layout` to a deep copy of `DEFAULT_WEB_CONFIG.dashboard.layout`
2. Clear and re-render the left, middle, and right columns (in the default card order)
3. Clear and recompute the unused card pool
4. Call `initSortable()` again to bind dragging

> This operation **does not save automatically**; the user still needs to click the save button to persist it.

---

## Event Bindings

The module binds the following events on `DOMContentLoaded`:

| Target element | Event | Handler |
|----------|------|----------|
| `#open-layout-editor` | `click` | `openLayoutEditor()` |
| `#layout-editor-close` | `click` | `closeLayoutEditor()` (restore) |
| `#layout-editor-overlay` | `click` | `closeLayoutEditor()` when clicking outside the overlay (restore) |
| `#layout-save-btn` | `click` | `saveLayout()` |
| `#layout-reset-btn` | `click` | `resetLayout()` |

---

## Usage Examples

### HTML Structure

The layout editor depends on the following DOM structure:

```html
<!-- Trigger button -->
<button id="open-layout-editor">Edit Layout</button>

<!-- Overlay -->
<div id="layout-editor-overlay" class="hidden">
  <div class="layout-editor-panel">
    <h2>Card Layout</h2>

    <!-- Three-column dropzones -->
    <div id="layout-dropzone-left"></div>
    <div id="layout-dropzone-middle"></div>
    <div id="layout-dropzone-right"></div>

    <!-- Unused card pool -->
    <div id="layout-dropzone-unused"></div>

    <!-- Action buttons -->
    <button id="layout-save-btn">Save</button>
    <button id="layout-reset-btn">Reset</button>
    <button id="layout-editor-close">Close</button>
  </div>
</div>
```

### Customizing the Default Layout

Modify `DEFAULT_WEB_CONFIG.dashboard.layout` in `src/celestialflow_web/static/ts/web_config.ts` to change the factory layout:

```typescript
const DEFAULT_WEB_CONFIG: WebConfig = {
  // ...
  dashboard: {
    historyLimit: 20,
    structureEdgeLabel: "none",
    useTotalPendingInStatus: false,
    layout: {
      left:   ["mermaid", "analysis"],
      middle: ["status"],
      right:  ["progress", "error-types", "summary"],
    },
  },
  // ...
};
```

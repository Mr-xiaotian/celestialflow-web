# src/celestialflow_web/templates/index.html

> 📅 Last Updated: 2026/09/24

The Jinja2 template file for the Web UI, defining the complete page structure of the monitoring system.

## Overall Layout

The page is divided into three main areas:

```
<header>  — Top control bar (settings panel, theme toggle)
<main>
  ├─ .tabs           — Tab navigation (Dashboard / Errors / Task Injection)
  ├─ #dashboard      — Dashboard (three-column layout)
  ├─ #errors         — Error logs
  └─ #task-injection  — Task injection
```

The template uses Jinja2's `{% include %}` to split each responsibility area into sub-templates:

| Partial | Responsibility |
|---------|------|
| `partials/head.html` | `<head>` section: favicon, CSS, CDN libraries (Chart.js, SortableJS, Mermaid) |
| `partials/header.html` | Top control bar and settings button, the container for `#settings-panel` |
| `partials/settings_panel.html` | Controls in the settings panel for language, refresh rate, auto-refresh, error pagination/sorting/jump/field editing, dashboard history/edge delta/pending mode/layout editing, and the injection page's "injectable only", etc. |
| `partials/tab_dashboard.html` | Dashboard tab container, containing the three empty slots `.left-panel` / `.middle-panel` / `.right-panel` and the hidden `#card-pool` |
| `partials/tab_errors.html` | Errors tab: search box, node filter, error table, pagination container |
| `partials/tab_injection.html` | Task injection tab: node browsing, current node editing, pending data preview, submission and status messages |
| `partials/modal_layout_editor.html` | Dashboard card layout editing modal (`#layout-editor-overlay`) |
| `partials/modal_error_columns_editor.html` | Error table column editing modal (`#errors-columns-editor-overlay`) |
| `partials/scripts.html` | Imports the single entry `js/main.js` as native ESM (see below) |

## Header Control Bar

| Element | ID / Class | Description |
|------|-----------|------|
| Settings button | `#settings-btn` | Click to open the settings panel, with a11y attributes |
| Settings panel | `#settings-panel` | Contains settings for refresh, history, language, pagination, delta toggle, etc. |
| UI language | `#language-select` | Supports switching between Chinese, English, and Japanese |
| Structure graph delta | `#structure-edge-delta` | Toggle controlling whether the success-count delta is shown on Mermaid graph edges |
| Theme toggle | `#theme-toggle` | Rounded pill button that switches between light and dark modes |

## Dashboard Three-Column Structure

`tab_dashboard.html` only provides three empty slot containers and the hidden `#card-pool`. All card DOM is injected into `#card-pool` by `web_config.ts` via `CARD_TEMPLATES` at module load, and then moved to the three columns by `applyDashboardLayout()` according to `webConfig.dashboard.layout`.

### Left column `.left-panel`

| Card | Class | Description |
|------|-------|------|
| Task structure graph | `.mermaid-card` | Mermaid flowchart, supporting node coloring and edge deltas |
| Graph analysis info | `.analysis-card` | Topology insight information |

### Middle column `.middle-panel`

| Card | Class | Description |
|------|-------|------|
| Node running status | `.status-card` | Dynamic node cards, with progress bars and real-time delta statistics |

### Right column `.right-panel`

| Card | Class | Description |
|------|-------|------|
| Node metric trends | `.progress-card` | Historical line chart with switchable metrics (completed/succeeded/errors/duplicated/pending) |
| Error type distribution | `.error-types-card` | Error type doughnut chart and legend, filtered by node |
| Overall status summary | `.summary-card` | Global 6-cell statistics dashboard |

## External Dependencies (CDN)

| Library | Version | Purpose |
|----|------|------|
| Chart.js | Not pinned (CDN latest) | Line chart rendering |
| SortableJS | `@latest` | Drag-and-drop sorting for dashboard layout and error table columns |
| Mermaid | `^10` (ESM) | Task graph visualization rendering |

## JS Module Loading

The frontend uses native ESM; `partials/scripts.html` imports only the single entry `js/main.js`, and the remaining modules are chained together by its static `import`s:

```html
<script
    type="module"
    src="{{ request.url_for('static', path='js/main.js') }}"
></script>
```

The entry's import order determines the module evaluation order:

```html
i18n.js               ← Internationalization support
utils.js              ← Common utility functions
web_config.js         ← Configuration management logic + card DOM injection (calls ensureAllCards at module load)
loaders.js            ← Data layer: status/graph meta fetching and local derivation
util_estimators.js    ← Graph-level derived metric estimation
dashboard_statuses.js ← Node status card rendering
dashboard_structure.js← Structure graph rendering
errors.js             ← Error log pagination + column editor
dashboard_analysis.js ← Topology analysis display
dashboard_error_types.js ← Error type distribution card
dashboard_summary.js  ← Summary statistics
dashboard_history.js  ← History charts
injection.js          ← Task injection logic
layout_editor.js      ← Card layout editor (depends on web_config's CARD_TEMPLATES, PANEL_SELECTOR_MAP, and applyDashboardLayout)
main.js               ← Global entry and polling coordination
```

> Note: `web_config.js` immediately calls `ensureAllCards()` at module load, injecting all card DOM into `#card-pool` in advance. Therefore the entry must import it first, ensuring that the top-level `getElementById` in subsequent `dashboard_*` modules can find the corresponding nodes; `tests/test_server.py` verifies this constraint through a module evaluation order test. All build artifacts must be reachable from `main.js` via `import`.

## CSS Style References

```html
css/_colors.css             ← Color variable definitions
css/base.css                ← Global base styles and the settings panel
css/dashboard.css           ← Dashboard layout and tab containers
css/dashboard_structure.css  ← Structure graph-specific styles
css/dashboard_analysis.css   ← Analysis card-specific styles
css/dashboard_statuses.css   ← Node card-specific styles
css/dashboard_summary.css    ← Summary panel-specific styles
css/dashboard_history.css    ← History chart-specific styles
css/dashboard_error_types.css ← Error type distribution card-specific styles
css/errors.css              ← Error log page styles
css/injection_layout.css     ← Injection page layout styles
css/injection_nodes.css      ← Injection page node list styles
css/injection_editor.css     ← Injection page editor styles
css/injection_preview.css    ← Injection page preview styles
```

## Card Layout Editor Modal (`#layout-editor-overlay`)

A floating modal (hidden by default via `.overlay.hidden`) that supports drag-and-drop sorting of the three-column dashboard cards.

- **Overlay**: `#layout-editor-overlay` / `.overlay` — full-screen semi-transparent black background
- **Editor body**: `#layout-editor` / `.layout-editor` — rounded card container
- **Three-column drop zones**: three drop zones (left, middle, right) (`#layout-dropzone-left`, `#layout-dropzone-middle`, `#layout-dropzone-right`), with drag-and-drop implemented via SortableJS
- **Unused pool**: `#layout-dropzone-unused` — holds cards removed from the three columns
- **Bottom buttons**: Save (`#layout-save-btn`) and Reset to default (`#layout-reset-btn`)
- Opened via the `#open-layout-editor` button in the settings panel; closed by clicking `#layout-editor-close` or outside the overlay
- On save, calls `applyDashboardLayout()` to take effect immediately, then calls `saveWebConfig()` to persist to the backend

## Error Table Column Editor Modal (`#errors-columns-editor-overlay`)

Introduced by `partials/modal_error_columns_editor.html`:

- **Overlay**: `#errors-columns-editor-overlay` / `.overlay` — reuses the same overlay style as the layout editor
- **Body**: `#errors-columns-editor` / `.layout-editor.error-columns-editor` — contains two dropzones: `#errors-columns-dropzone-visible` and `#errors-columns-dropzone-hidden`
- **Bottom buttons**: Save (`#errors-columns-save-btn`) and Reset to default (`#errors-columns-reset-btn`)
- Opened via the `#open-error-columns-editor` button in the settings panel; closed by clicking `#errors-columns-editor-close` or outside the overlay
- The logic is handled by `openErrorColumnsEditor()` / `saveErrorColumns()` in `errors.ts`; see `errors.md` for details

## Usage Examples

### Accessing via the Browser

After starting the Web server, visit the following in the browser address bar:

```
http://127.0.0.1:5000
```

Start command:

```bash
# Start from the command line (default 0.0.0.0:5000)
celestialflow-web

# Or start in Python
python -c "from celestialflow_web import TaskWebServer; TaskWebServer(host='127.0.0.1', port=5000).start_server()"
```

After opening it in a browser, you will see three tabs:
- **Dashboard**: Displays the task graph's structure graph, node running status, metric trends, and overall summary in real time
- **Errors**: View and search error records in pages
- **Task Injection**: Inject new tasks into specified nodes

### Template Modification Example

`index.html` uses the Jinja2 template engine, and the interface can be customized through custom template variables or by directly modifying the HTML.

#### Changing the Page Title

Edit `index.html` and find the `<title>` tag:

```html
<!-- Original content -->
<title>Task Graph Monitoring System</title>

<!-- Change to a custom title -->
<title>My Task Monitoring</title>
```

#### Adjusting the Dashboard Layout

> ⚠️ `tab_dashboard.html` **only provides** three empty slot containers (`.left-panel` / `.middle-panel` / `.right-panel`) and the hidden `#card-pool`. **Do not directly modify the card order in the HTML**; all cards are injected into `#card-pool` by `web_config.ts` via `CARD_TEMPLATES` at module load, and then moved to the three columns by `applyDashboardLayout()` according to `webConfig.dashboard.layout`.

If you need to adjust the three-column layout, prefer the following two approaches:

1. **Runtime**: Open "Edit Dashboard Layout" (`#open-layout-editor`) in the settings panel, drag cards to the target columns in the `#layout-editor-overlay` modal, and save.
2. **Defaults**: Edit `DEFAULT_WEB_CONFIG.dashboard.layout` in `src/celestialflow_web/static/ts/web_config.ts`, for example:

```typescript
dashboard: {
    layout: {
        left: ["analysis", "mermaid"],   // Put the analysis card at the very top
        middle: ["status"],
        right: ["progress", "summary", "error-types"],
    },
}
```

Available card keys: `mermaid`, `analysis`, `status`, `progress`, `error-types`, `summary`.

#### Dynamically Controlling via Configuration

All runtime UI preferences are controlled by the grouped `WebConfig`, which contains four subsections: `global` / `dashboard` / `errors` / `injection`. `web_config.ts` reads the user configuration at startup via `GET /api/pull_config`; on save it calls `POST /api/push_config` to overwrite it entirely. Initial values can be provided through the backend `config.json`:

```json
{
    "global": {
        "theme": "dark",
        "language": "zh-CN",
        "autoRefreshEnabled": true,
        "refreshInterval": 5000
    },
    "dashboard": {
        "historyLimit": 20,
        "showStructureEdgeDelta": true,
        "useTotalPendingInStatus": true,
        "layout": {
            "left": ["mermaid", "analysis"],
            "middle": ["status"],
            "right": ["progress", "error-types", "summary"]
        }
    },
    "errors": {
        "pageSize": 50,
        "sortOrder": "newest",
        "jumpToInjectionAfterRetry": true,
        "columns": ["index", "event_id", "message", "stage", "task", "time", "retry"]
    },
    "injection": {
        "showInjectableOnly": true
    }
}
```

> For detailed field descriptions, see [`web_config.md`](../static/ts/web_config.md). After modification, it takes effect via the "Save Settings" button in the settings panel or by waiting for `saveWebConfig()` to trigger automatically.

#### Adding Custom CSS

Place the custom style file in the `src/celestialflow_web/static/css/` directory and import it in `partials/head.html` using Jinja2's `request.url_for`, ensuring the path still resolves correctly when mounted under a non-root path:

```html
<link
    rel="stylesheet"
    href="{{ request.url_for('static', path='css/custom.css') }}"
/>
```

JS scripts use `{{ request.url_for('static', path='js/xxx.js') }}` in the same way.

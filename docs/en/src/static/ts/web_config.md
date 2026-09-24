# src/celestialflow_web/static/ts/web_config.ts

> 📅 Last Updated: 2026/09/24

Manages config loading, normalization, saving, and application for the web frontend. The config uses a **grouped structure** (`global`, `dashboard`, `errors`, `injection`), and also supports automatic migration from the legacy flat format.

## Type Definitions

### Current Grouped Config

```typescript
type WebGlobalConfig = {
  theme: "light" | "dark";
  autoRefreshEnabled: boolean;
  refreshInterval: number;
  language: Lang;
};

type WebDashboardConfig = {
  historyLimit: number;
  structureEdgeLabel: StructureEdgeLabel;
  useTotalPendingInStatus: boolean;
  layout: DashboardLayout;
};

type WebErrorsConfig = {
  pageSize: number;
  sortOrder: "newest" | "oldest";
  jumpToInjectionAfterRetry: boolean;
  columns: ErrorColumnKey[];
};

type WebInjectionConfig = {
  showInjectableOnly: boolean;
};

type WebConfig = {
  global: WebGlobalConfig;
  dashboard: WebDashboardConfig;
  errors: WebErrorsConfig;
  injection: WebInjectionConfig;
};
```

### Legacy Compatibility Types

```typescript
type LegacyWebConfig = {
  theme?: "light" | "dark";
  autoRefreshEnabled?: boolean;
  refreshInterval?: number;
  language?: Lang;
  historyLimit?: number;
  showStructureEdgeDelta?: boolean;
  structureEdgeLabel?: StructureEdgeLabel;
  useTotalPendingInStatus?: boolean;
  errorPageSize?: number;
  errorSortOrder?: "newest" | "oldest";
  dashboard?: Partial<DashboardLayout>;
};
```

> Migration rule: in the legacy flat format, `showStructureEdgeDelta === true` maps to `structureEdgeLabel: "delta"`, and `false` maps to `"none"`.

## Global Variables

| Variable | Type | Description |
|------|------|------|
| `webConfig` | `WebConfig` | Current runtime config object, initialized from `DEFAULT_WEB_CONFIG` at module load |
| `saveConfigPending` | `boolean` | Whether there are still new config changes waiting to be persisted |
| `saveConfigPromise` | `Promise<boolean> \| null` | Promise of the save queue currently in progress |
| `DEFAULT_WEB_CONFIG` | `WebConfig` | Default config template, used for initialization and fallback (the error table's default column order is `DEFAULT_WEB_CONFIG.errors.columns`) |
| `refreshRate` | `number` | Polling refresh interval (milliseconds), the normalized value of `global.refreshInterval`, updated by `setRefreshRate()` |
| `PANEL_SELECTOR_MAP` | `Record<DashboardColumnKey, string>` | Mapping from panel key to CSS selector (`left` → `.left-panel`, etc.) |
| `CARD_TEMPLATES` | `Record<string, string>` | Mapping from card ID to HTML template (`mermaid`, `analysis`, `status`, `progress`, `error-types`, `summary`) |
| `CARD_META` | `Record<string, string>` | Mapping from card ID to i18n label key (including `error-types`) |
| `ALL_CARD_IDS` | `string[]` | List of standard card IDs generated automatically from `Object.keys(CARD_TEMPLATES)` |

## Functions

### `loadWebConfig(): Promise<void>`

Asynchronously loads the config from `GET /api/pull_config`. Falls back to the default config automatically on failure.

---

### `saveWebConfig(): Promise<boolean>`

Persists the current `webConfig` via `POST /api/push_config`. Has an **anti-concurrency** mechanism: if a save is already in progress, reuses the same Promise.

---

### `performSaveWebConfig(): Promise<boolean>`

Performs the actual POST request, pushing the current `webConfig` snapshot to the backend. Concurrency control is handled by `saveWebConfig()`.

---

### `isGroupedWebConfig(config: unknown): boolean`

Detects whether the config object is in the new grouped format (the source identifies it by checking whether the `global`, `errors`, or `injection` sub-objects exist).

---

### `normalizeWebConfig(rawConfig?: Partial<WebConfig> | LegacyWebConfig | null): WebConfig`

Deep-merges the raw config returned by the backend (which may be in the legacy flat format or missing fields) with `DEFAULT_WEB_CONFIG`.

- Automatically detects and migrates the legacy flat config (`LegacyWebConfig`) to the new grouped format.
- Ensures the completeness of `dashboard.layout`.

---

### `normalizeDashboardLayout(layout?: Partial<DashboardLayout>): DashboardLayout`

Ensures the dashboard layout contains all three columns (`left`, `middle`, `right`), falling back to the default card order of `DEFAULT_WEB_CONFIG.dashboard.layout`; keys present in the passed-in `layout` override the defaults.

---

### `normalizeErrorColumns(rawColumns?: ErrorColumnKey[] | null): ErrorColumnKey[]`

Deduplicates and keeps only the error table column order supported by `DEFAULT_WEB_CONFIG.errors.columns`. The returned array can be written directly as `webConfig.errors.columns`.

---

### `normalizeStructureEdgeLabel(value: unknown): StructureEdgeLabel`

Normalizes the structure graph edge label display mode; only accepts `"none"` / `"delta"` / `"cumulative"`, and falls back to `"none"` for other values.

---

### `applyConfig(): void`

Synchronizes the various settings in `webConfig` to the page:

1. **Language**: applies `global.language` and updates all `data-i18n` elements on the page.
2. **Theme**: toggles the `dark-theme` class according to `global.theme`.
3. **Parameter sync**: syncs the refresh rate, history length, page size, structure graph edge label mode, node pending mode, and injection page filter toggle to the corresponding DOM controls.
4. **Error table columns**: reads `errors.columns` (already normalized via `normalizeErrorColumns`) and calls `renderErrorsTableHeader()` to redraw the header.
5. **Layout**: calls `applyDashboardLayout()` to rearrange the cards.

---

### `ensureAllCards(): void`

Executed immediately at module load; iterates over `CARD_TEMPLATES` to create all card DOM nodes and inject them into the `#card-pool` container. It checks whether an element with the corresponding class name already exists to avoid duplicate creation.

---

### `applyDashboardLayout(): void`

Core layout logic: implements dynamic movement of cards between the three column panels via DOM operations (`appendChild`). Strictly follows the order in the config array.

## Default Config Reference

```typescript
const DEFAULT_WEB_CONFIG: WebConfig = {
  global: {
    theme: "light",
    autoRefreshEnabled: true,
    refreshInterval: 5000,
    language: "zh-CN",
  },
  dashboard: {
    historyLimit: 20,
    structureEdgeLabel: "none",
    useTotalPendingInStatus: false,
    layout: {
      left: ["mermaid", "analysis"],
      middle: ["status"],
      right: ["progress", "error-types", "summary"],
    },
  },
  errors: {
    pageSize: 50,
    sortOrder: "newest",
    jumpToInjectionAfterRetry: true,
    columns: ["index", "event_id", "message", "stage", "task", "time", "retry"],
  },
  injection: {
    showInjectableOnly: true,
  },
};
```

## Usage Examples

```typescript
// Read the current config
console.log("Theme:", webConfig.global.theme);
console.log("Refresh interval:", webConfig.global.refreshInterval);
console.log("History length:", webConfig.dashboard.historyLimit);
console.log("Errors per page:", webConfig.errors.pageSize);
console.log("Injection page shows injectable only:", webConfig.injection.showInjectableOnly);

// Modify the config and save it
webConfig.global.theme = "dark";
webConfig.dashboard.historyLimit = 50;
applyConfig();  // apply to the page immediately
const saved = await saveWebConfig();  // persist to the backend

// Automatic migration of the legacy flat config
const legacy = { theme: "dark", refreshInterval: 3000, historyLimit: 10 };
const normalized = normalizeWebConfig(legacy);
// automatically migrated to { global: { theme: "dark", ... }, dashboard: { historyLimit: 10, ... }, ... }
```

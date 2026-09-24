# src/celestialflow_web/static/ts/web_config.ts

> 📅 最終更新日: 2026/09/24

Web フロントエンドの設定の読み込み、正規化、保存、適用を管理します。設定は**グループ構造**（`global`、`dashboard`、`errors`、`injection`）を採用し、同時に旧版のフラット形式の自動マイグレーションにも対応します。

## 型定義

### 現在のグループ設定

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

### 旧版互換型

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

> マイグレーション規則：旧フラット形式の `showStructureEdgeDelta === true` は `structureEdgeLabel: "delta"` にマッピングされ、`false` は `"none"` にマッピングされます。

## グローバル変数

| 変数 | 型 | 説明 |
|------|------|------|
| `webConfig` | `WebConfig` | 現在の実行時設定オブジェクト。モジュール読み込み時に `DEFAULT_WEB_CONFIG` で初期化 |
| `saveConfigPending` | `boolean` | 新たな設定変更がまだディスク書き込み待ちかどうか |
| `saveConfigPromise` | `Promise<boolean> \| null` | 現在実行中の保存キューの Promise |
| `DEFAULT_WEB_CONFIG` | `WebConfig` | デフォルト設定テンプレート。初期化とフォールバックに使用（エラーテーブルのデフォルトフィールド順序は `DEFAULT_WEB_CONFIG.errors.columns`） |
| `refreshRate` | `number` | ポーリングリフレッシュ間隔（ミリ秒）。`global.refreshInterval` の正規化値で、`setRefreshRate()` が更新 |
| `PANEL_SELECTOR_MAP` | `Record<DashboardColumnKey, string>` | パネルキーから CSS セレクタへのマッピング（`left` → `.left-panel` など） |
| `CARD_TEMPLATES` | `Record<string, string>` | カード ID から HTML テンプレートへのマッピング（`mermaid`、`analysis`、`status`、`progress`、`error-types`、`summary`） |
| `CARD_META` | `Record<string, string>` | カード ID から i18n ラベルキーへのマッピング（`error-types` を含む） |
| `ALL_CARD_IDS` | `string[]` | `Object.keys(CARD_TEMPLATES)` から自動生成される標準カード ID リスト |

## 関数

### `loadWebConfig(): Promise<void>`

`GET /api/pull_config` から非同期的に設定を読み込みます。失敗時は自動的にデフォルト設定にフォールバックします。

---

### `saveWebConfig(): Promise<boolean>`

現在の `webConfig` を `POST /api/push_config` 経由で永続化します。**並行防止**機構を備えます：すでに保存が進行中の場合は同じ Promise を再利用します。

---

### `performSaveWebConfig(): Promise<boolean>`

実際の POST リクエストを実行し、現在の `webConfig` スナップショットをバックエンドへプッシュします。並行制御は `saveWebConfig()` が担当します。

---

### `isGroupedWebConfig(config: unknown): boolean`

設定オブジェクトが新しいグループ形式かどうかを検出します（ソースコードでは `global`、`errors`、または `injection` の子オブジェクトが存在するかで識別します）。

---

### `normalizeWebConfig(rawConfig?: Partial<WebConfig> | LegacyWebConfig | null): WebConfig`

バックエンドが返す生の設定（旧版フラット形式や欠落フィールドの可能性がある）と `DEFAULT_WEB_CONFIG` をディープマージします。

- 旧版フラット設定（`LegacyWebConfig`）を自動検出して新しいグループ形式へマイグレーション。
- `dashboard.layout` の完全性を確保。

---

### `normalizeDashboardLayout(layout?: Partial<DashboardLayout>): DashboardLayout`

ダッシュボードレイアウトが 3 カラムすべて（`left`、`middle`、`right`）を含むことを確保し、`DEFAULT_WEB_CONFIG.dashboard.layout` のデフォルトカード順序をフォールバックとし、渡された `layout` に存在するキーはデフォルト値を上書きします。

---

### `normalizeErrorColumns(rawColumns?: ErrorColumnKey[] | null): ErrorColumnKey[]`

重複を排除し、`DEFAULT_WEB_CONFIG.errors.columns` がサポートするエラーテーブルのフィールド順序のみを保持します。返された配列はそのまま `webConfig.errors.columns` として書き込めます。

---

### `normalizeStructureEdgeLabel(value: unknown): StructureEdgeLabel`

構造図の辺ラベル表示モードを正規化します。`"none"` / `"delta"` / `"cumulative"` のみを受け付け、それ以外の値は `"none"` にフォールバックします。

---

### `applyConfig(): void`

`webConfig` 内の各設定をページへ同期します：

1. **言語**: `global.language` を適用し、ページ全体の `data-i18n` 要素を更新。
2. **テーマ**: `global.theme` に応じて `dark-theme` クラスを切り替え。
3. **パラメータ同期**: リフレッシュ率、ヒストリ長、1 ページあたり件数、構造図の辺ラベルモード、ノード待機モード、注入ページのフィルタスイッチなどを対応する DOM コントロールへ同期。
4. **エラーテーブルフィールド**: `errors.columns`（`normalizeErrorColumns` で正規化済み）を読み取り、`renderErrorsTableHeader()` を呼び出してヘッダーを再描画。
5. **レイアウト**: `applyDashboardLayout()` を呼び出してカードを再配置。

---

### `ensureAllCards(): void`

モジュール読み込み時に即座に実行され、`CARD_TEMPLATES` を走査してすべてのカード DOM ノードを作成し `#card-pool` コンテナへ注入します。対応するクラス名の要素がすでに存在するかを確認し、重複作成を避けます。

---

### `applyDashboardLayout(): void`

中核レイアウトロジック：DOM 操作（`appendChild`）を通じてカードを 3 カラムパネル間で動的に移動させます。設定配列の順序に厳密に従います。

## デフォルト設定の参考

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

## 使用例

```typescript
// 現在の設定を読み取る
console.log("テーマ:", webConfig.global.theme);
console.log("リフレッシュ間隔:", webConfig.global.refreshInterval);
console.log("ヒストリ長:", webConfig.dashboard.historyLimit);
console.log("エラー 1 ページ:", webConfig.errors.pageSize);
console.log("注入ページは注入可能のみ表示:", webConfig.injection.showInjectableOnly);

// 設定を変更して保存
webConfig.global.theme = "dark";
webConfig.dashboard.historyLimit = 50;
applyConfig();  // 即座にページへ適用
const saved = await saveWebConfig();  // バックエンドへ永続化

// 旧版フラット設定の自動マイグレーション
const legacy = { theme: "dark", refreshInterval: 3000, historyLimit: 10 };
const normalized = normalizeWebConfig(legacy);
// 自動的に { global: { theme: "dark", ... }, dashboard: { historyLimit: 10, ... }, ... } へマイグレーション
```

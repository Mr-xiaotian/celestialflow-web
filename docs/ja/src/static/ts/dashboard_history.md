# src/celestialflow_web/static/ts/dashboard_history.ts

> 📅 最終更新日: 2026/09/24

ノードの複数指標ヒストリデータの維持管理と、折れ線グラフの初期化・再描画を管理します。ヒストリデータは完全にフロントエンドで状態スナップショットを通じて蓄積され、独立したバックエンド API に依存しません。

## 型定義

```typescript
/** ヒストリグラフで切り替え表示可能な指標フィールドのキー */
type HistoryMetricKey =
  | "tasks_processed"
  | "tasks_succeeded"
  | "tasks_failed"
  | "tasks_duplicated"
  | "tasks_pending"
  | "total_tasks_pending"
  | "delta_tasks_processed"
  | "delta_tasks_succeeded"
  | "delta_tasks_failed"
  | "delta_tasks_duplicated";

/** ある時刻における単一ノードのヒストリサンプル点 */
type NodeHistoryPoint = {
  timestamp: number;
  tasks_processed: number;
  tasks_succeeded: number;
  tasks_failed: number;
  tasks_duplicated: number;
  tasks_pending: number;
  total_tasks_pending: number;
};

  type NodeHistory = NodeHistoryPoint[];

type ThemeColors = {
  text: string;   // 座標軸と凡例の文字色
  grid: string;   // グリッド線の色
  border: string; // 座標軸の枠線色
};
```

## グローバル変数

| 変数 | 型 | 説明 |
|------|------|------|
| `nodeHistories` | `Record<string, NodeHistory>` | 各ノードがローカルで管理するヒストリデータ系列 |
| `progressChart` | `ChartInstance \| null` | Chart.js 折れ線グラフインスタンス |
| `hiddenNodes` | `Set<string>` | ユーザーが凡例で手動で非表示にしたノードの集合（ページのライフサイクル内でのみ保持され、**永続化されない**） |
| `currentHistoryMetric` | `HistoryMetricKey` | 現在チャートに表示する指標。デフォルトは `"tasks_processed"` |
| `metricDots` | `NodeListOf<HTMLLabelElement>` | すべての `.metric-dot` ラベル要素。指標表示の切り替えに使用 |

## 補助関数

### `getColor(index: number): string`

インデックスに応じて CSS 変数から定義済みテーマ色を読み取り、異なるノードの折れ線を区別します。9 色を循環して剰余で使用します。

| Index | CSS 変数 | 説明 |
|-------|---------|------|
| 0 | `--cornflower-500` | コーンフラワーブルー |
| 1 | `--jade-500` | ジェイドグリーン |
| 2 | `--marigold-500` | マリーゴールドイエロー |
| 3 | `--crimson-500` | クリムゾン |
| 4 | `--violet-500` | バイオレット |
| 5 | `--rose-500` | ローズレッド |
| 6 | `--jade-400` | ジェイドグリーン（淡） |
| 7 | `--sky-500` | スカイブルー |
| 8 | `--amber-500` | アンバーオレンジ |

### `getHistoryMetricLabelKey(metric: HistoryMetricKey): string`

`HistoryMetricKey` を国際化翻訳キーにマッピングします。

| 入力 | 出力 |
|------|------|
| `tasks_processed` | `chart.metric.processed` |
| `tasks_succeeded` | `chart.metric.succeeded` |
| `tasks_failed` | `chart.metric.failed` |
| `tasks_duplicated` | `chart.metric.duplicated` |
| `tasks_pending` | `chart.metric.pending` |
| `total_tasks_pending` | `chart.metric.pendingGlobal` |
| `delta_tasks_processed` | `chart.metric.deltaProcessed` |
| `delta_tasks_succeeded` | `chart.metric.deltaSucceeded` |
| `delta_tasks_failed` | `chart.metric.deltaFailed` |
| `delta_tasks_duplicated` | `chart.metric.deltaDuplicated` |

### `updateHistoryMetricButtons(): void`

`metricDots` を走査し、`currentHistoryMetric` に基づいて一致する `<label>` に `.active` クラスを追加し、それ以外からは削除します。

### `updateChartAxisLabels(): void`

折れ線グラフの X/Y 軸タイトルテキストを更新し、それぞれ現在の言語の「時間」と対応する指標名にマッピングします。

---

## 中核ロジック関数

### `initHistoryChart(): void`

Chart.js 折れ線グラフインスタンスを初期化（または再構築）します。

- 既存インスタンスがある場合は、先に `destroy()` を呼び出して破棄
- `getChartThemeColors()` を呼び出して現在のテーマの文字色、グリッド色、軸線色を読み取る
- 凡例のクリックイベントを設定：ノードの表示/非表示を切り替え、`hiddenNodes` Set に同期
- **アニメーションを無効化**（`animation: false`）してリアルタイム更新の性能を向上
- インタラクションモードは `index`、`intersect: false`

### `updateChartTheme(): void`

折れ線グラフの配色（文字色、グリッド線色、軸線色）を更新します。テーマ切り替え後に呼び出し、インスタンスの再構築は不要です。

### `updateChartData(): void`

`currentHistoryMetric` に基づいて `extractProgressData()` を呼び出し、`nodeHistories` の対応する指標データを折れ線グラフに書き込んで更新します。`legendItem.hidden` を同期し、凡例のレンダリングが `hiddenNodes` と一致するようにします。

### `appendStatusSnapshotToHistory(timestamp, statuses, estimates, previousStatuses = {}): boolean`

中核ロジック：最新の状態スナップショットに基づいてヒストリ点を追加します。`estimates` は `statuses` と同じサイクルのグラフレベル派生値（`total_tasks_pending` の記録に使用）で、`previousStatuses` はノードの再起動の識別に使用します。

- **リセット検出**：ノードの `start_time` が変化（再起動）した場合、または `tasks_processed` が後退（ロールバック）した場合、そのノードのヒストリをクリアします。
- **重複排除**：タイムスタンプが同じ場合は最後の点を更新し、そうでなければ新しい点を追加します。
- **トリミング**：すべての変更は `getCurrentHistoryLimit()` の制約を受けます。
- **戻り値**: `boolean` — ヒストリデータが変化したかどうか。

### `extractProgressData(histories, metric): Record<string, Array<{x: number; y: number}>>`

ローカルで管理する `nodeHistories` マップを Chart.js 互換の `{x, y}` 座標点配列に変換します。

- **累積モード**: サンプル点の生のフィールド値を直接読み取ります。
- **増分モード（delta）**: `metric` が `delta_` で始まる場合、隣接するサンプル点の差分／時間差を計算して毎秒レートを求めます。最初の点は `y = 0` に固定します。

### `trimNodeHistories(): boolean`

`webConfig.dashboard.historyLimit` に基づいてフロントエンドがローカルで管理するヒストリ点の数をトリミングします。戻り値のブール値はヒストリデータが変化したかどうかを示します。

### `getCurrentHistoryLimit(): number`

現在のヒストリ曲線の保持点数制限を取得します。`webConfig.dashboard.historyLimit` を優先し、無効な場合はデフォルトで `20` を返します。

### `getChartThemeColors(): ThemeColors`

CSS 変数から現在のテーマ（ダーク／ライト）におけるチャートの文字、グリッド線、枠線の色を読み取ります。

| テーマ | 文字色 | グリッド色 | 枠線色 |
|------|--------|--------|--------|
| ライト | `--carbon-900` | `--carbon-200` | `--carbon-300` |
| ダーク | `--carbon-200` | `--carbon-600` | `--carbon-500` |

---

## 指標切り替えスイッチャ（モジュールレベルで自動実行）

```typescript
function initHistoryMetricSwitcher() { ... }
initHistoryMetricSwitcher(); // モジュールレベルで即時実行
```

`initHistoryMetricSwitcher()` はモジュールスコープで自動的に呼び出され、**`main.ts` から能動的に呼び出されることはありません**。これは以下を担当します：

1. `metricDots` ボタンのアクティブスタイルを同期
2. クリックイベントをバインドし、`currentHistoryMetric` を切り替えた後に軸タイトルを更新して再描画

## データフロー

```mermaid
flowchart LR
    subgraph "loaders.ts"
        LS[loadStatuses]
    end
    subgraph "dashboard_history.ts"
        AS[appendStatusSnapshotToHistory]
        NH[nodeHistories]
        EC[extractProgressData]
        UC[updateChartData]
        CH[Chart.js インスタンス]
    end
    LS -->|timestamp + statuses| AS
    AS --> NH
    NH --> EC
    EC -->|{x, y} 座標| UC
    UC --> CH
```

## 使用例

```typescript
// 手動でヒストリデータを構築してレンダリング
const mockHistory: Record<string, NodeHistory> = {
  "Processor": [
    { timestamp: 1000, tasks_processed: 10, tasks_succeeded: 9, tasks_failed: 1, tasks_duplicated: 0, tasks_pending: 90, total_tasks_pending: 120 },
    { timestamp: 1005, tasks_processed: 25, tasks_succeeded: 23, tasks_failed: 1, tasks_duplicated: 1, tasks_pending: 75, total_tasks_pending: 105 },
  ],
};

// nodeHistories = mockHistory;
// currentHistoryMetric = "tasks_succeeded";
// updateChartData();  // 折れ線グラフへレンダリング

// テーマ切り替え後にチャートの色を更新
// updateChartTheme();

// 手動でヒストリデータをトリミング
// webConfig.dashboard.historyLimit = 10;
// if (trimNodeHistories()) updateChartData();
```

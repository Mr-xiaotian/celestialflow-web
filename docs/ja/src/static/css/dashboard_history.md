# src/celestialflow_web/static/css/dashboard_history.css

> 📅 最終更新日: 2026/09/24

ノード指標履歴グラフ（Chart.js）の上方にあるコントロール領域のスタイルを担当し、指標切り替えボタングループを含みます。


## レイアウト設計 (`.progress-card-header`)

- **構造**: `flex` レイアウトを採用し、左側にカードタイトル、右側に指標切り替え器を表示します。
- **適応性**: `flex-wrap: wrap` を有効にし、狭い画面では自動的に折り返します。

## 指標切り替え器 (`.metric-indicators`)

- **コンテナ**: `flex` レイアウト、`flex-wrap: wrap`、中央揃え、`gap: 1rem`。
- **切り替えボタン (`.metric-dot`)**:
  - 各ボタンは色の円点（`.dot`）と文字ラベル（`.label`）を含みます。
  - **デフォルト状態**: `opacity: 0.55`。選択されていない指標を弱めます。
  - **ホバー状態**: `opacity: 0.8`。
  - **アクティブ状態 (`.active`)**: `opacity: 1`、薄いグレー背景（`--carbon-100`）、ダークモードでは `--carbon-700`。
  - **トレンド指標 (`.dot.delta`)**: 中空円（`background: transparent`、枠線のみ着色）。増分類の指標と累積類の指標を区別するために使用します。
- **区切り線 (`.metric-sep`)**: `1px` 幅の縦線で、累積指標グループとトレンド指標グループを区切るために使用します。

## 関連モジュール

- 実際の折れ線グラフは `dashboard_history.ts` が Chart.js と連携して canvas にレンダリングし、その内部の色（文字、軸線）は TS コード内で CSS 変数を読み取り、Chart.js インスタンスに設定されます。
- 指標の切り替えは `initHistoryMetricSwitcher()` によって自動的にバインドされます（モジュールレベルの実行）。

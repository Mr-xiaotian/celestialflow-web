# src/celestialflow_web/static/css/base.css

> 📅 最終更新日: 2026/09/24

システムのグローバルな基本スタイル、ダークモード切り替え、汎用コンポーネント（カード、タブ、バッジ）、レスポンシブな基本レイアウト、およびカードレイアウトエディタのモーダルウィンドウのスタイルを担当します。

## グローバル基本

- **リセット**: ボックスモデル（`border-box`）を統一し、デフォルトのフォントシーケンスを設定します。
- **背景と色**: ライトモード（`--carbon-50`）とダークモード（`--carbon-900`）における body の背景色を定義します。
- **コンテナ**: `.container` はコンテンツの最大幅を `1200px` に制限し、水平方向に中央揃えにします。

## コアコンポーネントのスタイル

### ヘッダーとナビゲーション (`header`)
- **コントロールパネル (`.control-panel`)**: 更新間隔の選択、設定ギア、テーマ切り替えボタンを含みます。内部の設定以外のボタンは、ダークモードでは統一してカーボン色の背景と枠線を使用します。
- **更新コントロールコンテナ (`.refresh-container`)**: 更新間隔ラベルとドロップダウンセレクタを水平に並べ、`gap: 0.5rem` とします。
- **設定ボタン (`.btn-settings`)**: 透明な背景、枠線なしで、ホバーと `focus-visible` のフィードバックを備え、ダークモードに対応します。
- **設定パネル (`.settings-panel`)**: ギアの下方に絶対配置で浮かぶ、角丸の白背景カードで、ダークモードでは `--carbon-800` 背景を使用します。子要素には以下が含まれます:
  - `.settings-header`: ヘッダー。タイトルと閉じるボタンを左右に配置し、下部に区切り線があります。
  - `.settings-title`: タイトル文字。`0.85rem`、`font-weight: 600`。
  - `.settings-close`: 閉じるボタン。透明な背景で、ホバー時に色が変わります。
  - `.settings-body`: 本体コンテンツのコンテナ。`padding: 0.5rem 0.75rem`。
  - `.settings-status`: 状態提示エリア。上部の枠線で区切り、`0.75rem`。
  - `.settings-status-success` / `.settings-status-error`: 成功/失敗の文字色。
  - `.settings-item`: 単一の設定項目。`grid` でラベルとセレクタを配置します。
  - `.settings-toggle`: トグルのチェックボックス。右揃え。
  - `.settings-divider` / `.settings-divider-label`: グループの区切り線とラベル。
  - `.settings-empty`: 空状態の提示。中央揃えのグレー文字。
  - `.settings-item-center`: 中央揃えの設定項目。操作ボタンによく使用されます。
- **テーマ切り替えボタン (`#theme-toggle`)**: ヘッダー右側に絶対配置される角丸の長方形ボタンで、ホバー時に色が変わります。狭い画面では `@media (max-width: 2048px)` 内で `position: static`、`order: 3` に変更されます。

### タブシステム (`.tabs`)
- 横に並ぶタブナビゲーションを実装し、`.active` クラスで現在選択中のモジュール（ダッシュボード、エラーログ、タスク注入）をハイライトします。

### 汎用カード (`.card`)
- 統一された背景の角丸（`1rem`）と影の効果を持ちます。
- **ホバーフィードバック**: ホバー時にわずかに上方向へ移動します（`translateY(-2px)`）。

## 補助クラス名

- **色クラス**: `.text-success` (緑)、`.text-error` (赤)、`.text-pending` (灰)、`.text-duplicate` (橙) などの素早い着色クラスを提供します。
- **増分類**: `.text-delta-*` シリーズは、ダッシュボードでより淡い指標変化値を表示するために使用します。
- **非表示**: `.hidden` クラスは JS で要素の表示/非表示を素早く制御するために使用します。
- **小サイズフォント**: `.text-sm` は `font-size: 0.75rem` を設定します。
- **カーボン色テキスト**: `.text-carbon` は `--carbon-400` で着色します。

## 空プレースホルダー (`.empty-placeholder`)

データが空の際に使用する中央揃えのテキストプレースホルダーで、デフォルトでは `text-align: center`、`color: --carbon-400`、`padding: 2rem`、`font-size: 1rem` となり、ダークモードでは色が淡くなります。

## 汎用ヒントエリア (`.tip-section`)

ページをまたいで再利用される説明的なヒントバーで、左側にテーマ色の枠線があります:

| セレクタ | 説明 |
|--------|------|
| `.tip-section` | ヒントバーのコンテナ。`--cornflower-50` 背景、左側に `4px` の実線枠線、`border-radius` は右側のみ角丸 |
| `.tip-content` | 内部は水平 flex レイアウトで、アイコンとテキストを中央揃えに配置 |
| `.tip-icon` | ヒントアイコン。`1.25rem` の正方形、`color: --cornflower-500`、右側に `0.75rem` の余白 |
| `.tip-text` | ヒント本文。`0.75rem`、ライトでは `--cornflower-600` / ダークでは `--carbon-300` |

## モーダルオーバーレイ (`.overlay`)

- **`.overlay`**: 固定配置の全画面半透明黒オーバーレイ（`rgba(0,0,0,0.4)`）、`z-index: 200`、中央揃えのフレックスレイアウトで、カードレイアウトエディタなどのモーダルウィンドウを載せるために使用します。
- **`.overlay.hidden`**: オーバーレイを `display: none` にし、JS と連携してポップアップの表示/非表示を制御します。

## カードレイアウトエディタ (`.layout-editor` シリーズ)

カードレイアウトエディタはモーダルウィンドウの形でオーバーレイの上に浮かび、三列ダッシュボードカードのドラッグによる並べ替えをサポートします。主な子セレクタ:

| セレクタ | 説明 |
|--------|------|
| `.layout-editor` | エディタのメインコンテナ: 角丸の白背景カード、`max-width: 700px`、縦方向 flex レイアウト |
| `.dark-theme .layout-editor` | ダークモードでは `--carbon-800` 背景を使用 |
| `.layout-editor-header` | タイトルバー: 左右に配置し、タイトルは左、閉じるボタンは右 |
| `.layout-editor-title` | タイトル文字: `1.1rem`、`font-weight: 600` |
| `.layout-editor-columns` | 三列グリッドレイアウトエリア: `grid-template-columns: repeat(3, 1fr)`、縦方向にスクロール可能 |
| `.layout-column` | 単一カラムのコンテナ: 縦方向 flex カラム |
| `.layout-column-header` | カラムタイトル: 中央揃え、下線区切り、小サイズフォント |
| `.layout-column-dropzone` | ドラッグ＆ドロップの配置エリア: 破線枠線、最小高さ `120px`、縦方向 flex でカードを配置 |
| `.layout-column-dropzone.drag-over` | ドラッグホバー時のハイライト: 青い枠線 + 薄い青の背景 |
| `.layout-card` | ドラッグ可能なカード項目: グレー背景の角丸、`cursor: grab`、`user-select: none` |
| `.layout-card:hover` | ホバー時に浮き上がる影の効果 |
| `.layout-card.dragging` | ドラッグ中は半透明（`opacity: 0.5`） |
| `.layout-card-name` | カード名の文字: `0.8rem`、`font-weight: 500` |
| `.layout-card-handle` | ドラッグハンドル: ⠿ 文字、`color: --carbon-400` |
| `.layout-unused` | 未使用カードプールのエリア: 三列の下方に位置 |
| `.layout-unused-header` | 未使用プールのタイトル: `0.75rem`、グレー |
| `.layout-unused .layout-column-dropzone` | 未使用プールの配置エリア: 横並び（`flex-direction: row`）、最小高さ `40px` |
| `.layout-editor-footer` | 下部ボタンバー: 右揃え、上部に区切り線 |
| `.btn-layout-save` | 保存ボタン: 青い塗りつぶし、幅 `80%` を占める |
| `.btn-layout-reset` | リセットボタン: グレーの輪郭線、幅 `20%` を占める |
| `.btn-layout-editor` | 設定パネル内の入口ボタン: 青い塗りつぶし、角丸 |
| `.error-columns-shell` | エラーログページのフィールドエディタの二列グリッドコンテナ（`grid-template-columns: repeat(2, minmax(0, 1fr))`） |
| `.error-columns-editor` | エラーログページのフィールドエディタ内のスタイル上書き: 下部ボタンを `auto` 幅かつ `min-width: 7rem` に変更。配置エリアは `min-height: 16rem` |
| `.dark-theme .btn-layout-save` / `.dark-theme .btn-layout-reset` | 上記二つのボタンのダークモードにおける統一された暗色スタイル（`--carbon-700` 背景、`--carbon-200` 文字、`--carbon-600` 枠線） |

## レスポンシブルール

### `@media (max-width: 2048px)`

ビューポート幅が ≤ 2048px のときに以下の調整が発動します:
- `h1` タイトル幅を `100%` に設定し、長いタイトルのオーバーフローを防止
- `#theme-toggle` テーマ切り替えボタンを `position: static`、`order: 3` に変更し、狭い画面でのコントロールバーの再配置に対応
- `.error-columns-shell` を単一カラム（`grid-template-columns: 1fr`）に切り替え、エラーログページのフィールドエディタの狭い画面での単一カラム表示に対応
- `.settings-panel` を上部 `4rem` の位置に中央揃えで固定配置するポップアップ層に変更（モバイル端末の全幅対応）

## ダークモード対応

`.dark-theme` クラスをルートノードの識別子として採用します。このモードでは、システムが以下の属性を自動的に調整します:
- 背景色とメインの文字色。
- カードおよび設定パネルの背景と枠線の色。
- フォームコントロール（select, button）の背景と枠線。
- 一部の意味論的な文字色（pending 状態の文字色など）。

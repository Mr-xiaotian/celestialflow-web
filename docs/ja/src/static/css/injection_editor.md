# src/celestialflow_web/static/css/injection_editor.css

> 📅 最終更新日: 2026/09/24

タスク注入ページ右側のエディタのスタイル定義を担当し、JSON 入力領域、検証メッセージ、操作ボタングループを含みます。


## エディタコンテナ (`.injection-editor-card`)

- 縦方向 flex レイアウトを採用し、固定間隔 `gap: 1rem` とします。

## エディタヘッダー (`.editor-header`)

- **レイアウト**: `flex` で左右に配置し、左側は説明文 + 現在のノード情報、右側は操作ボタングループです。
- `.editor-node-meta`: 狭い幅で収縮することを許可します（`min-width: 0`）。
- `.editor-caption`: 「現在のノード」タイトルの上方にある小型の説明文。`0.75rem`、グレー調（`--carbon-500`）。

## 現在のノード情報 (`.editor-node-row`)

- ノード名と右側の「編集済み」ラベルの行レイアウトで、`flex-wrap: wrap` に対応します。
- `.current-node-name`: 現在選択中のノード名。`1rem`、`font-weight: 600`。

## ボタンのスタイル (`.btn-small`, `.btn-select`, `.btn-clear`)

| セレクタ | 用途 | 背景色 | 文字色 |
|--------|------|--------|--------|
| `.btn-small` | 汎用小ボタン | — | — |
| `.btn-select` | 検証/フォーマットボタン | `--cornflower-50`（ライト）/ `--cornflower-700`（ダーク） | `--cornflower-700`（ライト）/ `--carbon-100`（ダーク） |
| `.btn-clear` | 下書きクリアボタン | `--carbon-100`（ライト）/ `--carbon-600`（ダーク） | `--carbon-700`（ライト）/ `--carbon-100`（ダーク） |

- **無効状態**: `opacity: 0.6`、`cursor: not-allowed`。

## JSON 入力エリア (`.json-input-section`)

- **JSON ヘッダー (`.json-header`)**: ラベルを左寄せにした上部の行。
- **JSON ラベル (`.json-label`)**: `0.75rem`、`font-weight: 500`。
- **JSON 編集ボックス (`.json-textarea`)**:
  - 等幅フォント（`Monaco, Menlo, monospace`）、`min-height: 20rem`、縦方向のリサイズに対応。
  - フォーカス時に枠線が `--cornflower-400` に変わります。
  - 無効状態: `--carbon-50` 背景、`--carbon-400` 文字。

## 検証メッセージ (`.validation-message`)

| 状態 | CSS クラス | 色 |
|------|--------|------|
| 成功 | `.validation-success` | `--jade-600`（ライト）/ `--jade-400`（ダーク） |
| 失敗 | `.validation-error` | `--crimson-600`（ライト）/ `--crimson-400`（ダーク） |
| 中性 | `.validation-neutral` | `--carbon-500`（ライト）/ `--carbon-400`（ダーク） |

- `min-height: 1.25rem`、`font-size: 0.75rem`、JSON 編集ボックスの下方に位置します。

## エディタ下部ボタングループ (`.editor-actions`)

- `flex` レイアウト、`gap: 0.75rem`、`flex-wrap: wrap`。

## 関連モジュール

- インタラクションのロジックは `injection.ts` 内の `renderCurrentNodeEditor()`、`validateCurrentDraft()`、`formatCurrentDraft()` などの関数によって駆動されます。

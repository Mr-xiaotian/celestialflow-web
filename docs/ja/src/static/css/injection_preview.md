# src/celestialflow_web/static/css/injection_preview.css

> 📅 最終更新日: 2026/09/24

タスク注入ページ下部の下書きプレビューエリア、送信ボタン、状態メッセージ、およびローディングアニメーションのスタイル定義を担当します。


## 下書きプレビューカード (`.draft-card`)

- 縦方向 flex レイアウト、`gap: 0.75rem`、`margin-bottom: 1rem`。
- 編集済みのすべての下書きを集約して表示するエリアとして機能します。

## 下書きプレビューエリア (`.draft-preview`)

- **読み取り専用スタイル**: `margin: 0`、`padding: 1rem`、入力状態なし。
- **等幅フォント**: `Monaco, Menlo, monospace`、`font-size: 0.75rem`。
- **背景**: ライトモード `--carbon-50`、ダークモード `--carbon-800`。
- **オーバーフロー**: `overflow: auto`、長いコンテンツのスクロールに対応。
- **最小高さ**: `min-height: 12rem`。

## 空状態プレースホルダー (`.empty-placeholder`)

- 下書きがないときに表示され、等幅フォントのスタイルです。

## 送信ブロック (`.submit-section`)

- `flex` レイアウト、左右に配置（状態提示 + 送信ボタン）、`gap: 1rem`、`margin-top: auto`。

## 状態メッセージ (`.status-message`)

- `flex` レイアウト、`align-items: center`、`font-weight: 500`。

| CSS クラス | 説明 | 色 |
|--------|------|------|
| `.status-success` | 送信成功 | `--jade-600`（ライト）/ `--jade-400`（ダーク） |
| `.status-error` | 送信失敗 | `--crimson-600`（ライト）/ `--crimson-400`（ダーク） |

- **状態アイコン (`.status-icon`)**: `1.25rem`、右マージン `0.5rem`、SVG インラインアイコン用に確保します。

## 送信ボタン (`.btn-submit`)

- **基本スタイル**: 青い塗りつぶし（`--cornflower-500`）、白い文字、角丸 `0.5rem`、影付き。
- **ホバー効果**: 背景が濃くなり（`--cornflower-600`）、わずかに上へ移動 `-1px`。
- **無効状態**: `--carbon-400` 背景、`cursor: not-allowed`、影なし・移動なし。
- **ダークモード**: 背景 `--cornflower-600`、無効状態 `--carbon-500`。

## ローディングインジケータ (`.spinner`)

```css
.spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid var(--frost-0);
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: injection-spin 1s linear infinite;
}
```

- 送信中に送信ボタン内部へ動的に挿入され、白い円環 + 透明な上部による回転効果を表します。

## 回転アニメーション (`@keyframes injection-spin`)

```css
@keyframes injection-spin {
  0%   { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

## 関連モジュール

- 下書きプレビューは `injection.ts` 内の `renderDraftList()` によって動的にレンダリングされます。
- 送信インタラクションは `handleSubmit()` によって駆動されます（ボタンのローディング状態の切り替え、状態メッセージの表示）。
- 送信ボタンの可用性は `updateSubmitButtonAvailability()` によって制御されます。

# src/celestialflow_web/static/css/injection_layout.css

> 📅 最終更新日: 2026/09/24

タスク注入ページの検索フィルター、二列レイアウト、およびレスポンシブブレークポイントのスタイルを担当します。


## 二列レイアウト (`.card-grid`)

```css
.card-grid {
  display: grid;
  grid-template-columns: minmax(18rem, 22rem) minmax(0, 1fr);
  gap: 1.5rem;
}
```

- 左側のノードリストは 18–22rem に固定し、右側のエディタは残りの幅に適応します。

## 検索フィルター

- **検索コンテナ (`.search-container`)**: 相対配置で、検索アイコンを載せるために使用します。
- **検索入力ボックス (`.search-input`)**:
  - 左側の内側余白 `2.5rem` は検索アイコンのためのスペースです。
  - フォーカス時に枠線色が `--cornflower-400` に切り替わります。
  - ダークモード: `--carbon-700` 背景。
- **検索アイコン (`.search-icon`)**: 入力ボックスの左側に絶対配置。`1rem`、`color: --carbon-400`。

## 注入可能ノードのトグル (`.injectable-toggle`)

- `flex` レイアウト、`gap: 0.5rem`、`font-size: 0.75rem`。
- 検索ボックスの下方、ノードリストの上方に位置します。

## レスポンシブ (`@media (max-width: 2048px)`)

狭い画面（≤2048px）では:
- `.card-grid` が単一カラムに切り替わります（`grid-template-columns: 1fr`）。
- `.node-list` の `max-height` 制限が解除されます。
- `.editor-header` と `.submit-section` が縦方向の積み重ねに切り替わります。
- `.editor-actions` が縦方向の並びに切り替わります。

## 関連モジュール

- レイアウト構造は `injection.ts` 内の `renderInjectionPage()` によって動的に埋め込まれます。
- 検索とフィルターのイベントは `setupEventListeners()` によってバインドされます。

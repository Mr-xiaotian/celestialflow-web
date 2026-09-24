# src/celestialflow_web/static/css/injection_nodes.css

> 📅 最終更新日: 2026/09/24

タスク注入ページ左側のノード閲覧リストのスタイル定義を担当し、ノード項目、選択状態、無効状態、「編集済み」ラベルを含みます。


## ノードリストコンテナ (`.node-list`)

- 縦方向 flex レイアウト、`gap: 0.5rem`。
- `max-height: 30rem`、超過時は縦方向にスクロール（`overflow-y: auto`）。

## ノード項目 (`.node-item`)

- **レイアウト**: `flex` で左右に配置（ノード情報 + 右側のラベル）、`gap: 0.75rem`。
- **基本スタイル**: 角丸 `0.75rem`、枠線 `1px solid --carbon-200`。
- **ホバー効果**: 背景が淡くなり（`--carbon-50`）、枠線が青くなり（`--cornflower-300`）、わずかに上へ移動 `-1px`。
- **ダークモード**: 背景 `--carbon-700`、ホバー時は `--carbon-600`。

| CSS クラス | 説明 |
|--------|------|
| `.node-item` | 基本的なノード項目のスタイル |
| `.node-item.active-node` | 現在選択中のノード: 青い枠線（`--cornflower-500`）+ 薄い青の背景（`--cornflower-50`） |
| `.disabled-node` | 注入不可のノード: `opacity: 0.55`、`cursor: not-allowed`、`pointer-events: none` |

## ノード情報エリア (`.node-info`)

- `min-width: 0`、`flex: 1`。狭い空間でテキストが収縮することを許可します。

## ノード名 (`.node-name`)

- `font-weight: 600`、`word-break: break-all`。
- ライトモード `--carbon-800`、ダークモード `--carbon-100`。

## 「編集済み」ラベル (`.node-side-tag`)

- `inline-flex`、`flex-shrink: 0`。
- カプセル形（`border-radius: 999px`）、小型の内側余白。
- ライトモード: 青い背景（`--cornflower-100`）+ 青い文字（`--cornflower-700`）。
- ダークモード: 濃い青の背景（`--cornflower-800`）+ 薄い青の文字（`--cornflower-100`）。

## 関連モジュール

- ノードリストは `injection.ts` 内の `renderNodeList()` によって動的にレンダリングされます。
- 選択ロジックは `selectNode()` によって駆動され、`.active-node` クラスの切り替えによってハイライトを実現します。
- 「注入可能なノードのみ表示」トグルのフィルターロジックは `isInjectableNode()` を参照してください。

# src/celestialflow_web/static/ts/layout_editor.ts

> 📅 最終更新日: 2026/09/24

## 役割

`layout_editor.ts` はダッシュボードの**カードレイアウトエディタ**のフロントエンドモジュールです。フローティングウィンドウ（overlay）内にドラッグ＆ドロップ式のインターフェースを提供し、ユーザーがダッシュボードの左・中・右の 3 カラムそれぞれに含めるカードを自由に調整でき、その結果を `config.json` に永続化します。

エディタは [SortableJS](https://sortablejs.github.io/Sortable/) を使用して領域をまたぐドラッグ並び替えを実現し、3 カラムと「未使用カードプール」の間で相互に移動できます。

---

## グローバル定数と状態

### `DEFAULT_WEB_CONFIG.dashboard.layout`（`web_config.ts` 由来）

デフォルトの 3 カラムカードレイアウト設定で、システム出荷時のカード割り当て方案を定義します（`resetLayout()` が使用）：

```javascript
{
  left:   ["mermaid", "analysis"],
  middle: ["status"],
  right:  ["progress", "error-types", "summary"],
}
```

### `originalLayout`

layout エディタを開いたときに保存されるレイアウトスナップショット（`{ left, middle, right }`）。閉じるときに `restore=true` の場合、未保存のドラッグ変更を復元するために使用します。

| カラム | デフォルトカード | 説明 |
|------|----------|------|
| `left` | mermaid, analysis | グラフレンダリング＋トポロジ分析 |
| `middle` | status | ノード状態テーブル |
| `right` | progress, error-types, summary | 進捗＋エラータイプ分布＋全体サマリ |

---

## 中核関数

### `renderCard(cardId: string): HTMLElement`

ドラッグ可能なカード DOM 要素を 1 つ作成します。

| 引数 | 型 | 説明 |
|------|------|------|
| `cardId` | `string` | カード識別子（例：`"mermaid"`、`"status"`） |

**戻り値：** `.layout-card` CSS クラスを持ち、`data-card-id` 属性とドラッグハンドルを保持する `<div>` 要素。

```html
<div class="layout-card" data-card-id="mermaid">
  <span class="layout-card-name">グラフレンダリング</span>
  <span class="layout-card-handle" aria-hidden="true">⠿</span>
</div>
```

カード名は `CARD_META[cardId]` からローカライズされた表示名を検索し、見つからない場合は元の `cardId` にフォールバックします。

---

### `openLayoutEditor()`

レイアウトエディタを開き、現在のレイアウトをレンダリングします。

**フロー：**

```
┌───────────────────────────────────────┐
│  1. overlay を表示                    │
│  2. webConfig.dashboard.layout を読む │
│  3. コピーを originalLayout に保存    │
│  4. 左/中/右の 3 カラムをレンダリング │
│  5. 未使用カードプールをレンダリング  │
│  6. initSortable() を呼び出してドラッグを有効化 │
└───────────────────────────────────────┘
```

未使用カードプールには、`ALL_CARD_IDS` のうち 3 カラムから参照されていないすべてのカードが含まれます。

---

### `closeLayoutEditor(restore: boolean = true)`

レイアウトエディタを閉じます。

| 引数 | 型 | デフォルト値 | 説明 |
|------|------|--------|------|
| `restore` | `boolean` | `true` | 元のレイアウトを復元するか。`true` のとき未保存のドラッグ変更をすべて取り消し、`false` のとき現在のメモリ状態を保持 |

**動作：**
- `restore=true`（デフォルト）：`originalLayout` で `webConfig.dashboard.layout` を上書きし、`applyConfig()` を呼び出してダッシュボードを更新します。これは閉じるボタンをクリックしたとき、またはオーバーレイをクリックしたときの動作です。
- `restore=false`：overlay を非表示にしますがデータは復元しません。これは保存成功後に呼び出される動作です。

---

### `initSortable()`

SortableJS を初期化し、4 つのドロップ領域で領域をまたぐドラッグを有効化します。

**対象となる領域：**

| ID | 説明 |
|----|------|
| `layout-dropzone-left` | 左カラムのドロップ領域 |
| `layout-dropzone-middle` | 中カラムのドロップ領域 |
| `layout-dropzone-right` | 右カラムのドロップ領域 |
| `layout-dropzone-unused` | 未使用カードプール |

**SortableJS 設定：**

| 設定項目 | 値 | 説明 |
|--------|-----|------|
| `group` | `"dashboard-layout"` | 共有グループ名。4 つの領域間で相互にドラッグ可能 |
| `animation` | `150` | ドラッグアニメーションの時間（ms） |
| `ghostClass` | `"dragging"` | ドラッグ中のプレースホルダ CSS クラス |
| `dragClass` | `"dragging"` | ドラッグ中のカード自体の CSS クラス |

---

### `destroySortableInstances(): void`

ドラッグ領域を再描画する前に、現在マウントされているすべての Sortable インスタンスを破棄し、リスナーの重複とインスタンスリークを防ぎます。

---

### `syncLayout()`

DOM 上の現在の 3 カラムカード順序を `webConfig.dashboard` に同期して書き戻します。

**フロー：**
1. `left`、`middle`、`right` の 3 つのドロップ領域を走査
2. 各領域の `.layout-card` 要素から `data-card-id` を読み取る
3. 順序配列として `webConfig.dashboard.layout` に書き込む

> この関数は**永続化しません**。メモリ構造を更新するだけです。永続化は `saveLayout()` が呼び出します。

---

### `saveLayout()`

レイアウトを保存してダッシュボードを更新します。

**フロー：**

```
┌───────────────────────────────────┐
│  1. syncLayout()                  │
│  2. await saveWebConfig()         │
│     ├─ 成功 → applyConfig()       │
│     │         closeLayoutEditor(false)
│     └─ 失敗 → 保存失敗の通知を表示 │
└───────────────────────────────────┘
```

`saveWebConfig()` は `webConfig` を `POST /api/push_config` 経由で `config.json` に永続化します。

---

### `resetLayout()`

レイアウトをデフォルトにリセットします。

**フロー：**

1. `webConfig.dashboard.layout` を `DEFAULT_WEB_CONFIG.dashboard.layout` のディープコピーにリセット
2. 左・中・右の 3 カラムをクリアして再レンダリング（デフォルトのカード順序に従う）
3. 未使用カードプールをクリアして再計算
4. 再度 `initSortable()` を呼び出してドラッグをバインド

> この操作は**自動保存されません**。ユーザーが保存ボタンをクリックして初めて永続化されます。

---

## イベントバインディング

モジュールは `DOMContentLoaded` 時に以下のイベントをバインドします：

| 対象要素 | イベント | ハンドラ関数 |
|----------|------|----------|
| `#open-layout-editor` | `click` | `openLayoutEditor()` |
| `#layout-editor-close` | `click` | `closeLayoutEditor()`（復元） |
| `#layout-editor-overlay` | `click` | オーバーレイの外側をクリックしたときに `closeLayoutEditor()`（復元） |
| `#layout-save-btn` | `click` | `saveLayout()` |
| `#layout-reset-btn` | `click` | `resetLayout()` |

---

## 使用例

### HTML 構造

レイアウトエディタは以下の DOM 構造に依存します：

```html
<!-- トリガーボタン -->
<button id="open-layout-editor">レイアウトを編集</button>

<!-- オーバーレイ -->
<div id="layout-editor-overlay" class="hidden">
  <div class="layout-editor-panel">
    <h2>カードレイアウト</h2>

    <!-- 3 カラムのドロップ領域 -->
    <div id="layout-dropzone-left"></div>
    <div id="layout-dropzone-middle"></div>
    <div id="layout-dropzone-right"></div>

    <!-- 未使用カードプール -->
    <div id="layout-dropzone-unused"></div>

    <!-- 操作ボタン -->
    <button id="layout-save-btn">保存</button>
    <button id="layout-reset-btn">リセット</button>
    <button id="layout-editor-close">閉じる</button>
  </div>
</div>
```

### デフォルトレイアウトのカスタマイズ

`src/celestialflow_web/static/ts/web_config.ts` の `DEFAULT_WEB_CONFIG.dashboard.layout` を変更すれば、出荷時のレイアウトを変更できます：

```typescript
const DEFAULT_WEB_CONFIG: WebConfig = {
  // ...
  dashboard: {
    historyLimit: 20,
    structureEdgeLabel: "none",
    useTotalPendingInStatus: false,
    layout: {
      left:   ["mermaid", "analysis"],
      middle: ["status"],
      right:  ["progress", "error-types", "summary"],
    },
  },
  // ...
};
```

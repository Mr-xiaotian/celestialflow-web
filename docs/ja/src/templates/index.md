# src/celestialflow_web/templates/index.html

> 📅 最終更新日: 2026/09/24

Web UI の Jinja2 テンプレートファイルで、監視システムの完全なページ構造を定義します。

## 全体レイアウト

ページは3つの主要領域に分かれます：

```
<header>  — トップコントロールバー（設定パネル、テーマ切り替え）
<main>
  ├─ .tabs           — タブナビゲーション（ダッシュボード / エラーログ / タスク注入）
  ├─ #dashboard      — ダッシュボード（3カラムレイアウト）
  ├─ #errors         — エラーログ
  └─ #task-injection  — タスク注入
```

テンプレートは Jinja2 の `{% include %}` を使用して各責務領域をサブテンプレートに分割します：

| Partial | 責務 |
|---------|------|
| `partials/head.html` | `<head>` ブロック：favicon、CSS、CDN ライブラリ（Chart.js、SortableJS、Mermaid） |
| `partials/header.html` | トップコントロールバーと設定ボタン、`#settings-panel` のコンテナ |
| `partials/settings_panel.html` | 設定パネル内の言語、リフレッシュ率、自動リフレッシュ、エラーページネーション/ソート/ジャンプ/フィールド編集、ダッシュボード履歴/エッジ増分/待機モード/レイアウト編集、注入ページの「注入可能のみ」などのコントロール |
| `partials/tab_dashboard.html` | ダッシュボードタブコンテナ。`.left-panel` / `.middle-panel` / `.right-panel` の3つの空欄と隠された `#card-pool` を含む |
| `partials/tab_errors.html` | エラーログタブ：検索ボックス、ノードフィルタ、エラーテーブル、ページネーションコンテナ |
| `partials/tab_injection.html` | タスク注入タブ：ノードブラウズ、現在ノードの編集、送信待ちデータのプレビュー、送信とステータスメッセージ |
| `partials/modal_layout_editor.html` | ダッシュボードカードレイアウト編集モーダル（`#layout-editor-overlay`） |
| `partials/modal_error_columns_editor.html` | エラーテーブルフィールド編集モーダル（`#errors-columns-editor-overlay`） |
| `partials/scripts.html` | ネイティブ ESM 方式で唯一の入口 `js/main.js` を読み込む（下記参照） |

## Header コントロールバー

| 要素 | ID / Class | 説明 |
|------|-----------|------|
| 設定ボタン | `#settings-btn` | クリックで設定パネルを開く。a11y 属性付き |
| 設定パネル | `#settings-panel` | リフレッシュ、履歴、言語、ページネーション、増分スイッチなどの設定を含む |
| インターフェース言語 | `#language-select` | 中・英・日の3言語切り替えに対応 |
| 構造図増分 | `#structure-edge-delta` | スイッチ。Mermaid 図のエッジに成功数増分を表示するか制御 |
| テーマ切り替え | `#theme-toggle` | 角丸カプセルボタン。明暗モードを切り替え |

## Dashboard 3カラム構造

`tab_dashboard.html` には3つの空欄コンテナと隠された `#card-pool` のみが提供されます。すべてのカード DOM は `web_config.ts` がモジュール読み込み時に `CARD_TEMPLATES` に基づいて `#card-pool` へ注入し、その後 `applyDashboardLayout()` が `webConfig.dashboard.layout` に従って3カラムへ移動します。

### 左カラム `.left-panel`

| カード | Class | 説明 |
|------|-------|------|
| タスク構造図 | `.mermaid-card` | Mermaid フローチャート。ノード着色とエッジ増分に対応 |
| グラフ分析情報 | `.analysis-card` | トポロジ構造の洞察情報 |

### 中央カラム `.middle-panel`

| カード | Class | 説明 |
|------|-------|------|
| ノード実行状態 | `.status-card` | 動的ノードカード。プログレスバーとリアルタイム増分統計を含む |

### 右カラム `.right-panel`

| カード | Class | 説明 |
|------|-------|------|
| ノード指標推移 | `.progress-card` | 指標切り替え（完了/成功/エラー/重複/待機）に対応した履歴折れ線グラフ |
| エラータイプ分布 | `.error-types-card` | ノードでフィルタ可能なエラータイプ doughnut 図と凡例 |
| 全体状態サマリー | `.summary-card` | グローバル6マスの統計ダッシュボード |

## 外部依存（CDN）

| ライブラリ | バージョン | 用途 |
|----|------|------|
| Chart.js | 未固定（CDN latest） | 折れ線グラフ描画 |
| SortableJS | `@latest` | ダッシュボードレイアウトとエラーテーブルフィールドのドラッグソート |
| Mermaid | `^10`（ESM） | タスクグラフ可視化レンダリング |

## JS モジュール読み込み

フロントエンドはネイティブ ESM を使用し、`partials/scripts.html` は唯一の入口 `js/main.js` のみを読み込み、残りのモジュールはその静的 `import` で連鎖します：

```html
<script
    type="module"
    src="{{ request.url_for('static', path='js/main.js') }}"
></script>
```

入口の import 順序がモジュール評価順序を決定します：

```html
i18n.js               ← 国際化サポート
utils.js              ← 汎用ユーティリティ関数
web_config.js         ← 設定管理ロジック + カード DOM 注入（モジュール読み込み時に ensureAllCards を呼び出し）
loaders.js            ← データ層：状態/グラフメタ情報の取得とローカル派生
util_estimators.js    ← グラフレベルの派生指標推定
dashboard_statuses.js ← ノード状態カードレンダリング
dashboard_structure.js← 構造図レンダリング
errors.js             ← エラーログページネーション + フィールドエディタ
dashboard_analysis.js ← トポロジ分析表示
dashboard_error_types.js ← エラータイプ分布カード
dashboard_summary.js  ← 集計統計
dashboard_history.js  ← 履歴チャート
injection.js          ← タスク注入ロジック
layout_editor.js      ← カードレイアウトエディタ（web_config の CARD_TEMPLATES、PANEL_SELECTOR_MAP および applyDashboardLayout に依存）
main.js               ← グローバル入口とポーリング調整
```

> 注意：`web_config.js` はモジュール読み込み時に直ちに `ensureAllCards()` を呼び出し、すべてのカード DOM を事前に `#card-pool` へ注入します。そのため入口は必ず最初にこれを import し、後続の `dashboard_*` モジュールのトップレベル `getElementById` が対応ノードを見つけられるようにする必要があります；`tests/test_server.py` はモジュール評価順序テストでこの制約を検証します。すべてのコンパイル成果物は `main.js` から `import` を通じて到達可能でなければなりません。

## CSS スタイル参照

```html
css/_colors.css             ← 色変数定義
css/base.css                ← グローバル基本スタイルと設定パネル
css/dashboard.css           ← ダッシュボードレイアウトと Tab コンテナ
css/dashboard_structure.css  ← 構造図専用スタイル
css/dashboard_analysis.css   ← 分析カード専用スタイル
css/dashboard_statuses.css   ← ノードカード専用スタイル
css/dashboard_summary.css    ← サマリーパネル専用スタイル
css/dashboard_history.css    ← 履歴図専用スタイル
css/dashboard_error_types.css ← エラータイプ分布カード専用スタイル
css/errors.css              ← エラーログページスタイル
css/injection_layout.css     ← 注入ページレイアウトスタイル
css/injection_nodes.css      ← 注入ページノードリストスタイル
css/injection_editor.css     ← 注入ページエディタスタイル
css/injection_preview.css    ← 注入ページプレビュースタイル
```

## カードレイアウトエディタモーダル (`#layout-editor-overlay`)

フローティングモーダル（デフォルトは `.overlay.hidden` で非表示）。3カラムダッシュボードカードのドラッグソートに対応します。

- **オーバーレイ**: `#layout-editor-overlay` / `.overlay` — 全画面の半透明黒背景
- **エディタ本体**: `#layout-editor` / `.layout-editor` — 角丸カードコンテナ
- **3カラム配置エリア**: 左中右の3つの drop zone（`#layout-dropzone-left`、`#layout-dropzone-middle`、`#layout-dropzone-right`）。SortableJS ベースでドラッグを実現
- **未使用プール**: `#layout-dropzone-unused` — 3カラムから外されたカードを収容
- **下部ボタン**: 保存（`#layout-save-btn`）とデフォルトにリセット（`#layout-reset-btn`）
- 設定パネルの `#open-layout-editor` ボタンで開く；`#layout-editor-close` をクリックするかオーバーレイ外をクリックで閉じる
- 保存時に `applyDashboardLayout()` を呼び出して即時反映し、その後 `saveWebConfig()` を呼び出してバックエンドに永続化

## エラーテーブルフィールドエディタモーダル (`#errors-columns-editor-overlay`)

`partials/modal_error_columns_editor.html` で読み込まれます：

- **オーバーレイ**: `#errors-columns-editor-overlay` / `.overlay` — レイアウトエディタと同じオーバーレイスタイルを再利用
- **本体**: `#errors-columns-editor` / `.layout-editor.error-columns-editor` — 2つの dropzone を含む：`#errors-columns-dropzone-visible` と `#errors-columns-dropzone-hidden`
- **下部ボタン**: 保存（`#errors-columns-save-btn`）とデフォルトにリセット（`#errors-columns-reset-btn`）
- 設定パネルの `#open-error-columns-editor` ボタンで開く；`#errors-columns-editor-close` をクリックするかオーバーレイ外をクリックで閉じる
- `errors.ts` の `openErrorColumnsEditor()` / `saveErrorColumns()` がロジックを担当。詳細は `errors.md` を参照

## 使用例

### ブラウザからアクセス

Web サーバーを起動後、ブラウザのアドレスバーで次にアクセスします：

```
http://127.0.0.1:5000
```

起動コマンド：

```bash
# コマンドラインからの起動（デフォルト 0.0.0.0:5000）
celestialflow-web

# または Python で起動
python -c "from celestialflow_web import TaskWebServer; TaskWebServer(host='127.0.0.1', port=5000).start_server()"
```

ブラウザを開くと3つのタブが表示されます：
- **ダッシュボード (Dashboard)**: タスクグラフの構造図、ノード実行状態、指標推移、全体サマリーをリアルタイム表示
- **エラーログ (Errors)**: エラー記録をページネーションで閲覧・検索
- **タスク注入 (Task Injection)**: 指定ノードへ新しいタスクを注入

### テンプレート変更の例

`index.html` は Jinja2 テンプレートエンジンを使用しており、カスタムテンプレート変数や HTML の直接編集でインターフェースをカスタマイズできます。

#### ページタイトルの変更

`index.html` を編集し `<title>` タグを見つけます：

```html
<!-- 元の内容 -->
<title>タスクグラフ監視システム</title>

<!-- カスタムタイトルに変更 -->
<title>私のタスク監視</title>
```

#### ダッシュボードレイアウトの調整

> ⚠️ `tab_dashboard.html` には3つの空欄コンテナ（`.left-panel` / `.middle-panel` / `.right-panel`）と隠された `#card-pool` **のみが提供されます**。**HTML 内のカード順序を直接変更しないでください**。すべてのカードは `web_config.ts` がモジュール読み込み時に `CARD_TEMPLATES` を通じて `#card-pool` へ注入し、その後 `applyDashboardLayout()` が `webConfig.dashboard.layout` に従って3カラムへ移動します。

3カラムレイアウトを調整する必要がある場合は、優先的に次の2つの方法を使用してください：

1. **実行時**：設定パネルの「ダッシュボードレイアウトを編集」（`#open-layout-editor`）を開き、`#layout-editor-overlay` モーダルでカードを目標カラムへドラッグして保存。
2. **デフォルト値**：`src/celestialflow_web/static/ts/web_config.ts` の `DEFAULT_WEB_CONFIG.dashboard.layout` を編集。例えば：

```typescript
dashboard: {
    layout: {
        left: ["analysis", "mermaid"],   // 分析カードを最上部に配置
        middle: ["status"],
        right: ["progress", "summary", "error-types"],
    },
}
```

利用可能なカード key：`mermaid`、`analysis`、`status`、`progress`、`error-types`、`summary`。

#### 設定による動的制御

実行時のすべての UI 設定はグループ化された `WebConfig` で制御され、`global` / `dashboard` / `errors` / `injection` の4つのサブセクションを含みます。`web_config.ts` は起動時に `GET /api/pull_config` でユーザー設定を読み込み、保存時は `POST /api/push_config` を呼び出して全体を上書きします。バックエンドの `config.json` で初期値を提供できます：

```json
{
    "global": {
        "theme": "dark",
        "language": "zh-CN",
        "autoRefreshEnabled": true,
        "refreshInterval": 5000
    },
    "dashboard": {
        "historyLimit": 20,
        "showStructureEdgeDelta": true,
        "useTotalPendingInStatus": true,
        "layout": {
            "left": ["mermaid", "analysis"],
            "middle": ["status"],
            "right": ["progress", "error-types", "summary"]
        }
    },
    "errors": {
        "pageSize": 50,
        "sortOrder": "newest",
        "jumpToInjectionAfterRetry": true,
        "columns": ["index", "event_id", "message", "stage", "task", "time", "retry"]
    },
    "injection": {
        "showInjectableOnly": true
    }
}
```

> フィールドの詳細説明は [`web_config.md`](../static/ts/web_config.md) を参照。変更後は設定パネルの「設定を保存」ボタン、または `saveWebConfig()` の自動トリガーを待つことで反映されます。

#### カスタム CSS の追加

カスタムスタイルファイルを `src/celestialflow_web/static/css/` ディレクトリに置き、`partials/head.html` で Jinja2 の `request.url_for` を使って読み込み、非ルートパスにマウントされた場合でもパスが正しく解決されるようにします：

```html
<link
    rel="stylesheet"
    href="{{ request.url_for('static', path='css/custom.css') }}"
/>
```

JS スクリプトも同様に `{{ request.url_for('static', path='js/xxx.js') }}` を使用します。

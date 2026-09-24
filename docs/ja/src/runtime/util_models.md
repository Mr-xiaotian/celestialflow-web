# src/celestialflow_web/runtime/util_models.py

> 📅 最終更新日: 2026/09/24

## 役割

`celestialflow_web.runtime.util_models` モジュールは Web モジュールが使用するすべての Pydantic データモデルを定義し、データ検証、シリアライズ、API リクエスト/レスポンスの型制約に使用されます。

## モデル一覧

### GraphMetaModel

グラフメタ情報データモデル。グラフ構造（ノード / エッジ / ソースノード）、ノード構築期メタ情報（`node_meta`）、グラフ分析結果（`analysis`）を統合して保持します。

| フィールド | 型 | デフォルト値 | 説明 |
|------|------|--------|------|
| `graph_id` | `str` | `""` | グラフインスタンス識別子。Reporter 側の graph コンテキスト検証に使用 |
| `nodes` | `list[str]` | `[]` | ノード名リスト |
| `edges` | `dict[str, list[str]]` | `{}` | エッジ辞書。キーはソースノード名、値はターゲットノード名リスト |
| `source_nodes` | `list[str]` | `[]` | ソースノード（入口ノード）名リスト |
| `node_meta` | `dict[str, dict[str, Any]]` | `{}` | ノード構築期メタ情報辞書。キーはノード名 |
| `analysis` | `dict[str, Any] \| None` | `None` | グラフ分析結果辞書 |

### StatusModel

ノード状態データモデル。各ノードの実行状態を表します。

| フィールド | 型 | 説明 |
|------|------|------|
| `graph_id` | `str` | グラフインスタンス識別子。デフォルト `""` |
| `timestamp` | `float` | 状態データのタイムスタンプ（Unix） |
| `status` | `dict[str, dict[str, Any]]` | ノード名から状態辞書へのマッピング |

### ErrorsModel

エラー内容データモデル。完全なエラー記録リストを含みます。

| フィールド | 型 | 説明 |
|------|------|------|
| `graph_id` | `str` | グラフインスタンス識別子。デフォルト `""` |
| `errors` | `list[dict[str, Any]]` | エラー記録リスト。各項目はエラー辞書；SQLite データベースに直接書き込まれる |

### TaskInjectionModel

タスク注入リクエストモデル。実行中のタスクグラフへ新しいタスクを動的に挿入するために使用します。

> このモデルは `RootModel[dict[str, list[Any]]]` を継承し、リクエストボディは直接 `{ノード名: [タスクリスト]}` 形式の辞書で、`node`/`task_datas`/`timestamp` などの独立フィールドは含みません。

| ルート値の型 | 説明 |
|----------|------|
| `dict[str, list[Any]]` | キーはノード名、値はそのノードへ注入するタスクデータのリスト |

**リクエストボディの例：**

```json
{
  "StageA": [{"id": 1, "value": 42}, {"id": 2, "value": 99}],
  "StageB": [{"id": 3, "value": 55}]
}
```

### TerminationInjectionModel

終了信号注入リクエストモデル。実行中のタスクグラフへ終了対象ノードを注入するために使用します。

> このモデルは `RootModel[list[str]]` を継承し、リクエストボディは直接ノード名の文字列リストで、他のラッパーフィールドは含みません。

| ルート値の型 | 説明 |
|----------|------|
| `list[str]` | 終了信号を注入するノード名リスト |

**リクエストボディの例：**

```json
[
  "StageA",
  "StageB"
]
```

### DashboardConfigModel

ダッシュボードレイアウト設定モデル。フロントエンドのパネルカードレイアウトを定義します。

| フィールド | 型 | 説明 |
|------|------|------|
| `left` | `list[str]` | 左パネルに表示するカードタイプのリスト |
| `middle` | `list[str]` | 中央パネルに表示するカードタイプのリスト |
| `right` | `list[str]` | 右パネルに表示するカードタイプのリスト |

### GlobalConfigModel

グローバル共有設定モデル（`WebConfigModel.global_` の下にネストされます）。

| フィールド | 型 | デフォルト値 | 説明 |
|------|------|--------|------|
| `theme` | `str` | — | UI テーマ（`"light"`、`"dark"` など） |
| `autoRefreshEnabled` | `bool` | `True` | 自動リフレッシュを有効にするか |
| `refreshInterval` | `int` | — | ページデータのリフレッシュ間隔（ms） |
| `language` | `str` | `"zh-CN"` | インターフェース言語 |

### DashboardPageConfigModel

ダッシュボードページ設定モデル（`WebConfigModel.dashboard` の下にネストされます）。

| フィールド | 型 | デフォルト値 | 説明 |
|------|------|--------|------|
| `historyLimit` | `int` | — | 履歴記録の数量上限 |
| `showStructureEdgeDelta` | `bool` | `False` | 構造図のエッジ増分を表示するか |
| `useTotalPendingInStatus` | `bool` | `False` | ノード待機パラメータにグローバル推定を使用するか |
| `layout` | `DashboardConfigModel` | — | ダッシュボードカードの3カラムレイアウト定義 |

### ErrorsPageConfigModel

エラーページ設定モデル（`WebConfigModel.errors` の下にネストされます）。

| フィールド | 型 | デフォルト値 | 説明 |
|------|------|--------|------|
| `pageSize` | `int` | `10` | エラーページの1ページあたりの件数 |
| `sortOrder` | `str` | `"newest"` | デフォルトのソート方式（`"newest"` / `"oldest"`） |
| `jumpToInjectionAfterRetry` | `bool` | `True` | タスクリトライ後に注入ページへ遷移するか |
| `columns` | `list[str]` | `["index", "event_id", "message", "stage", "task", "time", "retry"]` | エラーページのテーブルの列定義と表示順（設定パネルの列エディタで制御） |

### InjectionPageConfigModel

注入ページ設定モデル（`WebConfigModel.injection` の下にネストされます）。

| フィールド | 型 | デフォルト値 | 説明 |
|------|------|--------|------|
| `showInjectableOnly` | `bool` | `True` | 注入可能なノードのみを表示するか |

### WebConfigModel

Web UI グローバル設定モデル（ネストされたグループ構造）。

| フィールド | 型 | デフォルト値 | 説明 |
|------|------|--------|------|
| `global_` | `GlobalConfigModel` | — | グローバル共有設定（JSON エイリアスは `"global"`） |
| `dashboard` | `DashboardPageConfigModel` | — | ダッシュボードページ設定 |
| `errors` | `ErrorsPageConfigModel` | — | エラーページ設定 |
| `injection` | `InjectionPageConfigModel` | `InjectionPageConfigModel()` | 注入ページ設定 |

設定はネストされたグループ構造を採用しています：`theme`、`refreshInterval`、`language` などは `GlobalConfigModel`（JSON キーは `"global"`）にあり、`historyLimit`、`showStructureEdgeDelta` などは `DashboardPageConfigModel` にあり、`pageSize`、`sortOrder` などは `ErrorsPageConfigModel` にあります。

## 使用例

### データ検証とシリアライズ

```python
from celestialflow_web.runtime.util_models import (
    WebConfigModel,
    GlobalConfigModel,
    DashboardPageConfigModel,
    DashboardConfigModel,
    ErrorsPageConfigModel,
    InjectionPageConfigModel,
    TaskInjectionModel,
)

# --- WebConfigModel の使用（ネスト構造） ---
# `global` は Python の予約語であるため、WebConfigModel は model_validate()
# または Pydantic の alias パスを通じてのみ構築できる；直接 WebConfigModel(global_=...) は
# model_config が populate_by_name を有効にしていないため失敗する（__init__ 段階のみ）。
config = WebConfigModel.model_validate(
    {
        "global": GlobalConfigModel(
            theme="dark",
            autoRefreshEnabled=True,
            refreshInterval=5000,
            language="zh-CN",
        ).model_dump(),
        "dashboard": DashboardPageConfigModel(
            historyLimit=20,
            showStructureEdgeDelta=False,
            useTotalPendingInStatus=False,
            layout=DashboardConfigModel(
                left=["mermaid"],
                middle=["status"],
                right=["progress"],
            ),
        ).model_dump(),
        "errors": ErrorsPageConfigModel(
            pageSize=10,
            sortOrder="newest",
            jumpToInjectionAfterRetry=True,
            columns=["index", "event_id", "message", "stage", "task", "time", "retry"],
        ).model_dump(),
        "injection": InjectionPageConfigModel(
            showInjectableOnly=True,
        ).model_dump(),
    }
)
print(f"テーマ: {config.global_.theme}")
print(f"ダッシュボードレイアウト: {config.dashboard.layout.model_dump()}")

# 辞書にシリアライズ（by_alias=True で global_ を "global" に変換）
config_dict = config.model_dump(by_alias=True)

# 辞書から作成
restored = WebConfigModel.model_validate(config_dict)

# --- TaskInjectionModel の使用 ---
injection = TaskInjectionModel(
    StageA=[{"id": 1, "value": 42}, {"id": 2, "value": 99}],
    StageB=[{"id": 3, "value": 55}],
)
print(f"注入ノード数: {len(injection.root)}")
for node_name, tasks in injection.root.items():
    print(f"  {node_name}: {len(tasks)} 個のタスク")
```

> 注意：`TaskInjectionModel` は `RootModel[dict[str, list[Any]]]` であり、リクエストボディは直接ノード名からタスクリストへのマッピング辞書で、`node`/`task_datas` などのフィールドをラップしません。

### エラーデータの処理

```python
from celestialflow_web.runtime.util_models import ErrorsModel

# エラー内容
content = ErrorsModel(
    graph_id="graph-001",
    errors=[
        {"error_type": "ValueError", "error_message": "Invalid input"},
        {"error_type": "TimeoutError", "error_message": "Connection lost"},
    ],
)
print(f"エラー件数: {len(content.errors)}")
```

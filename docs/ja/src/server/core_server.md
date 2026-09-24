# src/celestialflow_web/server/core_server.py

> 📅 最終更新日: 2026/09/24

TaskWeb モジュールは FastAPI ベースの軽量な Web サーバーを提供し、タスクグラフの実行をリアルタイムで監視・管理します。`TaskReporter`（バックエンド）と Web UI（フロントエンド）の間の中継局として機能します。

## 起動方法

### コマンドラインからの起動

```bash
# デフォルトでは 0.0.0.0:5000 をリッスン
celestialflow-web

# ポートを指定
celestialflow-web --port 5005

# ホストとポートを指定
celestialflow-web --host 127.0.0.1 --port 5005

# ログレベルを指定
celestialflow-web --log-level debug
```

### コマンドライン引数

| 引数 | デフォルト値 | 説明 |
|------|--------|------|
| `--host` | `0.0.0.0` | リッスンアドレス |
| `--port` | `5000` | リッスンポート |
| `--log-level` | `info` | ログレベル (critical/error/warning/info/debug/trace) |

### コードからの起動

```python
from celestialflow_web import TaskWebServer

server = TaskWebServer(host="127.0.0.1", port=5005, log_level="info")
server.start_server()
```

### CLI 入口

`core_server.py` はコマンドライン入口関数も提供します：

- `parse_args()` — `--host`、`--port`、`--log-level` 引数を解析；`--log-level` は `critical` / `error` / `warning` / `info` / `debug` / `trace` に制限。
- `main_entry()` — 解析後の引数に基づいて `TaskWebServer` を構築し、`start_server()` を呼び出す。

コマンドラインツール `celestialflow-web` は `main_entry` から登録されます。

## 機能インターフェース

`http://localhost:5000`（または指定ポート）にアクセスすると Web UI が表示されます。

### 主要パネル

| パネル | 機能 |
|------|------|
| **Dashboard** | タスクグラフのリアルタイム状態概要（構造の可視化（Mermaid 図）、ノード数、成功/失敗/滞留タスク数、折れ線グラフ） |
| **Errors** | リアルタイムのエラーログリスト |
| **Task Injection** | Web インターフェースからタスクを動的に注入 |

### テーマサポート

- デイ/ナイトテーマの切り替えに対応
- テーマ設定はバックエンドの `config.json` に永続化

## API インターフェース (RESTful)

TaskWeb は `TaskReporter` の呼び出しとフロントエンドでの利用のための RESTful API を提供します。すべてのインターフェースは `/api/` をプレフィックスとし、取得インターフェースは `pull_`、プッシュインターフェースは `push_` で命名されます。

### 取得インターフェース (GET /api/pull_*)

`known_rev` メカニズムをサポートする取得インターフェース（`pull_status`、`pull_graph_meta`、`pull_errors`、`pull_error_type_counts`）は、サーバー側のデータバージョンが変化していない場合に帯域を節約するため `data: null` を返します；`pull_config`、`pull_injection`、`pull_server_state` は `known_rev` メカニズムを使用せず、毎回完全なデータを返します（うち `pull_server_state` は `sync_graph_context` を呼び出すため副作用があります）。

| エンドポイント | 返却構造 (data フィールド) | 説明 |
|------|--------------------|------|
| `pull_config` | `dict` | テーマ、言語、リフレッシュ頻度などのグローバル設定を取得 |
| `pull_graph_meta` | `dict[str, Any]` | グラフメタ情報（グラフ構造 + ノード構築期メタ情報 + グラフ分析結果）を取得 |
| `pull_status` | `dict[str, dict[str, Any]]` | 各ノードのリアルタイム実行指標と統一タイムスタンプを取得 |
| `pull_errors` | `list[dict]` | ページネーションでエラーログを取得。ノード/キーワードフィルタとソートに対応 |
| `pull_error_type_counts` | `list[dict[str, Any]]` | エラータイプ別に集計した統計結果。ノードフィルタに対応 |
| `pull_injection` | `{"tasks": dict[str, list[Any]], "terminations": list[str]}` | TaskGraph が注入待ちのタスクキューと終了信号を取得するためのもの（タスクはノード名でグループ化、読み取り後にクリア） |
| `pull_server_state` | `dict[str, Any]` | Reporter 同期に必要なサーバー状態（interval/is_current_graph/has_graph_meta/max_event_id_in_fail）を取得 |

### プッシュインターフェース (POST /api/push_*)

主に `TaskReporter` が呼び出し、バックエンドの実行状態を報告するために使用します。

| エンドポイント | データモデル | 説明 |
|------|---------|------|
| `push_config` | `WebConfigModel` | フロントエンドが呼び出し、ユーザー設定を保存 |
| `push_status` | `StatusModel` | ノード状態スナップショット + 現在のタイムスタンプを報告 |
| `push_graph_meta` | `GraphMetaModel` | グラフメタ情報（グラフ構造 + ノード構築期メタ情報 + 分析結果）を報告；`graph_id` が一致しない場合は 409 を返す |
| `push_errors` | `ErrorsModel` | エラー内容を直接プッシュし SQLite に書き込み |
| `push_injection_tasks` | `TaskInjectionModel` | フロントエンドがタスク注入リクエストを送信 |
| `push_injection_terminations` | `TerminationInjectionModel` | フロントエンドが終了信号注入リクエストを送信 |

## データモデル (Pydantic)

> 完全なモデル定義は `util_models.md` を参照。ここではコアフィールドのみを列挙します。

### GraphMetaModel

```python
class GraphMetaModel(BaseModel):
    graph_id: str = ""  # グラフインスタンス識別子。Reporter 側の graph コンテキスト検証に使用
    nodes: list[str] = Field(default_factory=list)  # ノード名リスト
    edges: dict[str, list[str]] = Field(
        default_factory=dict
    )  # エッジ辞書。キーはソースノード名、値はターゲットノード名リスト
    source_nodes: list[str] = Field(default_factory=list)  # ソースノードリスト
    node_meta: dict[str, dict[str, Any]] = Field(
        default_factory=dict
    )  # ノード構築期メタ情報。キーはノード名
    analysis: dict[str, Any] | None = None  # グラフ分析結果
```

### StatusModel

```python
class StatusModel(BaseModel):
    graph_id: str = ""  # グラフインスタンス識別子
    timestamp: float  # 統一サンプリングタイムスタンプ
    status: dict[str, dict[str, Any]]  # キーはノード名、値はノード状態辞書
```

### ErrorsModel

```python
class ErrorsModel(BaseModel):
    graph_id: str = ""  # グラフインスタンス識別子
    errors: list[dict[str, Any]]  # エラー記録リスト。SQLite データベースに直接書き込まれる
```

### TaskInjectionModel

```python
class TaskInjectionModel(RootModel[dict[str, list[Any]]]):
    """タスク注入リクエストモデル。形式は {node_name: [tasklist]}。"""
```

> リクエストボディは直接ノード名からタスクリストへのマッピングです。例：
> `{"StageA": [task1, task2], "StageB": [task3]}`

### TerminationInjectionModel

```python
class TerminationInjectionModel(RootModel[list[str]]):
    """終了信号注入リクエストモデル。形式は [node_name, ...]。"""
```

> リクエストボディは直接ノード名のリストです。例：
> `["StageA", "StageB"]`

### WebConfigModel

設定はネストされたグループ構造を採用しています。

```python
class GlobalConfigModel(BaseModel):
    theme: str
    autoRefreshEnabled: bool = True
    refreshInterval: int
    language: str = "zh-CN"


class DashboardConfigModel(BaseModel):
    left: list[str]
    middle: list[str]
    right: list[str]


class DashboardPageConfigModel(BaseModel):
    historyLimit: int
    showStructureEdgeDelta: bool = False
    useTotalPendingInStatus: bool = False
    layout: DashboardConfigModel


class ErrorsPageConfigModel(BaseModel):
    pageSize: int = 10
    sortOrder: str = "newest"
    jumpToInjectionAfterRetry: bool = True
    columns: list[str] = Field(
        default_factory=lambda: [
            "index",
            "event_id",
            "message",
            "stage",
            "task",
            "time",
            "retry",
        ]
    )


class InjectionPageConfigModel(BaseModel):
    showInjectableOnly: bool = True


class WebConfigModel(BaseModel):
    global_: GlobalConfigModel = Field(alias="global")
    dashboard: DashboardPageConfigModel
    errors: ErrorsPageConfigModel
    injection: InjectionPageConfigModel = Field(
        default_factory=InjectionPageConfigModel
    )
```

## 設定管理

Web サービスの設定の永続化はパッケージ内の `src/celestialflow_web/config.json` に保存されます。

- `load_config()` — 起動時に読み込み `WebConfigModel` で検証；`config.json` が存在しない場合は直接 `ConfigurationError` をスローし、ハードコードされたデフォルト値では起動しません。
- `save_config(config, config_path)` — 設定を JSON ファイルに保存、スレッドセーフ（上位の `push_config` ルート内の `config_lock` が保証）
- `cal_interval(refresh_interval)` — ミリ秒のリフレッシュ間隔を秒に変換、範囲は `[1.0, 60.0]` に制限
- **同期メカニズム**: フロントエンドが `refreshInterval` を更新すると、バックエンドの `report_interval` が自動的に同期され、`TaskReporter` のプッシュ頻度に影響します。

## TaskGraph との統合

### TaskGraph で有効化

```python
from celestialflow import TaskGraph, TaskStage


def process(x: int) -> int:
    return x * 2


stage_a = TaskStage("StageA", process, execution_mode="thread")
graph = TaskGraph(name="DemoGraph")
graph.set_stages(stages=[stage_a])
graph.set_reporter(True, host="127.0.0.1", port=5005)
init_tasks = {stage_a.get_name(): [1, 2, 3]}
graph.start_graph(init_tasks)
```

### データフロー

```
TaskGraph                         TaskWeb                    Browser
    |                                |                          |
    |--- push_graph_meta ---------->|--- Dashboard ----------->|
    |--- push_status --------------->|                          |
    |                                |                          |
    |--- push_errors --------------->|---- Errors ------------->|
    |                                |                          |
    |<-- pull_injection -------------|<--- Inject Tasks --------|
    |<-- pull_server_state ----------|<--- Reporter Sync -------|
    |                                |                          |
```

## エラー処理

### SQLite 永続化

エラー記録は `append_records` を通じて SQLite データベースに直接書き込まれ、効率的なクエリとページネーションをサポートします。SQLite データベースファイルは `tempfile.mkstemp` で手動管理されたファイルディスクリプタを作成して使用します（`NamedTemporaryFile` が Windows 上で自動削除とファイル再オープンが競合するのを回避）。

### タスク注入の並行安全性

`injection_tasks` 辞書と `injection_terminations` 集合は `task_injection_lock` で保護され、`push_injection_tasks` / `push_injection_terminations` の書き込みと `pull_injection` の読み取り（クリアを含む）はすべてロック内で操作され、競合状態を回避します。タスク注入は**上書き**セマンティクスを採用します：同じノード名の新しいタスクは古いタスクリストを上書きします；終了信号注入は**集合**セマンティクスを採用します：重複するノード名は重複排除されます。

## 注意事項

1. **ポート競合**: 指定ポートが使用されていないことを確認してください。
2. **ファイアウォール**: リモートアクセスが必要な場合は、ファイアウォールルールを設定してください。
3. **HTTPS**: 本番環境ではリバースプロキシ（Nginx など）を使用して HTTPS を追加することを推奨します。
4. **認証**: 現在のバージョンには組み込み認証がありません。本番環境では認証レイヤーを追加することを推奨します。

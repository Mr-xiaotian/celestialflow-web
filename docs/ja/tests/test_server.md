# tests/test_server.py

> 📅 最終更新日: 2026/09/24

## 役割

`celestialflow_web.server.core_server` が提供する RESTful API を検証し、Web ダッシュボードがグラフ状態の表示、設定の取得、タスクの注入、エラーログの閲覧を正しく行えること、およびスナップショットデータの分離性を検証します。

## コアテスト対象

- `TaskWebServer`: FastAPI ベースで実装された監視・操作サーバー。

## 主要テストシナリオ

### スナップショット分離
- `test_store_snapshot_methods_return_isolated_copies`: server の各スナップショットインターフェースがディープコピーを返し、返り値を変更しても内部 store に影響しないことを検証。

### 静的リソースレンダリング
- `test_index_page`: ホームページ `/` が `dashboard` コンテナを含む HTML ページを正しく返せることを検証。
- `test_entry_module_reaches_every_built_artifact`: ホームページが1つの ESM 入口 `main.js` のみを参照し、その入口が import グラフに従ってすべてのコンパイル成果物に到達できることを検証し、誰からも import されないデッドモジュールの発生を防ぐ。
- `test_card_injecting_module_evaluates_before_dashboards`: `web_config` がモジュール評価順序で各 `dashboard_*` モジュールより先であること（カード DOM 注入が、それに依存する `getElementById` より先）を検証。

### 設定の取得
- `test_config_api`: フロントエンドが必要とするランタイムパラメータ（リフレッシュ頻度、テーマなど）が正しく取得できることを検証。

### サーバー状態
- `test_server_state_api`: reporter が取得するサーバー同期状態を検証。ポーリング間隔、現在のグラフ識別子、グラフメタ情報の準備状態（`has_graph_meta`）、失敗イベントの水位線を含む。

### 状態同期 (Rev メカニズム)
- `test_status_push_pull`:
  - `push_status` がスナップショットを正しく保存できることを検証。
  - `pull_status` が増分更新をサポートすること（`known_rev` がサーバーの現在バージョンと一致する場合、帯域を節約するため空データを返す）を検証。

### グラフメタ情報同期
- `test_graph_meta_push_pull`: `push_graph_meta` / `pull_graph_meta` がグラフ構造、ノード構築期メタ情報、分析結果を完全に保持し、`known_rev` がヒットした場合は再送しないことを検証。

### タスク注入
- `test_task_injection`: POST インターフェースで注入したタスクが正しく一時保持され、スケジューラが GET インターフェースで消費し、消費後にクリアされることを検証。
- `test_task_injection_overwrites_tasklist_per_node`: 新しい push がノードごとに task list を更新し、追記しないことを検証。
- `test_task_injection_requires_tasklist_mapping`: 不正な payload（リストでない値）が 422 を返すことを検証。
- `test_termination_injection_requires_string_array`: 終了信号注入インターフェースがリクエストボディを文字列配列として要求し、そうでなければ 422 を返すことを検証。

### エラータイプ集計
- `test_get_error_type_counts_returns_grouped_stats`: 全ノードのエラータイプ集計統計を検証し、`error_type` ごとにグループ化されたカウントを返す。
- `test_get_error_type_counts_supports_node_filter`: ノード（`stage`）でフィルタしたエラータイプ集計を検証。
- `test_pull_error_type_counts`: `/api/pull_error_type_counts` HTTP エンドポイントが全ノード集計、単一ノードフィルタ、および `known_rev` キャッシュヒット時の `data: null` 返却をサポートすることを検証。

### エラー管理
- `test_errors_pagination`:
  - エラー記録の一括プッシュを検証。
  - ページネーションロジックを検証：`total_pages`、`total`、現在ページのデータ量を確認。
  - ノード（`node`）によるフィルタロジックを検証。
  - キーワード（`keyword`）フィルタロジックを検証。
  - ソート（`sort_order`）を検証：`newest` と `oldest` の両方をサポート。
- `test_push_errors_appends_for_same_graph`: 同じ `graph_id` で複数回プッシュしたエラーは追記のみで上書きされない。
- `test_push_errors_duplicate_append_is_idempotent`: 同じ `event_id` を重複プッシュしても重複行が発生しない。
- `test_newer_graph_replaces_previous_graph_context`: 新しい `graph_id` が到来すると古いエラーキャッシュがクリアされる。
- `test_stale_graph_pushes_are_ignored`: 新しいグラフへ切り替えた後、古いグラフの遅延プッシュが現在のキャッシュを汚染しない。
- `test_push_errors_meta_route_removed`: `/api/push_errors_meta` は削除済みで、アクセスすると 404 を返す。

## テストカバレッジマトリクス

| テスト関数 | カバレッジ対象 |
|----------|----------|
| `test_store_snapshot_methods_return_isolated_copies` | スナップショットがディープコピーを返す |
| `test_index_page` | ホームページの HTML レンダリング |
| `test_entry_module_reaches_every_built_artifact` | ESM 入口がすべてのコンパイル成果物に到達可能 |
| `test_card_injecting_module_evaluates_before_dashboards` | `web_config` が dashboard モジュールより先に評価される |
| `test_config_api` | `/api/pull_config` の設定取得 |
| `test_server_state_api` | `/api/pull_server_state` のサーバー状態 |
| `test_push_errors_meta_route_removed` | 旧エンドポイントが削除済み |
| `test_status_push_pull` | 状態プッシュと増分取得 |
| `test_graph_meta_push_pull` | グラフメタ情報のプッシュと増分取得 |
| `test_task_injection` | タスクと終了信号の注入、消費、クリア |
| `test_task_injection_overwrites_tasklist_per_node` | ノード単位の task list 上書き |
| `test_task_injection_requires_tasklist_mapping` | タスク注入パラメータの検証 |
| `test_termination_injection_requires_string_array` | 終了信号注入パラメータの検証 |
| `test_errors_pagination` | エラーのページネーション、フィルタ、ソート |
| `test_push_errors_appends_for_same_graph` | 同一グラフのエラー追記 |
| `test_push_errors_duplicate_append_is_idempotent` | 重複プッシュの冪等性 |
| `test_newer_graph_replaces_previous_graph_context` | 新グラフコンテキストへの切り替え |
| `test_stale_graph_pushes_are_ignored` | 期限切れプッシュの無視 |
| `test_get_error_type_counts_returns_grouped_stats` | 全ノードのエラータイプ集計 |
| `test_get_error_type_counts_supports_node_filter` | ノードでフィルタしたエラータイプ集計 |
| `test_pull_error_type_counts` | エラータイプ集計 API（キャッシュヒット） |

## テストの重点

- **Rev バージョン管理**: フロントエンドのリフレッシュロジックの効率性を確保し、冗長なデータ転送を避ける。
- **ページネーションの正確性**: バックエンドがエラー記録を処理する際のオフセット計算を検証。
- **タスクの一貫性**: 注入されたタスクが取得・消費後に正しくクリアされ、重複処理を防ぐことを確保。
- **スナップショット分離**: フロントエンドが取得したデータが、内部状態の急変によって不整合を起こさないことを確保。
- **パラメータ検証**: 注入インターフェースが不正な payload に対して 422 を返し、下流が誤ったデータを処理するのを防ぐことを検証。
- **エラータイプ集計**: `/api/pull_error_type_counts` が `error_type` ごとにグループ集計でき、全ノードおよびノード単位のフィルタをサポートし、Rev メカニズムと連携してキャッシュヒットを実現することを検証。
- **ユーティリティメソッド**: `get_error_type_counts` は server 層の純粋なユーティリティメソッドで、返り値はダッシュボードのエラー分布表示に直接使用できる。

## 実行方法

```bash
# すべて実行
uv run pytest tests/test_server.py -v

# 状態同期テストのみ実行
uv run pytest tests/test_server.py -k "status" -v

# タスク注入テストのみ実行
uv run pytest tests/test_server.py -k "injection" -v

# エラー管理テストのみ実行
uv run pytest tests/test_server.py -k "errors" -v

# 設定取得テストのみ実行
uv run pytest tests/test_server.py -k "config" -v

# エラータイプ集計テストのみ実行
uv run pytest tests/test_server.py -k "error_type" -v
```

## 重要な詳細

- `FastAPI TestClient` を使用して模擬リクエストを行うため、実際のポートリッスンは起動しません。
- スナップショット分離テストは `web_server` fixture（`conftest.py` が提供）を直接操作し、その他のテストは `client` fixture を使用します。
- テストは各関数の実行前に新しい server インスタンスを作成します。

## 注意事項

- Web サービスは CelestialFlow の可視化ウィンドウです。
- 関連する実装は `src/celestialflow_web/server/core_server.py` にあります。

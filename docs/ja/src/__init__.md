# src/celestialflow_web/__init__.py

> 📅 最終更新日: 2026/09/24

`celestialflow_web` パッケージは CelestialFlow の独立した Web 監視インターフェースを提供し、FastAPI とネイティブ TypeScript で構築され、タスク状態の可視化、エラー追跡、タスク注入、フロントエンド設定の永続化をサポートします。

## モジュール概要

パッケージルートは現在、公開オブジェクトを1つだけエクスポートします：

| エクスポートシンボル | 出所 | 説明 |
|---------|------|------|
| `TaskWebServer` | `celestialflow_web.server.core_server` | FastAPI Web サービス入口クラス |

ランタイム構造はすでに3つのバックエンドサブパッケージに分割されています：

| サブパッケージ | 役割 |
|------|------|
| `server/` | サービス入口とアプリケーションライフサイクル管理 |
| `runtime/` | 設定、モデル、SQLite、パラメータ正規化ユーティリティ |
| `routes/` | Pull / Push ルート登録 |

## ファイル説明

### コアバックエンドコンポーネント

1. **server/core_server.py** (`TaskWebServer`)
   - **役割**: Web コアサーバー。データキャッシュ、バージョン管理（known_rev）、API ルートを管理します。
   - **主要機能**: 状態集約、設定の永続化、エラーのページネーションクエリ、タスク注入の中継。

2. **routes/**
   - **役割**: ホームページ、Pull API、Push API を組み立てます。

3. **runtime/**
   - **役割**: `config.json` の読み書き、Pydantic モデル、SQLite 操作、パラメータ正規化ユーティリティを提供します。

### コアフロントエンドコンポーネント

フロントエンド TypeScript ソースファイルは `src/celestialflow_web/static/ts/` にあり、JS にコンパイルされた後 `templates/index.html` によって読み込まれます：

1. **main.ts** — グローバル入口とポーリング調整
2. **utils.ts** — 汎用ユーティリティ関数
3. **i18n.ts** — 国際化サポート
4. **web_config.ts** — 設定管理ロジック + カード DOM 注入（モジュール読み込み時に `ensureAllCards()` を呼び出し）
5. **loaders.ts** — データ層：状態/グラフメタ情報の取得、バージョンガードとローカル派生
6. **util_estimators.ts** — グラフレベルの派生指標推定（グローバルな待機処理量、推定残り時間）
7. **types.d.ts** — フロントエンド/バックエンドの契約型宣言（純粋な型のみ、JS は生成しない）
8. **dashboard_statuses.ts** — 動的ノードカードをレンダリングし、各ステージのリアルタイム性能指標とプログレスバーを表示
9. **dashboard_structure.ts** — Mermaid.js ベースでタスクグラフトポロジ構造をレンダリングし、動的ノード着色をサポート
10. **dashboard_history.ts** — 複数指標の履歴シーケンスを保持し、Chart.js で進捗折れ線グラフをレンダリング
11. **dashboard_summary.ts** — グローバル統計ダッシュボードのレンダリングと更新
12. **dashboard_analysis.ts** — トポロジ分析情報の表示
13. **dashboard_error_types.ts** — エラータイプ分布の doughnut 図と凡例
14. **errors.ts** — エラーログのページネーション表示と詳細フィルタリング
15. **injection.ts** — 手動タスク注入 UI を管理し、複数ノードの一括注入をサポート
16. **layout_editor.ts** — カードレイアウトエディタ（web_config の CARD_TEMPLATES/PANEL_SELECTOR_MAP に依存）

## アーキテクチャの特徴

### クライアント側の履歴蓄積
フロントエンド/バックエンドの通信頻度を大幅に下げるため、履歴トレンドデータはバックエンドから全量プッシュされず、フロントエンドが連続する状態スナップショット（Status Snapshot）に基づいてブラウザメモリ内で自ら蓄積・維持します。

### 増分取得メカニズム
すべての取得インターフェース（`pull_*`）は `known_rev` メカニズムをサポートします。バックエンドのデータバージョンが変化した場合のみ実際の Payload を転送し、そうでなければバージョン番号のみを返すため、ポーリング帯域を大幅に節約できます。

### 設定の永続化
バックエンドは起動時にパッケージ内の `config.json` を読み込み、`WebConfigModel` で検証します。フロントエンドが設定を変更すると、バックエンドは最新の設定を同じファイルに書き戻します。

## 使用パターン

### サーバーの起動
```bash
# コマンドラインツールを直接実行
celestialflow-web --port 5000
```

### タスク注入の例
```python
import requests

# 指定ノードへ注入待ちタスクを上書き書き込み（形式：{ノード名: [タスクリスト]}）
requests.post(
    "http://localhost:5000/api/push_injection_tasks",
    json={"Stage_A": [{"id": 1, "data": "payload"}]},
)
```

## 使用例

### TaskWebServer の作成と起動の基本例

```python
from celestialflow_web import TaskWebServer

# サーバーインスタンスを作成
server = TaskWebServer(
    host="127.0.0.1",  # リッスンアドレス
    port=5000,  # リッスンポート
    log_level="info",  # ログレベル
)

# サーバーを起動（ブロッキング呼び出し、ずっと動作し続ける）
server.start_server()
```

起動後、ブラウザで `http://127.0.0.1:5000` にアクセスすると Web UI 監視ダッシュボードが表示されます。

### CelestialFlow ランタイムとの連携例

```python
from celestialflow import TaskGraph, TaskStage
from celestialflow.persistence import LogInlet
from celestialflow.observability import TaskReporter
import asyncio

from celestialflow_web import TaskWebServer


async def main():
    # 1. まず Web サーバーを起動（バックグラウンドスレッドで動作）
    server = TaskWebServer(host="127.0.0.1", port=5000, log_level="info")
    # 実際の本番環境では server.start_server() はブロッキングするため、
    # ここでは reporter と server が連携するフローを示す

    # 2. タスクグラフを作成
    def process(x: int) -> int:
        return x * 2

    graph = TaskGraph(name="DemoGraph", schedule_mode="eager")
    stage = TaskStage("Processor", process, execution_mode="thread")
    graph.set_stages([stage])

    # 3. TaskReporter を作成して起動
    log_inlet = LogInlet()
    reporter = TaskReporter(
        host="127.0.0.1",
        port=5000,
        task_graph=graph,
        log_inlet=log_inlet,
    )
    reporter.start()

    # 4. タスクを実行
    graph.start_graph({stage.get_name(): range(50)})

    # 5. レポーターを停止
    reporter.stop()


asyncio.run(main())
```

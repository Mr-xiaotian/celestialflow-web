# tests/conftest.py

> 📅 最終更新日: 2026/09/24

## 役割
`tests/` ディレクトリ配下のテストケースに Web サーバーと HTTP クライアントの Pytest Fixture を提供し、実際のフロントエンド/バックエンドのインタラクション環境を模擬します。

## コア Fixture
- `web_server`:
  - **機能**: デフォルト設定の `TaskWebServer` インスタンスを初期化します。
  - **スコープ**: 各テスト関数の実行前に新しいインスタンスを作成します。
- `client`:
  - **機能**: `FastAPI.testclient.TestClient` に基づいて同期 HTTP クライアントを作成します。
  - **依存**: `web_server` fixture に依存し、その内部の `app` インスタンスに直接アクセスします。

## 使用例
```python
def test_index_page(client):
    """ホームページがアクセス可能で、重要なコンテナを含むことを検証する。"""
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="dashboard"' in response.text
```

## 注意事項
- テストは FastAPI 組み込みの TestClient を使用し、実際のポートリッスンは起動しないため、実行効率が高くポート競合のリスクもありません。
- 関連する実装は `src/celestialflow_web/server/core_server.py` にあります。

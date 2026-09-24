# src/celestialflow_web/runtime/__init__.py

> 📅 最終更新日: 2026/09/24

## 役割

`celestialflow_web.runtime` は Web サービスのランタイム依存のユーティリティ関数、データモデル、SQLite アクセス関数を集約し、統一したエクスポートを外部に提供して、`server/` と `routes/` から呼び出せるようにします。

## 公開エクスポート

| シンボル | 出所 | 説明 |
|------|------|------|
| `WebConfigModel` | `util_models.py` | フロントエンドのグループ設定モデル |
| `append_records` | `util_sqlite.py` | エラー記録を追記 |
| `cal_interval` | `util_cal.py` | ミリ秒のリフレッシュ間隔を秒に正規化 |
| `clear_records` | `util_sqlite.py` | エラー記録をクリア |
| `connect_db` | `util_sqlite.py` | SQLite 接続を開く |
| `get_max_event_id_in_fail` | `util_sqlite.py` | 失敗記録の最大 `event_id` をクエリ |
| `load_config` | `util_config.py` | `config.json` を読み込んで解析 |
| `load_records` | `util_sqlite.py` | すべてのエラー記録を読み込む |
| `query_error_type_counts` | `util_sqlite.py` | エラータイプのカウントを集計 |
| `query_records` | `util_sqlite.py` | エラー記録をページネーションでクエリ |

## `__all__`

```python
__all__ = [
    "WebConfigModel",
    "append_records",
    "cal_interval",
    "clear_records",
    "connect_db",
    "get_max_event_id_in_fail",
    "load_config",
    "load_records",
    "query_error_type_counts",
    "query_records",
]
```

## 使用例

```python
from celestialflow_web.runtime import WebConfigModel, cal_interval, load_config

config = WebConfigModel.model_validate(load_config("src/celestialflow_web/config.json"))
interval = cal_interval(config.global_.refreshInterval)
print(interval)
```

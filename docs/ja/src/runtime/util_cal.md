# src/celestialflow_web/runtime/util_cal.py

> 📅 最終更新日: 2026/09/24

Web モジュールの軽量計算とクエリパラメータ正規化ユーティリティ。

## cal_interval

```python
def cal_interval(refresh_interval: int) -> float:
    """ミリ秒のリフレッシュ間隔を秒に換算し、[1.0, 60.0] の範囲に制限する。"""
```

フロントエンドから渡されたミリ秒単位のリフレッシュ間隔を秒に変換し、妥当な範囲に制限します。ポーリング頻度が高すぎてサーバー負荷が大きくなったり、低すぎてデータ遅延が生じたりするのを防ぎます。

## normalize_errors_query

```python
def normalize_errors_query(
    page: int, page_size: int, node: str, keyword: str, sort_order: str
) -> tuple[int, int, str, str, str]:
    """エラークエリパラメータを正規化する。"""
```

- `page` を最小1に正規化します。
- `page_size` を `[1, 200]` に制約します。
- `node` / `keyword` の前後の空白を除去し、`keyword` を小文字に変換します。
- `sort_order` は `"newest"` または `"oldest"` のみ許可し、それ以外の値は一律 `"newest"` にフォールバックします。

現在 `routes/core_pull.py` は本モジュールから直接 `normalize_errors_query()` をインポートし、`/api/pull_errors` のパラメータクリーニングに使用しています。

## 使用例

### リフレッシュ間隔換算関数の使用例

```python
from celestialflow_web.runtime.util_cal import cal_interval

# 5000ms -> 5.0s（標準の5秒リフレッシュ）
print(f"5000ms -> {cal_interval(5000)}s")  # 5.0

# 1000ms -> 1.0s（下限1秒）
print(f"1000ms -> {cal_interval(1000)}s")  # 1.0

# 500ms -> 1.0s（下限未満のため 1.0 に制限）
print(f"500ms  -> {cal_interval(500)}s")  # 1.0

# 120000ms -> 60.0s（上限超過のため 60.0 に制限）
print(f"120000ms -> {cal_interval(120000)}s")  # 60.0

# 境界：ちょうど上限に等しい
print(f"60000ms -> {cal_interval(60000)}s")  # 60.0

# 典型的な Web UI のリフレッシュ間隔設定
refresh_options_ms = [1000, 2000, 5000, 10000, 30000]
print("\n一般的なリフレッシュ間隔の変換:")
for ms in refresh_options_ms:
    seconds = cal_interval(ms)
    print(f"  {ms:>6}ms -> {seconds:.1f}s")
# 出力：
#    1000ms -> 1.0s
#    2000ms -> 2.0s
#    5000ms -> 5.0s
#   10000ms -> 10.0s
#   30000ms -> 30.0s
```

### エラークエリパラメータ正規化の例

```python
from celestialflow_web.runtime.util_cal import normalize_errors_query

page, page_size, node, keyword, sort_order = normalize_errors_query(
    page=0,
    page_size=999,
    node=" StageA ",
    keyword=" Timeout ",
    sort_order="invalid",
)

print(page)  # 1
print(page_size)  # 200
print(node)  # "StageA"
print(keyword)  # "timeout"
print(sort_order)  # "newest"
```

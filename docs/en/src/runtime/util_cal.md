# src/celestialflow_web/runtime/util_cal.py

> 📅 Last Updated: 2026/09/24

Lightweight computation and query parameter normalization utilities for the Web module.

## cal_interval

```python
def cal_interval(refresh_interval: int) -> float:
    """Convert a millisecond refresh interval to seconds, clamped to the range [1.0, 60.0]."""
```

Converts the millisecond-level refresh interval passed in by the frontend to seconds and clamps it to a reasonable range, preventing the polling frequency from being too high (which would overload the server) or too low (which would delay data).

## normalize_errors_query

```python
def normalize_errors_query(
    page: int, page_size: int, node: str, keyword: str, sort_order: str
) -> tuple[int, int, str, str, str]:
    """Normalize error query parameters."""
```

- Normalizes `page` to a minimum of 1.
- Constrains `page_size` to `[1, 200]`.
- Trims leading and trailing whitespace from `node` / `keyword`, and lowercases `keyword`.
- `sort_order` only allows `"newest"` or `"oldest"`; any other value falls back to `"newest"`.

Currently `routes/core_pull.py` imports `normalize_errors_query()` directly from this module to sanitize the parameters of `/api/pull_errors`.

## Usage Examples

### Example of Using the Refresh Interval Conversion Function

```python
from celestialflow_web.runtime.util_cal import cal_interval

# 5000ms -> 5.0s (standard 5-second refresh)
print(f"5000ms -> {cal_interval(5000)}s")  # 5.0

# 1000ms -> 1.0s (lower bound of 1 second)
print(f"1000ms -> {cal_interval(1000)}s")  # 1.0

# 500ms -> 1.0s (below the lower bound, clamped to 1.0)
print(f"500ms  -> {cal_interval(500)}s")  # 1.0

# 120000ms -> 60.0s (above the upper bound, clamped to 60.0)
print(f"120000ms -> {cal_interval(120000)}s")  # 60.0

# Boundary: exactly equal to the upper bound
print(f"60000ms -> {cal_interval(60000)}s")  # 60.0

# Typical Web UI refresh interval configuration
refresh_options_ms = [1000, 2000, 5000, 10000, 30000]
print("\nCommon refresh interval conversions:")
for ms in refresh_options_ms:
    seconds = cal_interval(ms)
    print(f"  {ms:>6}ms -> {seconds:.1f}s")
# Output:
#    1000ms -> 1.0s
#    2000ms -> 2.0s
#    5000ms -> 5.0s
#   10000ms -> 10.0s
#   30000ms -> 30.0s
```

### Example of Normalizing Error Query Parameters

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

# runtime/util_cal.py
def cal_interval(refresh_interval: int) -> float:
    """
    将毫秒刷新间隔换算为秒，并限制在 [1, 60] 范围内。

    :param refresh_interval: 刷新间隔（毫秒）
    :return: 限制在 [1, 60] 范围内的秒数
    """
    return max(1.0, min(float(refresh_interval) / 1000.0, 60.0))


def normalize_errors_query(
    page: int, page_size: int, node: str, keyword: str, sort_order: str
) -> tuple[int, int, str, str, str]:
    """
    归一化错误查询参数，返回归一化后的页面、每页大小、节点和关键词。

    :param page: 页码
    :param page_size: 每页大小
    :param node: 节点名称
    :param keyword: 搜索关键词
    :param sort_order: 排序方式
    :return: (归一化页码, 归一化每页大小, 归一化节点名, 归一化关键词, 排序方式)
    """
    normalized_page_size = max(1, min(int(page_size), 200))
    normalized_page = max(1, int(page))
    normalized_node = node.strip()
    normalized_keyword = keyword.strip().lower()
    normalized_sort_order = sort_order.strip().lower()
    if normalized_sort_order not in {"newest", "oldest"}:
        normalized_sort_order = "newest"
    return (
        normalized_page,
        normalized_page_size,
        normalized_node,
        normalized_keyword,
        normalized_sort_order,
    )

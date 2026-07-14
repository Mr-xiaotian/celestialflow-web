# Subagent Prompt - Runtime

你负责 `src/runtime` 区域的中文文档同步。

## 负责范围

- `src/celestialflow_web/runtime/*.py`
- 对应的 `docs/zh-CN/src/runtime/*.md`

## 重点检查

- `__init__.py` 导出列表是否与文档一致
- `util_cal.py`、`util_config.py`、`util_errors.py`、`util_models.py`、`util_sqlite.py` 的函数、模型与示例是否匹配当前代码
- 参数校验、返回值、异常行为、默认值是否准确
- 是否仍引用旧平铺模块路径或主仓库路径

## 输出补充要求

- 如果发现重复实现、未使用导出、命名摇摆等代码现象，可以在“代码-文档不一致问题”之外，单独作为“附带发现”列出
- 不要为了文档一致性而改写代码语义；以当前代码实际行为为准

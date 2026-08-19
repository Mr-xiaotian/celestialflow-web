# Web 测试包

> 📅 最后更新日期: 2026/08/19

## 作用
`tests/` 覆盖 CelestialFlow Web 层的接口与页面集成行为，确保状态快照隔离、状态拉取推送、配置推送、任务注入、错误分页过滤、图上下文切换及过期推送忽略保持稳定。

## 包含的文件
- `__init__.py`: 空文件，仅用于将 `tests/` 标识为 Python 包，不包含任何测试代码或共享逻辑。
- `conftest.py`: 提供 `web_server` 和 `client` 两个 Pytest Fixture。
- `test_server.py`: 覆盖快照隔离、仪表盘首页、配置 API、状态同步、任务注入及错误分页等 Web API 集成测试。

## 运行方式

```bash
# 全部执行
uv run pytest tests -v

# 仅运行 server 集成测试
uv run pytest tests/test_server.py -v
```

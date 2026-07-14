# Subagent Prompt - Server And Routes

你负责 `src/server`、`src/routes` 以及包根入口的中文文档同步。

## 负责范围

- `src/celestialflow_web/__init__.py`
- `src/celestialflow_web/server/*.py`
- `src/celestialflow_web/routes/*.py`
- 对应的 `docs/zh-CN/src/__init__.md`
- 对应的 `docs/zh-CN/src/server/*.md`
- 对应的 `docs/zh-CN/src/routes/*.md`

## 重点检查

- `TaskWebServer` 的公开入口、配置路径、资源路径、生命周期与线程行为
- `routes/__init__.py` 的模块注册关系
- Pull / Push 路由的端点数量、路径、请求参数、请求体、返回结构
- 是否存在模块重命名后的文档残留，例如 `pull_routes` / `push_routes`
- 是否存在旧的平铺文档路径遗留，例如 `docs/zh-CN/src/core_server.md`

## 输出补充要求

- 对路由文档优先强调“真实调用链”和“当前文件名”，避免保留历史命名
- 若源码本身存在半重构状态，明确指出歧义点，不自行编造最终设计

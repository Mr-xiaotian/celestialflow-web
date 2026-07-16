# Push 路由（POST）— `core_push`

> 📅 最后更新日期: 2026/07/16

## 作用

`core_push` 模块提供 **Reporter（上报端）** 与前端向服务端**推送**数据的全部 POST 端点。每次推送会更新对应的内存存储并递增版本号（`store_revs`），使客户端通过 Pull 路由感知到数据变化。

## 核心函数

### `register(router: APIRouter, server: TaskWebServer, config_path: str) -> None`

在给定的 `APIRouter` 上注册全部 7 个 POST 端点。

| 参数 | 类型 | 说明 |
|------|------|------|
| `router` | `APIRouter` | FastAPI 路由器实例 |
| `server` | `TaskWebServer` | 持有共享状态的 Web 服务器实例 |
| `config_path` | `str` | 配置文件磁盘路径，用于持久化配置 |

---

## 端点

### 1. `POST /api/push_config`

保存前端配置并同步更新 `server.report_interval`。

处理流程：

```mermaid
flowchart LR
    A[WebConfigModel 请求体] --> B[model_dump by_alias]
    B --> C[更新 server.config]
    C --> D[cal_interval refreshInterval]
    D --> E[更新 server.report_interval]
    E --> F[save_config]
```

> 注意：当前实现会先更新内存中的配置，再尝试写盘；如果 `save_config()` 失败，请求会返回 500，但进程内配置仍已更新。

### 2. `POST /api/push_injection_tasks`

接收前端任务注入请求，请求体为 `TaskInjectionModel`，格式为 `{node_name: [tasklist]}`。

- 逐节点写入 `server.injection_tasks`
- 同一节点的新任务列表会覆盖旧值（**按节点覆盖**，非追加）
- 整个写入过程由 `task_injection_lock` 保护
- 失败时返回 `JSONResponse({"ok": False, "msg": ...}, 500)`

### 3. `POST /api/push_injection_terminations`

接收终止符注入请求，请求体为 `TerminationInjectionModel`，格式为 `[node_name, ...]`。

- 写入 `server.injection_terminations`
- 采用集合语义，重复节点会自动去重
- 失败时返回 `JSONResponse({"ok": False, "msg": ...}, 500)`

### 4. `POST /api/push_structure`

Reporter 推送图结构快照。

- 仅当 `graph_id` 与当前 graph 上下文一致时才写入
- 成功写入后递增 `store_revs["structure"]`

### 5. `POST /api/push_analysis`

Reporter 推送图分析结果。

- 校验 `graph_id`
- 写入 `analysis_store`
- 递增 `store_revs["analysis"]`

### 6. `POST /api/push_status`

Reporter 推送节点状态快照。

- 校验 `graph_id`
- 更新 `status_timestamp` 与 `status_store`
- 递增 `store_revs["status"]`

### 7. `POST /api/push_errors`

Reporter 推送错误记录列表。

- 校验 `graph_id`
- 调用 `append_records()` 写入 SQLite
- 递增 `store_revs["errors"]`

---

## 关键细节

- 所有 reporter 侧 Push 接口都依赖 `server.is_current_graph(data.graph_id)` 做 graph 上下文校验。
- `push_injection_tasks` 和 `push_injection_terminations` 面向前端，当前实现不要求 `graph_id`。
- `push_config` 使用 `runtime.util_cal.cal_interval()` 把毫秒刷新间隔归一化为 `[1.0, 60.0]` 秒。

## 使用示例

### 前端保存配置

```javascript
const resp = await fetch("/api/push_config", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    global: {
      theme: "dark",
      autoRefreshEnabled: true,
      refreshInterval: 10000,
      language: "zh-CN",
    },
    dashboard: {
      historyLimit: 20,
      showStructureEdgeDelta: false,
      useTotalPendingInStatus: false,
      layout: { left: ["mermaid"], middle: ["status"], right: ["progress"] },
    },
    errors: {
      pageSize: 10,
      sortOrder: "newest",
      jumpToInjectionAfterRetry: true,
    },
    injection: {
      showInjectableOnly: true,
    },
  }),
});
console.log(await resp.json());
```

### Reporter 推送状态

```python
import requests

requests.post(
    "http://localhost:5000/api/push_status",
    json={
        "graph_id": "graph-001",
        "timestamp": 1716883200.5,
        "status": {
            "StageA": {"tasks_succeeded": 10, "tasks_failed": 0},
        },
    },
    timeout=3,
)
```

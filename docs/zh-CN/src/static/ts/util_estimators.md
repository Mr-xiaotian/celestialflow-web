# src/celestialflow_web/static/ts/util_estimators.ts

> 📅 最后更新日期: 2026/09/24

图级派生指标估算模块。前端自有的图级估算：仅依赖同一次状态快照中的原始计数与静态拓扑，推算各节点的全局待处理任务量与预计剩余时间。

## 类型定义

```typescript
/** 有向边邻接表：{上游节点: [下游节点, ...]} */
type GraphEdges = Record<string, string[]>;

/** 以节点名为键的计数映射 */
export type CountMap = Record<string, number>;

/** 每节点发往各下游的任务数：{上游节点: {下游节点: 任务数}} */
export type DownstreamMap = Record<string, Record<string, number>>;

/** 图拓扑索引：节点全集与前驱邻接表 */
type GraphIndex = {
  nodes: string[];                        // 全量节点名，与边表键集一致
  predecessors: Record<string, string[]>; // 每个节点的前驱列表
};
```

## 函数

### `calcGlobalPending(edges, processedMap, pendingMap, downstreamMap): CountMap`

基于任务图（DAG）估算各节点全局待处理任务数量（偏保守 / 拥塞放大型）。

**算法：** 对每个上游-下游组合维护独立放大系数：

```
scale[u][w] = total_u * output_u->w / max(1, proc_u)
```

其中 `output_u->w / proc_u` 为 u 对 w 的产出比，取自 u 自身的单次快照（与 `proc_u` 同源一致），避免跨节点快照时间差的影响。据此递推每个节点的预计总输入量：

```
total_v = external_v + sum(scale[u][v] for u in preds(v))
```

其中 `external_v = max(0, seen_v - sum(output_u->v))` 为外部注入任务数，不参与上游放大；`seen_v = processed_v + pending_v`。预计剩余任务数为 `max(pending_v, total_v - processed_v)`。

按拓扑序单趟传播：处理任一节点时其全部前驱均已定型。若传入的图不是 DAG（`topoSort()` 返回 `null`），会抛出 `Error("calcGlobalPending() requires a DAG edges map")` —— 调用方（`loaders.ts`）会先用 `analysis.isDAG` 判定，非 DAG 时退化为节点自身待处理量，不调用本函数。

| 参数 | 类型 | 说明 |
|------|------|------|
| `edges` | `GraphEdges` | 有向边邻接表，节点需与 map 的 key 对应 |
| `processedMap` | `CountMap` | 每个节点已完成的任务数量 |
| `pendingMap` | `CountMap` | 每个节点当前剩余的任务数量 |
| `downstreamMap` | `DownstreamMap` | 每个节点实际发送给各下游的任务数量，缺失节点或下游按 0 处理 |

**返回：** `CountMap`，估算得到的各节点全局待处理任务数量。

### `calcRemaining(processed, pending, elapsed): number`

基于已处理任务、剩余任务以及已消耗时间计算预计剩余时间：`pending / processed * elapsed`。当 `processed` 或 `pending` 为 0 时返回 `0`。

| 参数 | 类型 | 说明 |
|------|------|------|
| `processed` | `number` | 已处理任务数 |
| `pending` | `number` | 待处理任务数 |
| `elapsed` | `number` | 已消耗时间（秒） |

## 内部辅助函数（不导出）

- `buildGraphIndex(edges)`：构建节点全集与前驱邻接表。
- `topoSort(edges)`：对邻接表执行 Kahn 拓扑排序；图中存在环时返回 `null`。

## 使用示例

```typescript
import { calcGlobalPending, calcRemaining } from "./util_estimators.js";

const edges = { A: ["B"], B: ["C"], C: [] };
const processed = { A: 100, B: 80, C: 50 };
const pending = { A: 10, B: 20, C: 5 };
const downstream = { A: { B: 100 }, B: { C: 80 }, C: {} };

const totalPending = calcGlobalPending(edges, processed, pending, downstream);
// totalPending["C"] 为含上游链路的全局待处理量估计

const remaining = calcRemaining(processed["B"], totalPending["B"], 3600);
console.log(totalPending, remaining);
```

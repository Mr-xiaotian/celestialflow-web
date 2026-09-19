/**
 * 图级派生指标估算模块
 * 前端自有的图级估算：仅依赖同一次状态快照中的原始计数与静态拓扑，
 * 推算各节点的全局待处理任务量与预计剩余时间。
 */
/**
 * 构建拓扑索引
 * @param {GraphEdges} edges - 有向边邻接表
 * @returns {GraphIndex} 节点全集与前驱邻接表
 */
function buildGraphIndex(edges) {
    const nodes = Object.keys(edges);
    const predecessors = {};
    for (const node of nodes) {
        predecessors[node] = [];
    }
    for (const [from, toNames] of Object.entries(edges)) {
        for (const to of toNames) {
            predecessors[to].push(from);
        }
    }
    return { nodes, predecessors };
}
/**
 * 对邻接表执行 Kahn 拓扑排序
 * @param {GraphEdges} edges - 有向边邻接表
 * @returns {string[] | null} 拓扑序；图中存在环时返回 `null`
 */
function topoSort(edges) {
    const { nodes, predecessors } = buildGraphIndex(edges);
    const inDegree = {};
    for (const node of nodes) {
        inDegree[node] = predecessors[node].length;
    }
    const queue = nodes.filter((node) => inDegree[node] === 0);
    const order = [];
    for (let cursor = 0; cursor < queue.length; cursor++) {
        const node = queue[cursor];
        order.push(node);
        for (const next of edges[node]) {
            inDegree[next] -= 1;
            if (inDegree[next] === 0) {
                queue.push(next);
            }
        }
    }
    return order.length === nodes.length ? order : null;
}
/**
 * 基于任务图（DAG）估算各节点全局待处理任务数量（偏保守 / 拥塞放大型）
 *
 * 对每个上游-下游组合维护独立放大系数：
 *
 *     scale[u][w] = total_u * output_u->w / max(1, proc_u)
 *
 * 其中 `output_u->w / proc_u` 为 u 对 w 的产出比，取自 u 自身的单次快照（与 `proc_u`
 * 同源一致），避免跨节点快照时间差的影响。据此递推每个节点的预计总输入量：
 *
 *     total_v = external_v + sum(scale[u][v] for u in preds(v))
 *
 * 其中 `external_v = max(0, seen_v - sum(output_u->v))` 为外部注入任务数，不参与上游
 * 放大；`seen_v = processed_v + pending_v`。预计剩余任务数为
 * `max(pending_v, total_v - processed_v)`。
 *
 * 按拓扑序单趟传播：处理任一节点时其全部前驱均已定型。
 *
 * @param {GraphEdges} edges - 有向边邻接表，节点需与 map 的 key 对应
 * @param {CountMap} processedMap - 每个节点已完成的任务数量
 * @param {CountMap} pendingMap - 每个节点当前剩余的任务数量
 * @param {DownstreamMap} downstreamMap - 每个节点实际发送给各下游的任务数量，缺失节点或下游按 0 处理
 * @returns {CountMap} 估算得到的全局待处理任务数量
 */
export function calcGlobalPending(edges, processedMap, pendingMap, downstreamMap) {
    const topoOrder = topoSort(edges);
    if (topoOrder === null) {
        throw new Error("calcGlobalPending() requires a DAG edges map");
    }
    const { predecessors } = buildGraphIndex(edges);
    const expectedPending = {};
    const scale = {};
    for (const node of topoOrder) {
        const processed = Math.trunc(processedMap[node] || 0);
        const pending = Math.trunc(pendingMap[node] || 0);
        const seen = processed + pending;
        const preds = predecessors[node];
        let total;
        if (!preds.length) {
            // 没有上游时，总量就等于当前观测到的任务量
            total = seen;
        }
        else {
            // 上游已发送量即为本节点已接收量（共享计数），据此拆分外部注入
            let receivedSum = 0;
            for (const pred of preds) {
                receivedSum += downstreamMap[pred]?.[node] || 0;
            }
            const external = Math.max(0, seen - receivedSum);
            // 外部注入不参与上游放大；上游部分累加各上游的预计输出量
            let upstreamTotal = 0;
            for (const pred of preds) {
                upstreamTotal += scale[pred][node];
            }
            total = external + upstreamTotal;
        }
        // 本节点对各下游的预计输出量：产出比取自本节点自身快照，processed 与输出同源
        const targets = edges[node];
        const nodeScale = {};
        for (const target of targets) {
            const output = downstreamMap[node]?.[target] || 0;
            nodeScale[target] = (total * output) / Math.max(1, processed);
        }
        scale[node] = nodeScale;
        // 理论上预计值不会小于当前值
        expectedPending[node] = Math.trunc(Math.max(pending, total - processed));
    }
    return expectedPending;
}
/**
 * 基于已处理任务、剩余任务以及已消耗时间来计算剩余时间
 * @param {number} processed - 已处理任务数
 * @param {number} pending - 待处理任务数
 * @param {number} elapsed - 已消耗时间（秒）
 * @returns {number} 预计剩余时间（秒）；已处理或待处理为 0 时返回 0
 */
export function calcRemaining(processed, pending, elapsed) {
    if (processed && pending) {
        return (pending / processed) * elapsed;
    }
    return 0;
}

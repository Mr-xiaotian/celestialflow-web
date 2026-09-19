"use strict";
/**
 * 数据层：模型状态与拉取
 *
 * 负责指标数据的拉取、版本守卫与本地派生。渲染模块只读取这里暴露的全局变量，
 * 不自行发起请求 —— 这样"数据从哪来"与"数据怎么画"不再混在同一个文件里。
 *
 * 契约类型见 types.d.ts；命名以 `load*` 开头的函数是唯一的网络入口。
 */
// ==== 节点状态模型 ====
let nodeStatuses = {}; // 当前各节点运行状态
let lastNodeStatuses = {}; // 上一轮状态快照，用于计算增量
let nodeEstimates = {}; // 本轮图级派生值，与 nodeStatuses 同步轮转
let lastNodeEstimates = {}; // 上一轮派生值，用于计算增量
let statusRev = -1; // 上次拉取的数据版本号，-1 表示首次拉取全量
let statusesRequestSeq = 0; // 请求序列号，防止旧状态响应覆盖新结果
let lastStatusTimestamp = 0; // 最近一次状态快照的统一时间戳，供历史曲线记录使用
// ==== 图元信息模型 ====
let graphMeta = {
    nodes: [],
    edges: {},
    source_nodes: [],
    node_meta: {},
    analysis: null,
}; // 图元信息（有向图 + 节点元信息 + 分析结果）
let graphMetaRev = -1; // 数据版本号，用于增量拉取
let graphMetaRequestSeq = 0; // 请求序列号，防止旧图元信息响应覆盖新结果
/**
 * 异步加载最新的节点状态数据
 * 从后端 API 获取节点状态并更新全局变量；全局估算与历史曲线同步由 `refreshAll` 收口处理
 * @returns {Promise<boolean>} 当状态版本发生变化并成功更新时返回 `true`，否则返回 `false`。
 */
async function loadStatuses() {
    try {
        const requestSeq = ++statusesRequestSeq; // 为当前状态请求分配递增序号
        const res = await fetch(`/api/pull_status?known_rev=${statusRev}`);
        const body = (await res.json());
        if (requestSeq !== statusesRequestSeq)
            return false; // 丢弃已过时请求的返回结果
        if (body.data === null)
            return false;
        lastNodeStatuses = nodeStatuses;
        nodeStatuses = body.data;
        statusRev = body.rev;
        lastStatusTimestamp = Number(body.timestamp || 0);
        return true;
    }
    catch (e) {
        console.error("状态加载失败", e);
        return false;
    }
}
/**
 * 异步加载最新的图元信息
 * 一次拉取图拓扑、节点构建期元信息与图分析结果，并更新全局变量 graphMeta
 * @returns {Promise<boolean>} 当版本发生变化并成功更新时返回 `true`，否则返回 `false`。
 */
async function loadGraphMeta() {
    try {
        const requestSeq = ++graphMetaRequestSeq; // 为当前请求分配递增序号
        const res = await fetch(`/api/pull_graph_meta?known_rev=${graphMetaRev}`);
        const body = (await res.json());
        if (requestSeq !== graphMetaRequestSeq)
            return false; // 丢弃已过时请求的返回结果
        if (body.data === null)
            return false;
        graphMeta = body.data;
        graphMetaRev = body.rev;
        return true;
    }
    catch (e) {
        console.error("图元信息加载失败", e);
        return false;
    }
}
/**
 * 基于同一快照内的原始计数与静态拓扑，刷新各节点的图级派生值
 *
 * `total_tasks_pending` 与 `total_remaining_time` 需要每个节点的计数与每边输出量，
 * 外加图元信息提供的拓扑与 DAG 判定。图元信息尚未就绪时直接返回，
 * 避免在拓扑缺失时静默算出退化的结果。
 * @returns {void}
 */
function refreshNodeEstimates() {
    const analysis = graphMeta.analysis; // 图分析结果随图元信息一次性到达
    if (!graphMeta.nodes.length || !analysis) {
        return; // 图元信息尚未就绪
    }
    const processedMap = {};
    const pendingMap = {};
    const downstreamMap = {};
    for (const [name, status] of Object.entries(nodeStatuses)) {
        processedMap[name] = Number(status.tasks_processed || 0);
        pendingMap[name] = Number(status.tasks_pending || 0);
        downstreamMap[name] = { ...(status.downstream_counts || {}) };
    }
    // 非 DAG 无法拓扑传播，全局待处理量退化为节点自身的待处理量
    const totalPendingMap = analysis.isDAG
        ? calcGlobalPending(graphMeta.edges, processedMap, pendingMap, downstreamMap)
        : { ...pendingMap };
    const nextEstimates = {};
    for (const [name, status] of Object.entries(nodeStatuses)) {
        const totalPending = totalPendingMap[name];
        nextEstimates[name] = {
            total_tasks_pending: totalPending,
            total_remaining_time: calcRemaining(Number(status.tasks_processed || 0), totalPending, Number(status.elapsed_time || 0)),
        };
    }
    lastNodeEstimates = nodeEstimates;
    nodeEstimates = nextEstimates;
}

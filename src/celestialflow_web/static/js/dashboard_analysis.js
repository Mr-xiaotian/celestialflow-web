/**
 * 拓扑分析展示模块
 * 负责展示图元信息中的图级静态字段（图名称、是否为 DAG、图模式等）；
 * 图级静态字段随图元信息由 loaders.ts 提供，本文件只读不拉。
 *
 * 另外展示当前会话的"最后活跃"时间：该值来自会话心跳而非图分析，
 * 但仅与其余分析信息一同展示，图元信息尚未到达时整个卡片回退到占位提示。
 */
import { t } from "./i18n.js";
import { graphMeta } from "./loaders.js";
import { SESSION_SWITCH_EVENT, SESSIONS_CHANGED_EVENT, getActiveSession, } from "./sessions.js";
import { escapeHtml, formatTimestamp, renderLabelWithTooltip } from "./utils.js";
/**
 * 构建"最后活跃"信息行。
 *
 * 没有活跃会话时返回空串，避免图分析卡片出现一行空值。
 * @returns {string} 该行的 HTML 字符串；无会话时为空串
 */
function renderLastSeenRow() {
    const session = getActiveSession();
    if (!session)
        return "";
    const lastSeen = formatTimestamp(session.last_seen);
    return `
    <div class="analysis-row">
      <span class="analysis-label">${t("analysis.lastSeen")}</span>
      <span class="analysis-value">${escapeHtml(lastSeen)}</span>
    </div>`;
}
/**
 * 渲染分析信息面板
 * 根据 graphMeta 顶层的图级静态字段展示图名称、结构类型、DAG 状态、图模式与启动时间。
 * @returns {void}
 */
export function renderAnalysisInfo() {
    const container = document.getElementById("analysis-info"); // 分析卡片内容容器
    if (!container)
        return;
    if (!graphMeta.nodes.length) {
        // 图元信息未到达时不展示任何行（含最后活跃），只回退到占位提示。
        container.innerHTML = `<div class="empty-placeholder">${t("analysis.noData")}</div>`;
        return;
    }
    const { graph: graphName, start_time: startTime, is_dag: isDAG, graph_mode: graphMode, class_name: className, } = graphMeta; // 解构图级静态字段
    const startTimeText = startTime > 0 ? formatTimestamp(startTime) : "-";
    // 统一构建分析信息内容，避免分散更新不同 DOM 节点。
    container.innerHTML = `
    <div class="analysis-row">
      <span class="analysis-label">${t("analysis.graphName")}</span>
      <span class="analysis-value">${escapeHtml(graphName)}</span>
    </div>

    <div class="analysis-row">
      <span class="analysis-label">${renderLabelWithTooltip("analysis.graphMode", "analysis.graphModeHelp")}</span>
      <span class="analysis-value">${escapeHtml(graphMode)}</span>
    </div>

    <div class="analysis-row">
      <span class="analysis-label">${renderLabelWithTooltip("analysis.structType", "analysis.structTypeHelp")}</span>
      <span class="analysis-value">${escapeHtml(className)}</span>
    </div>

    <div class="analysis-row">
      <span class="analysis-label">${t("analysis.isDAG")}</span>
      <span class="analysis-value ${isDAG ? "ok" : "warn"}">
        ${isDAG ? t("analysis.dagYes") : t("analysis.dagNo")}
      </span>
    </div>

    <div class="analysis-row">
      <span class="analysis-label">${t("analysis.startTime")}</span>
      <span class="analysis-value">${startTimeText}</span>
    </div>

${renderLastSeenRow()}
  `;
}
// 会话切换或会话列表刷新（含心跳更新）后重绘，保证"最后活跃"不会僵住。
document.addEventListener(SESSION_SWITCH_EVENT, () => {
    renderAnalysisInfo();
});
document.addEventListener(SESSIONS_CHANGED_EVENT, () => {
    renderAnalysisInfo();
});

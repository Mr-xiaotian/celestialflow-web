/**
 * 拓扑分析展示模块
 * 负责展示图元信息中的拓扑分析结果（如是否为 DAG、图模式等）；
 * 分析结果随图元信息由 loaders.ts 提供，本文件只读不拉。
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
 * 根据 graphMeta.analysis 在页面上显示结构类型、DAG 状态、图模式和层级数量等信息
 * @returns {void}
 */
export function renderAnalysisInfo() {
    const container = document.getElementById("analysis-info"); // 分析卡片内容容器
    if (!container)
        return;
    const analysis = graphMeta.analysis; // 分析结果随图元信息一次性到达
    if (!analysis) {
        // 分析信息未到达时不展示任何行（含最后活跃），只回退到占位提示。
        container.innerHTML = `<div class="empty-placeholder">${t("analysis.noData")}</div>`;
        return;
    }
    const { name, startTime, isDAG, graphMode, className, layersDict } = analysis; // 解构常用分析字段
    const layerCount = Object.keys(layersDict).length; // 通过层级字典键数推导层级总数
    const startTimeText = startTime > 0 ? formatTimestamp(startTime) : "-";
    // 统一构建分析信息内容，避免分散更新不同 DOM 节点。
    container.innerHTML = `
    <div class="analysis-row">
      <span class="analysis-label">${t("analysis.graphName")}</span>
      <span class="analysis-value">${escapeHtml(name)}</span>
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
      <span class="analysis-label">${t("analysis.layerCount")}</span>
      <span class="analysis-value">${layerCount}</span>
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

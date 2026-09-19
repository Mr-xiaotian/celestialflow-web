"use strict";
/**
 * 拓扑分析展示模块
 * 负责展示图元信息中的拓扑分析结果（如是否为 DAG、图模式等）；
 * 分析结果随图元信息由 loaders.ts 提供，本文件只读不拉。
 */
/**
 * 渲染分析信息面板
 * 根据 graphMeta.analysis 在页面上显示结构类型、DAG 状态、图模式和层级数量等信息
 * @returns {void}
 */
function renderAnalysisInfo() {
    const container = document.getElementById("analysis-info"); // 分析卡片内容容器
    if (!container)
        return;
    const analysis = graphMeta.analysis; // 分析结果随图元信息一次性到达
    if (!analysis) {
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
      <span class="analysis-label">${t("analysis.startTime")}</span>
      <span class="analysis-value">${startTimeText}</span>
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
  `;
}

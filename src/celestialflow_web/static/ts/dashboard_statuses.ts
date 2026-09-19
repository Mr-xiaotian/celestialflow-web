/**
 * 节点状态监控模块
 * 负责各节点运行指标（成功、失败、等待、重复、速率等）的实时展示；
 * 数据由 loaders.ts 提供，本文件只读不拉。
 */

import { t } from "./i18n.js";
import { graphMeta, lastNodeEstimates, lastNodeStatuses, nodeEstimates, nodeStatuses } from "./loaders.js";
import { calcRemaining } from "./util_estimators.js";
import { escapeHtml, formatAvgTime, formatDuration, formatTimestamp, formatWithDelta, renderLabelWithTooltip, switchToErrorsTab } from "./utils.js";
import { webConfig } from "./web_config.js";
import type { NodeEstimate } from "./loaders.js";
import type { NodeStatus } from "./types.js";

type ElapsedSegment = {
  className: string; // 对应的颜色 CSS 类名
  count: number; // 该类型任务数量
};

// DOM 元素引用
const dashboardGrid = document.getElementById("dashboard-grid") as HTMLElement;

/**
 * 根据当前配置获取节点状态卡应展示的等待任务数。
 * @param {NodeStatus} status - 节点状态快照
 * @param {NodeEstimate} [estimate] - 该节点的图级派生值；图元信息就绪前可能缺失
 * @returns {number} 当前节点状态卡使用的等待值
 */
function getDisplayPending(status: NodeStatus, estimate?: NodeEstimate): number {
  if (webConfig.dashboard.useTotalPendingInStatus) {
    return Number(estimate?.total_tasks_pending || 0);
  }
  return Number(status.tasks_pending || 0);
}

/**
 * 根据当前配置获取节点状态卡应展示的剩余时间。
 *
 * 总等待模式使用图级估算的 `total_remaining_time`；否则基于本节点自身的计数就地推算，
 * 不依赖任何额外状态。
 * @param {NodeStatus} status - 节点状态快照
 * @param {NodeEstimate} [estimate] - 该节点的图级派生值；图元信息就绪前可能缺失
 * @returns {number} 当前节点状态卡使用的剩余时间（秒）
 */
function getDisplayRemainingTime(
  status: NodeStatus,
  estimate?: NodeEstimate,
): number {
  if (webConfig.dashboard.useTotalPendingInStatus) {
    return Number(estimate?.total_remaining_time || 0);
  }
  return calcRemaining(
    Number(status.tasks_processed || 0),
    Number(status.tasks_pending || 0),
    Number(status.elapsed_time || 0),
  );
}

/**
 * 获取节点状态卡当前应展示的等待标签 HTML。
 * @returns {string} 等待标签及提示点 HTML
 */
function getPendingLabelHtml(): string {
  return renderLabelWithTooltip(
    webConfig.dashboard.useTotalPendingInStatus
      ? "status.pendingGlobal"
      : "status.pending",
    webConfig.dashboard.useTotalPendingInStatus
      ? "status.pendingGlobalHelp"
      : "status.pendingHelp",
  );
}

/**
 * 将 elapsed 时间格式化为带颜色的 HTML 字符串
 * @param {number} seconds - 秒数
 * @param {number} successCount - 成功任务数
 * @param {number} failedCount - 失败任务数
 * @param {number} duplicateCount - 重复任务数
 * @returns {string} 带颜色分段的时间 HTML
 */
function formatElapsedDuration(
  seconds: number,
  successCount: number,
  failedCount: number,
  duplicateCount: number,
): string {
  const duration = formatDuration(seconds);
  const digitCount = duration.replace(/:/g, "").length;
  if (!digitCount) return duration;

  const segments = getElapsedSegments(
    successCount,
    failedCount,
    duplicateCount,
  );
  if (!segments.length) return duration;
  const digitClasses = buildElapsedDigitClasses(segments, digitCount);
  return renderElapsedDurationHtml(
    duration,
    digitClasses,
    segments[0].className,
  );
}

/**
 * 根据成功、失败、重复任务数生成有效的 elapsed 颜色段
 * @param {number} successCount - 成功任务数
 * @param {number} failedCount - 失败任务数
 * @param {number} duplicateCount - 重复任务数
 * @returns {Array<{ className: string; count: number }>} 有效颜色段列表
 */
function getElapsedSegments(
  successCount: number,
  failedCount: number,
  duplicateCount: number,
): ElapsedSegment[] {
  return [
    { className: "elapsed-success", count: Math.max(0, successCount || 0) },
    { className: "elapsed-error", count: Math.max(0, failedCount || 0) },
    { className: "elapsed-duplicate", count: Math.max(0, duplicateCount || 0) },
  ].filter((segment) => segment.count > 0);
}

/**
 * 按任务状态比例为时间字符串（HH:MM:SS）的每一位分配颜色类
 * @param {Array<{ className: string; count: number }>} segments - 有效颜色段列表
 * @param {number} digitCount - 需要染色的总位数（不含冒号）
 * @returns {string[]} 按顺序排列的 CSS 类名列表
 */
function buildElapsedDigitClasses(
  segments: ElapsedSegment[],
  digitCount: number,
): string[] {
  if (digitCount <= segments.length) {
    return segments.slice(0, digitCount).map((segment) => segment.className);
  }

  const totalCount = segments.reduce((sum, segment) => sum + segment.count, 0);
  const remainingPool = digitCount - segments.length;
  const exactAllocations = segments.map(
    (segment) => (segment.count / totalCount) * remainingPool,
  );
  const allocations = exactAllocations.map((value) => 1 + Math.floor(value));

  const remainingDigits =
    digitCount - allocations.reduce((sum, value) => sum + value, 0);
  const sortedIndexes = exactAllocations
    .map((value, index) => ({ index, remainder: value - Math.floor(value) }))
    .sort((a, b) => {
      if (b.remainder !== a.remainder) return b.remainder - a.remainder;
      return a.index - b.index;
    });

  for (let i = 0; i < remainingDigits; i++) {
    allocations[sortedIndexes[i % sortedIndexes.length].index] += 1;
  }

  const digitClasses: string[] = [];
  allocations.forEach((allocation, index) => {
    for (let i = 0; i < allocation; i++) {
      digitClasses.push(segments[index].className);
    }
  });

  while (digitClasses.length < digitCount) {
    digitClasses.push(segments[segments.length - 1].className);
  }

  return digitClasses;
}

/**
 * 将时间字符串渲染为带颜色 span 的 HTML
 * @param {string} duration - 原始时间字符串
 * @param {string[]} digitClasses - 每一位数字对应的颜色类
 * @param {string} defaultClassName - 当分隔符前没有数字时使用的默认颜色类
 * @returns {string} 渲染后的 HTML 字符串
 */
function renderElapsedDurationHtml(
  duration: string,
  digitClasses: string[],
  defaultClassName: string,
): string {
  let digitIndex = 0;
  return duration
    .split("")
    .map((char) => {
      if (char === ":") {
        const leftClassName =
          digitIndex > 0 ? digitClasses[digitIndex - 1] : defaultClassName;
        return `<span class="${leftClassName}">:</span>`;
      }
      const className =
        digitClasses[digitIndex] || digitClasses[digitClasses.length - 1];
      digitIndex += 1;
      return `<span class="${className}">${char}</span>`;
    })
    .join("");
}

/**
 * 根据节点状态生成 HTML，显示进度条、统计数据等
 * @returns {void}
 */
export function renderDashboard(): void {
  dashboardGrid.innerHTML = "";

  if (!Object.keys(nodeStatuses).length) {
    dashboardGrid.innerHTML = `<div class="empty-placeholder" style="grid-column: 1 / -1;">${t("status.noData")}</div>`;
    return;
  }

  for (const [node, data] of Object.entries(nodeStatuses)) {
    // 计算增量变化
    const last = lastNodeStatuses[node] || ({} as NodeStatus); // 上一轮同节点状态
    const estimate = nodeEstimates[node]; // 当前图级派生值
    const lastEstimate = lastNodeEstimates[node]; // 上一轮图级派生值
    const displayPending = getDisplayPending(data, estimate); // 当前等待值展示字段
    const lastDisplayPending = getDisplayPending(last, lastEstimate); // 上一轮等待值展示字段
    const displayRemainingTime = getDisplayRemainingTime(data, estimate); // 当前剩余时间展示字段
    const addSucceeded = data.tasks_succeeded - (last.tasks_succeeded || 0); // 成功数增量
    const addPending = displayPending - lastDisplayPending; // 等待数增量
    const addFailed = data.tasks_failed - (last.tasks_failed || 0); // 失败数增量
    const addDuplicated = data.tasks_duplicated - (last.tasks_duplicated || 0); // 重复数增量

    const meta = graphMeta.node_meta[node]; // 构建期元信息随图元信息一次性拉取

    // 并行数量：serial 串行模式无并发概念，显示 "-"；元信息缺失时同样显示 "-"
    const parallelismText =
      !meta || meta.execution_mode === "serial" ? "-" : String(meta.max_workers);

    // 计算进度
    const total = data.tasks_processed + displayPending; // 已处理 + 待处理构成总量
    const progressRatio =
      total === 0 ? 0 : Math.floor((data.tasks_processed / total) * 100);

    // 计算四段进度条宽度百分比
    const pctSuccess = total === 0 ? 0 : (data.tasks_succeeded / total) * 100;
    const pctError = total === 0 ? 0 : (data.tasks_failed / total) * 100;
    const pctDuplicate =
      total === 0 ? 0 : (data.tasks_duplicated / total) * 100;
    const pctPending = total === 0 ? 0 : (displayPending / total) * 100;

    const card = document.createElement("div"); // 当前节点状态卡 DOM
    if (data.status === 1) {
      card.className = "node-card status-running";
    } else if (data.status === 2) {
      card.className = "node-card status-stopped";
    } else {
      card.className = "node-card";
    }
    card.innerHTML = `
          <div class="card-header">
            <h3 class="card-title">${escapeHtml(node)}</h3>
          </div>
          <div class="stat-grid">
            <div><div class="stat-label">${t("status.succeeded")}</div><div class="stat-value text-success">${formatWithDelta(
              data.tasks_succeeded,
              addSucceeded,
              "text-delta-success",
              "text-delta-success",
            )}</div></div>
            <div><div class="stat-label">${getPendingLabelHtml()}</div><div class="stat-value text-pending">${formatWithDelta(
              displayPending,
              addPending,
              "text-delta-pending",
              "text-delta-pending",
            )}</div></div>
            <div><div class="stat-label">${t("status.error")}</div><div class="stat-value text-error error-clickable" data-node="${escapeHtml(node)}">${formatWithDelta(
              data.tasks_failed,
              addFailed,
              "text-delta-error",
              "text-delta-error",
            )}</div></div>
            <div><div class="stat-label">${t("status.duplicated")}</div><div class="stat-value text-duplicate">${formatWithDelta(
              data.tasks_duplicated,
              addDuplicated,
              "text-delta-duplicate",
              "text-delta-duplicate",
            )}</div></div>
            <div><div class="stat-label">${renderLabelWithTooltip("status.executionMode", "status.executionModeHelp")}</div><div class="stat-value">${escapeHtml(meta?.execution_mode ?? "-")}</div></div>
            <div><div class="stat-label">${renderLabelWithTooltip("status.parallelism", "status.parallelismHelp")}</div><div class="stat-value">${escapeHtml(parallelismText)}</div></div>
          </div>
          <div class="text-sm text-carbon">${t("status.startTime")}${formatTimestamp(data.start_time)}</div>
          <div class="progress-container">
            <div class="progress-header">
              <span>${t("status.completionRate")}</span>
              <span class="time-estimate">
                <span class="elapsed">${formatElapsedDuration(
                  data.elapsed_time,
                  data.tasks_succeeded,
                  data.tasks_failed,
                  data.tasks_duplicated,
                )}</span>
                &lt;
                <span class="remaining">${formatDuration(displayRemainingTime)}</span>,
                <span class="task-avg-time">${formatAvgTime(
                  data.elapsed_time,
                  data.tasks_processed,
                )}</span>,
                <span class="progress-ratio">${progressRatio}%</span>
              </span>
            </div>
            <div class="progress-bar">
              <div class="progress-segment seg-success"   style="width: ${pctSuccess.toFixed(1)}%"></div>
              <div class="progress-segment seg-error"     style="width: ${pctError.toFixed(1)}%"></div>
              <div class="progress-segment seg-duplicate" style="width: ${pctDuplicate.toFixed(1)}%"></div>
              <div class="progress-segment seg-pending"   style="width: ${pctPending.toFixed(1)}%"></div>
            </div>
          </div>
        `;

    // 为错误数添加点击事件（跳转到错误日志页面并筛选该节点）
    const errorValue = card.querySelector(".error-clickable");
    if (errorValue) {
      errorValue.addEventListener("click", (e) => {
        e.stopPropagation(); // 阻止事件冒泡
        switchToErrorsTab(node); // 使用原始 node 值（非转义）作为筛选器的值
      });
    }

    dashboardGrid.appendChild(card);
  }
}

/**
 * 会话管理模块
 *
 * 服务端按 graph_id 维护多个任务图运行实例会话，本模块负责：
 * - 定期拉取会话列表（`/api/pull_sessions`），维护当前选中的会话
 * - 渲染 header 中的会话选择器并处理切换
 * - 切换会话时广播事件，供各数据模块重置自身累积状态
 *
 * 只有本模块会调用 `/api/pull_sessions`；其余模块通过 `getActiveGraphId()`
 * 读取当前会话标识，并在请求中携带该参数。
 */

import { t } from "./i18n.js";
import type { GraphSession } from "./types.js";

/** 会话列表拉取间隔（毫秒），比状态轮询更慢，避免无谓请求。 */
const SESSIONS_POLL_INTERVAL = 5000;

/** 切换会话时广播的事件名，payload 为新选中的 graph_id。 */
export const SESSION_SWITCH_EVENT = "cf:session-switch";

/** 会话列表变化时广播的事件名，供选择器以外的模块感知。 */
export const SESSIONS_CHANGED_EVENT = "cf:sessions-changed";

// ==== 模块状态 ====
let sessions: GraphSession[] = []; // 服务端当前全部会话
let activeGraphId: string | null = null; // 当前选中的会话标识，null 表示尚无会话
let sessionsFetched = false; // 是否已完成首次拉取，用于区分"空列表"与"尚未拉取"
let sessionsTimer: ReturnType<typeof setInterval> | null = null;
let requestSeq = 0; // 请求序号，防止慢响应覆盖新结果

/**
 * 读取当前选中的会话标识。
 *
 * 数据模块在所有请求中携带该值；为空时服务端会返回 404，页面显示空态。
 *
 * @returns {string | null} 当前会话的 graph_id，未选中时为 null
 */
export function getActiveGraphId(): string | null {
  return activeGraphId;
}

/**
 * 读取当前活跃会话对象。
 *
 * @returns {GraphSession | null} 当前会话，未选中或已被移除时为 null
 */
export function getActiveSession(): GraphSession | null {
  if (!activeGraphId) return null;
  return sessions.find((session) => session.graph_id === activeGraphId) ?? null;
}

/**
 * 为带 graph_id 的接口构造查询参数。
 *
 * @param {Record<string, string | number>} [extra={}] - 额外查询参数
 * @returns {string} 形如 `graph_id=xxx&known_rev=-1` 的查询串；无会话时仅含额外参数
 */
export function withGraphId(
  extra: Record<string, string | number> = {},
): string {
  const params = new URLSearchParams();
  if (activeGraphId) {
    params.set("graph_id", activeGraphId);
  }
  for (const [key, value] of Object.entries(extra)) {
    params.set(key, String(value));
  }
  return params.toString();
}

/**
 * 切换当前选中的会话并广播切换事件。
 *
 * 相同会话不会重复触发；切换后由监听方负责清空本地累积数据并重新拉取。
 *
 * @param {string} graphId - 目标会话的 graph_id
 * @returns {void}
 */
export function setActiveGraphId(graphId: string): void {
  if (activeGraphId === graphId) return;
  activeGraphId = graphId;
  document.dispatchEvent(
    new CustomEvent<string>(SESSION_SWITCH_EVENT, { detail: graphId }),
  );
}

/**
 * 请求服务端移除指定会话（彻底删除其缓存与临时数据库）。
 *
 * 移除成功后立即刷新会话列表；若被移除的正是当前会话，则切换到剩余会话中
 * 最近活跃的一个，没有剩余会话时回到空态。
 *
 * @param {string} graphId - 待移除会话的 graph_id
 * @returns {Promise<boolean>} 是否移除成功
 */
export async function removeSession(graphId: string): Promise<boolean> {
  try {
    const res = await fetch("/api/remove_session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ graph_id: graphId }),
    });
    if (!res.ok) return false;
    await loadSessions();
    return true;
  } catch (e) {
    console.error("会话移除失败", e);
    return false;
  }
}

/**
 * 根据会话列表解析出应当选中的会话标识。
 *
 * 规则：保留仍然存在的当前会话；否则选择最近活跃的会话（优先 alive）。
 *
 * @param {GraphSession[]} list - 最新会话列表
 * @returns {string | null} 应选中的 graph_id
 */
function resolveActiveSession(list: GraphSession[]): string | null {
  if (!list.length) return null;

  if (activeGraphId && list.some((session) => session.graph_id === activeGraphId)) {
    return activeGraphId;
  }

  const aliveSessions = list.filter((session) => session.alive);
  const pool = aliveSessions.length ? aliveSessions : list;
  const latest = pool.reduce((best, current) =>
    current.last_seen > best.last_seen ? current : best,
  );
  return latest.graph_id;
}

/**
 * 根据最新会话列表同步 activeGraphId，并在发生变化时广播切换事件。
 *
 * 与显式用户选择不同，这里的切换同样需要清空各数据模块的累积状态。
 *
 * @param {string | null} nextGraphId - 解析后的目标会话标识
 * @returns {void}
 */
function applyResolvedActive(nextGraphId: string | null): void {
  if (nextGraphId === activeGraphId) return;
  if (nextGraphId === null) {
    activeGraphId = null;
    document.dispatchEvent(
      new CustomEvent<string>(SESSION_SWITCH_EVENT, { detail: "" }),
    );
    return;
  }
  activeGraphId = nextGraphId;
  document.dispatchEvent(
    new CustomEvent<string>(SESSION_SWITCH_EVENT, { detail: nextGraphId }),
  );
}

/**
 * 拉取最新会话列表，并在必要时同步当前选中会话。
 *
 * @returns {Promise<boolean>} 会话列表是否发生变化
 * @returns {Promise<boolean>}
 */
export async function loadSessions(): Promise<boolean> {
  const seq = ++requestSeq;
  try {
    const res = await fetch("/api/pull_sessions");
    if (!res.ok) return false;
    const list = (await res.json()) as GraphSession[];
    if (seq !== requestSeq) return false;

    const changed = JSON.stringify(list) !== JSON.stringify(sessions);
    sessions = list;
    sessionsFetched = true;
    applyResolvedActive(resolveActiveSession(list));
    renderSessionSelector();
    document.dispatchEvent(new Event(SESSIONS_CHANGED_EVENT));
    return changed;
  } catch (e) {
    console.error("会话列表加载失败", e);
    return false;
  }
}

// ==== 选择器渲染 ====

/**
 * 获取会话下拉框。
 *
 * @returns {HTMLSelectElement | null} 下拉框节点（位于设置面板的 Session 分组）
 */
function getSelectEl(): HTMLSelectElement | null {
  return document.getElementById("session-select") as HTMLSelectElement | null;
}

/**
 * 获取会话移除按钮。
 *
 * @returns {HTMLButtonElement | null} 移除按钮节点
 */
function getRemoveBtn(): HTMLButtonElement | null {
  return document.getElementById(
    "session-remove-btn",
  ) as HTMLButtonElement | null;
}

/**
 * 根据会话名生成选择器展示文案。
 *
 * @param {GraphSession} session - 会话对象
 * @returns {string} 展示文本
 */
function formatSessionLabel(session: GraphSession): string {
  return session.name || session.graph_id;
}

/**
 * 渲染设置面板中的会话下拉框与移除按钮状态。
 *
 * 模板已提供静态骨架，这里只更新 `<option>` 列表与禁用态，不重写容器结构，
 * 以免破坏设置面板上的 i18n 属性与其它交互绑定。
 *
 * @returns {void}
 */
export function renderSessionSelector(): void {
  const select = getSelectEl();
  const removeBtn = getRemoveBtn();
  if (!select) return;

  if (!sessions.length) {
    const placeholder = sessionsFetched ? t("session.empty") : t("session.loading");
    select.innerHTML = `<option value="">${escapeHtmlText(placeholder)}</option>`;
    select.disabled = true;
    if (removeBtn) removeBtn.disabled = true;
    return;
  }

  select.innerHTML = sessions
    .map((session) => {
      const selected = session.graph_id === activeGraphId ? " selected" : "";
      const deadTag = session.alive ? "" : " · " + t("session.dead");
      const label = `${formatSessionLabel(session)}${deadTag}`;
      return `<option value="${escapeAttr(session.graph_id)}"${selected}>${escapeHtmlText(label)}</option>`;
    })
    .join("");
  select.disabled = false;
  if (removeBtn) removeBtn.disabled = !getActiveSession();
}

/**
 * 绑定会话下拉框与移除按钮的交互（仅绑定一次）。
 *
 * @returns {void}
 */
function setupSessionControls(): void {
  const select = getSelectEl();
  select?.addEventListener("change", () => {
    setActiveGraphId(select.value);
  });

  const removeBtn = getRemoveBtn();
  removeBtn?.addEventListener("click", async () => {
    const target = getActiveSession();
    if (!target) return;
    const ok = await removeSession(target.graph_id);
    if (!ok) {
      console.warn("会话移除失败", target.graph_id);
    }
  });
}

/**
 * 转义 HTML 文本节点内容。
 *
 * @param {string} str - 原始文本
 * @returns {string} 转义后的文本
 */
function escapeHtmlText(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

/**
 * 转义 HTML 属性值。
 *
 * @param {string} str - 原始属性值
 * @returns {string} 转义后的属性值
 */
function escapeAttr(str: string): string {
  return escapeHtmlText(str).replace(/"/g, "&quot;");
}

/**
 * 启动会话列表的周期轮询。
 *
 * @returns {void}
 */
function startSessionPolling(): void {
  if (sessionsTimer !== null) return;
  sessionsTimer = setInterval(() => {
    void loadSessions();
  }, SESSIONS_POLL_INTERVAL);
}

// 页面加载后立即拉取一次会话列表，并启动周期刷新。
document.addEventListener("DOMContentLoaded", () => {
  setupSessionControls();
  void loadSessions();
  startSessionPolling();
});

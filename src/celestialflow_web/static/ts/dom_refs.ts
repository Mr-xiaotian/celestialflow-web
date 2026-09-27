/**
 * 全局 DOM 元素引用模块
 *
 * 这是一个**无副作用、无依赖**的叶子模块：只做元素查询，不 import 任何其它业务模块。
 * `main.ts` 与 `web_config.ts` 都依赖同一批元素，把查询集中在这里可以避免两者互相
 * import（形成 ESM 循环），也让"元素缺失"的处理方式统一。
 *
 * 这些引用在模块求值期解析，因此 `index.html` 的静态模板必须在此之前就绪——
 * 这是页面入口的固有前提（脚本以 `type="module"` 延迟执行）。
 */

/** 文档中必须存在的元素 id 类型集合。 */
export type RequiredElementId =
  | "refresh-interval"
  | "history-limit"
  | "settings-btn"
  | "settings-panel"
  | "settings-close"
  | "settings-status"
  | "theme-toggle"
  | "language-select"
  | "auto-refresh-toggle"
  | "error-page-size"
  | "error-jump-to-injection-toggle"
  | "structure-edge-label"
  | "status-total-pending-toggle"
  | "injectable-only-toggle"
  | "settings-current-group"
  | "settings-current-label"
  | "settings-current-empty";

/**
 * 查询必须存在的元素；缺失时立即抛出带 id 的错误。
 *
 * 相比 `as HTMLElement` 断言，这里把"模板缺元素"从隐蔽的空引用崩溃
 * 变成启动期一条可读的错误信息。
 *
 * @param {RequiredElementId} id - 元素 id
 * @returns {T} 查询到的元素
 * @raises Error: 元素不存在时抛出
 */
function requireEl<T extends HTMLElement>(id: RequiredElementId): T {
  const el = document.getElementById(id);
  if (!el) {
    throw new Error(`required element not found: #${id}`);
  }
  return el as T;
}

// ==== 全局设置 ====
export const refreshSelect = requireEl<HTMLSelectElement>("refresh-interval"); // 刷新间隔下拉框
export const historyLimitSelect = requireEl<HTMLSelectElement>("history-limit"); // 历史长度下拉框
export const themeToggleBtn = requireEl<HTMLButtonElement>("theme-toggle"); // 主题切换按钮
export const autoRefreshToggle = requireEl<HTMLInputElement>("auto-refresh-toggle"); // 自动刷新开关
export const languageSelect = requireEl<HTMLSelectElement>("language-select"); // 语言选择下拉框

// ==== 仪表盘设置 ====
export const structureEdgeLabelSelect = requireEl<HTMLSelectElement>("structure-edge-label"); // 结构图边标签显示模式
export const statusTotalPendingToggle = requireEl<HTMLInputElement>("status-total-pending-toggle"); // 节点状态卡等待值模式

// ==== 错误页设置 ====
export const errorPageSizeSelect = requireEl<HTMLSelectElement>("error-page-size"); // 错误每页条数
export const errorJumpToInjectionToggle = requireEl<HTMLInputElement>("error-jump-to-injection-toggle"); // 错误页注入后跳转

// ==== 注入页设置 ====
export const injectableOnlyToggle = requireEl<HTMLInputElement>("injectable-only-toggle"); // 仅显示可注入节点

// ==== 设置面板骨架 ====
export const settingsBtn = requireEl<HTMLButtonElement>("settings-btn"); // 设置齿轮按钮
export const settingsPanel = requireEl<HTMLElement>("settings-panel"); // 设置悬浮面板
export const settingsClose = requireEl<HTMLButtonElement>("settings-close"); // 设置面板关闭按钮
export const settingsStatus = requireEl<HTMLElement>("settings-status"); // 设置保存状态提示
export const settingsCurrentGroup = requireEl<HTMLElement>("settings-current-group"); // 当前页设置分组
export const settingsCurrentLabel = requireEl<HTMLElement>("settings-current-label"); // 当前页设置分组标题
export const settingsCurrentEmpty = requireEl<HTMLElement>("settings-current-empty"); // 当前页无专属设置提示

// ==== 页签 ====
export const settingsCurrentItems = document.querySelectorAll<HTMLElement>("[data-settings-tab]"); // 当前页设置项列表
export const tabButtons = document.querySelectorAll<HTMLElement>(".tab-btn"); // 页签按钮列表
export const tabContents = document.querySelectorAll<HTMLElement>(".tab-content"); // 页签内容列表

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
function requireEl(id) {
    const el = document.getElementById(id);
    if (!el) {
        throw new Error(`required element not found: #${id}`);
    }
    return el;
}
// ==== 全局设置 ====
export const refreshSelect = requireEl("refresh-interval"); // 刷新间隔下拉框
export const historyLimitSelect = requireEl("history-limit"); // 历史长度下拉框
export const themeToggleBtn = requireEl("theme-toggle"); // 主题切换按钮
export const autoRefreshToggle = requireEl("auto-refresh-toggle"); // 自动刷新开关
export const languageSelect = requireEl("language-select"); // 语言选择下拉框
// ==== 仪表盘设置 ====
export const structureEdgeLabelSelect = requireEl("structure-edge-label"); // 结构图边标签显示模式
export const statusTotalPendingToggle = requireEl("status-total-pending-toggle"); // 节点状态卡等待值模式
// ==== 错误页设置 ====
export const errorPageSizeSelect = requireEl("error-page-size"); // 错误每页条数
export const errorJumpToInjectionToggle = requireEl("error-jump-to-injection-toggle"); // 错误页注入后跳转
// ==== 注入页设置 ====
export const injectableOnlyToggle = requireEl("injectable-only-toggle"); // 仅显示可注入节点
// ==== 设置面板骨架 ====
export const settingsBtn = requireEl("settings-btn"); // 设置齿轮按钮
export const settingsPanel = requireEl("settings-panel"); // 设置悬浮面板
export const settingsClose = requireEl("settings-close"); // 设置面板关闭按钮
export const settingsStatus = requireEl("settings-status"); // 设置保存状态提示
export const settingsCurrentGroup = requireEl("settings-current-group"); // 当前页设置分组
export const settingsCurrentLabel = requireEl("settings-current-label"); // 当前页设置分组标题
export const settingsCurrentEmpty = requireEl("settings-current-empty"); // 当前页无专属设置提示
// ==== 页签 ====
export const settingsCurrentItems = document.querySelectorAll("[data-settings-tab]"); // 当前页设置项列表
export const tabButtons = document.querySelectorAll(".tab-btn"); // 页签按钮列表
export const tabContents = document.querySelectorAll(".tab-content"); // 页签内容列表

/**
 * 设置保存状态提示模块
 *
 * 独立成叶子模块（仅依赖 `dom_refs` 与 `i18n`），避免 `errors.ts` 为了弹一条提示
 * 而反向 import `main.ts`，从而打断 `main ↔ errors` 的 ESM 循环。
 */

import { settingsStatus } from "./dom_refs.js";
import { t } from "./i18n.js";

/** 成功提示的显示时长（毫秒）。 */
const SUCCESS_HIDE_MS = 2000;

/** 失败提示的显示时长（毫秒），比成功更长以便阅读。 */
const FAILURE_HIDE_MS = 5000;

/** 状态提示自动隐藏定时器，避免重复触发时相互覆盖。 */
let settingsStatusTimer: ReturnType<typeof setTimeout> | null = null;

/**
 * 显示设置保存状态消息
 * @param {string} messageKey - 状态消息的翻译键
 * @returns {void}
 */
export function showSettingsSaveStatus(messageKey: string): void {
    if (settingsStatusTimer) {
        clearTimeout(settingsStatusTimer);
    }

    settingsStatus.dataset.messageKey = messageKey;
    settingsStatus.textContent = t(messageKey);
    settingsStatus.classList.remove("hidden", "settings-status-success", "settings-status-error");
    settingsStatus.classList.add(
        messageKey === "settings.saveSuccess" ? "settings-status-success" : "settings-status-error"
    );

    settingsStatusTimer = setTimeout(() => {
        settingsStatus.classList.add("hidden");
        settingsStatus.dataset.messageKey = "";
    }, messageKey === "settings.saveSuccess" ? SUCCESS_HIDE_MS : FAILURE_HIDE_MS);
}

/**
 * 更新设置保存状态消息文本（供语言切换后重绘）
 * @returns {void}
 */
export function updateSettingsStatusText(): void {
    const messageKey = settingsStatus.dataset.messageKey;
    if (!messageKey) return;
    settingsStatus.textContent = t(messageKey);
}

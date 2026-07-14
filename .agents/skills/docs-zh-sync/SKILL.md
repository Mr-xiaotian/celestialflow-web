---
name: "docs-zh-sync"
description: "Audits celestialflow-web code in src/celestialflow_web and tests, then updates mirrored docs/zh-CN markdown. Invoke when code changes require Chinese docs sync."
---

# Docs Zh Sync（celestialflow-web 项目配置）

本文件是 `celestialflow-web` 项目的 `docs-zh-sync` 技能专属配置，引用通用框架 `~/.agents/skills/docs-zh-sync/`。

当用户提出以下需求时，立即调用本技能：

- 同步、补全、刷新中文文档
- 依据代码更新 `docs/zh-CN`
- 检查 `src/celestialflow_web/`、`tests/` 后批量修正文档
- 发现文档过期、缺页、路径不一致，要求按代码现状修复

## 通用框架

本技能基于通用框架 `~/.agents/skills/docs-zh-sync/SKILL.md`，该框架定义了：

- 4 阶段执行流程（时间确认 → 扫描与区域划分 → 委派子代理 → 汇总与交付）
- 通用审计清单（`_subagent-audit.md`）
- 通用写作规范（`_subagent-writing.md`）
- 通用输出格式与降级策略

主 agent 执行时，应优先遵循通用框架的流程，并结合本文件的项目特化配置。

---

## 项目特化：子任务划分

### 扫描与区域划分

按以下 **5 个固定子任务** 拆分。主 agent 不需要再做额外判断。

| # | 子任务 | 子代理 Prompt 文件 | 负责扫描的代码目录/文件 |
|---|--------|-------------------|------------------------|
| 1 | src/runtime | `subagent-runtime.md` | `src/celestialflow_web/runtime/*.py` |
| 2 | src/server + routes + package | `subagent-server-routes.md` | `src/celestialflow_web/__init__.py`<br>`src/celestialflow_web/server/*.py`<br>`src/celestialflow_web/routes/*.py` |
| 3 | src/static/css | `subagent-static-css.md` | `src/celestialflow_web/static/css/*.css` |
| 4 | src/static/ts + templates | `subagent-static-ts-template.md` | `src/celestialflow_web/static/ts/*.ts`<br>`src/celestialflow_web/templates/*.html` |
| 5 | tests | `subagent-tests.md` | `tests/*.py` |

执行步骤：

1. 用 `find_path` 或 `terminal` 扫描每个子任务对应的代码目录，生成该子任务的代码文件清单。
2. 按项目路径映射规则（见 `_subagent-base.md`）推算每个代码文件对应的 `docs/zh-CN/` 目标文档路径。
3. 同时扫描对应 `docs/zh-CN/` 目录，找出“有文档但无对应源码”的孤立文件，单独列出。

### 委派子代理

按上述 5 个子任务并行委派子代理。每个子代理消息中必须包含：

- 子任务编号和名称
- 当前日期 `YYYY/MM/DD`
- 该子任务的**代码→文档对照清单**（含孤立文档列表）
- 需要阅读的 Skill 文件路径：

| 顺序 | 文件 | 说明 |
|:----:|------|------|
| 1 | `~/.agents/skills/docs-zh-sync/_subagent-base.md` | 通用规则、输出格式 |
| 2 | `~/.agents/skills/docs-zh-sync/_subagent-audit.md` | 通用审计清单 |
| 3 | `~/.agents/skills/docs-zh-sync/_subagent-writing.md` | 通用写作规范 |
| 4 | 项目内 `.agents/skills/docs-zh-sync/_subagent-base.md` | 项目专属路径映射 |
| 5 | 项目内 `.agents/skills/docs-zh-sync/subagent-*.md` | 区域特化提示 |

> 退化策略：如果当前环境限制子代理读取外部 Skill 目录，可临时将通用文件和项目文件合并写入项目内临时文件（如 `temp/docs-zh-sync/instructions-{子任务}.md`），让子代理读取该临时文件，执行完毕后删除。

**推荐并行度**：
- 正常环境下可一次性并行 4-5 个子代理。
- 若环境受限，可串行执行，但最终汇总中需明确已完成和剩余范围。

### 汇总与交付

所有子代理完成后，汇总输出：

- 本次扫描的区域
- 更新、新建、删除或移动的文档路径（按区域分组）
- 发现的代码-文档不一致问题汇总（按严重度）
- 仍待人工确认的歧义点

如果只完成了部分区域，要明确列出已完成范围和剩余范围。

汇总完成后，提醒用户顺手检查以下高风险项：

- [ ] 是否仍存在旧路径遗留（如 `docs/zh-CN/src/core_server.md`、`docs/zh-CN/src/util_*.md`）
- [ ] 是否仍出现过期模块名（如 `pull_routes.py` / `push_routes.py` 与 `core_pull.py` / `core_push.py` 混用）
- [ ] 是否有静态资源文档仍引用编译产物 `static/js/`，而不是源码 `static/ts/`
- [ ] 是否有顶层说明文档仍引用旧包路径 `celestialflow.web.*`

### 降级策略

如果当前环境不支持 `subagent`，则按上述 5 个子任务顺序串行执行，每个子任务作为一个独立分区，输出格式仍遵循 `_subagent-base.md` 的要求。

## 排除项

除非用户明确要求，否则通常不处理：

- `docs/en/`
- `docs/ja/`
- 生成产物，如 `src/celestialflow_web/static/js/*.js`
- `__pycache__/`
- 第三方依赖锁文件、图片、二进制资源
- `docs/zh-CN/` 顶层文件和其他无直接代码对应的目录
- `src/celestialflow_web/package.json`
- `src/celestialflow_web/package-lock.json`
- `src/celestialflow_web/tsconfig.json`
- `src/celestialflow_web/config.json`

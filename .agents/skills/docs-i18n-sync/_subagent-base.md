# Subagent Base: I18n Translation Worker（celestialflow-web 项目特化）

> 本文件仅定义 celestialflow-web 项目的特化约定。**通用翻译规则（路径映射、操作规则、内容分类、Mermaid 细则、输出格式等）请参阅 `~/.agents/skills/docs-i18n-sync/_subagent-base.md`**。
>
> 开始工作前，请按顺序阅读：
> 1. `~/.agents/skills/docs-i18n-sync/_subagent-base.md`（通用翻译规则）
> 2. 本文件（项目特化约定）

---

## 项目路径映射

源语言为 `docs/zh-CN/`，目标语言为 `docs/{en,ja}/`，三者结构完全镜像。

### 镜像目录

| 源路径 (zh-CN) | 目标路径 (en/ja) |
|----------------|-----------------|
| `docs/zh-CN/src/...` | `docs/{en,ja}/src/...` |
| `docs/zh-CN/tests/...` | `docs/{en,ja}/tests/...` |
| `docs/zh-CN/*.md`（顶层） | `docs/{en,ja}/*.md`（顶层） |

### 顶层特殊文件

本项目根存在 `README.md`（中文为主），**必须**翻译到 `docs/en/README.md` 与 `docs/ja/README.md`：
按 `scan_i18n_diff.py --root-file README.md` 的方式映射（源在项目根，不在 `docs/zh-CN/`）。
`docs/zh-CN/` 下**不放** `README.md` 镜像，故 `docs/{en,ja}/README.md` 不应被误判为 DELETE。

### H1 标题镜像（本项目强制）

`docs-zh-sync` 会把 `docs/zh-CN/` 的 H1 全量改为源码相对路径（如 `# src/celestialflow_web/runtime/util_cal.py`），
且明确排除 en/ja。因此 en/ja 必须**逐字镜像**这类路径型 H1；总览类 README（`docs/{en,ja}/README.md`）的 H1 照常翻译。

### 代码块注释语言（本项目约定：本地化）

本项目 en/ja 语料约定（与同源项目 CelestialFlow 保持一致）：代码块中的**中文注释、docstring、示例输出文本一律本地化**（英/日），
仅保留标识符、结构、路径、URL。请与既有译文保持一致，**不要**在同一次同步中混用"保留中文"与"本地化"两种策略。

### Mermaid 图表

翻译节点标签与 `subgraph` 标题中的中文；保留节点 ID、连线类型、Mermaid 关键字、`style`/`classDef` 定义与颜色值。注释（`%%`）中的中文说明也应本地化。

---

## 日期行格式

**日期值始终取自 `docs/zh-CN/` 中对应文件的日期行，与翻译时的"今天"无关**。这是"zh-CN 是唯一事实来源"原则的直接体现。

子代理必须按主 agent 注入的 `{DATE_LABEL}` 写入日期行，**不要自行决定格式或日期值**：

- English: `> 📅 Last Updated: YYYY/MM/DD`
- 日本語: `> 📅 最終更新日: YYYY/MM/DD`

日期值直接复制 `docs/zh-CN/` 对应文件的日期行。**禁止用"今天"或"当前日期"作为译文日期**。

# Subagent Prompt - Static TS And Template

你负责 `src/static/ts` 与 `templates` 区域的中文文档同步。

## 负责范围

- `src/celestialflow_web/static/ts/*.ts`
- `src/celestialflow_web/templates/*.html`
- 对应的 `docs/zh-CN/src/static/ts/*.md`
- 对应的 `docs/zh-CN/src/templates/*.md`

## 重点检查

- TS 模块的导出函数、页面初始化流程、模块协作关系
- `main.ts`、`web_config.ts`、`injection.ts` 等关键文件的职责划分
- `globals.d.ts` 的声明是否与文档一致
- `templates/index.html` 中脚本、样式与容器区域的组织方式
- 是否仍残留旧包路径、旧 API 路径或旧模块名

## ⚠️ 脚本假阳性与范围约定（务必遵守）

- `scan_manifest.py` 反向映射 `.md` 时会优先命中 `.py`，因此 TS 区域**每一个** `.md` 都会被误报为「孤立文档 → 删除（无对应源码）」。**这是工具假阳性**：它们都有 1:1 的 `.ts` 源码，必须全部保留并正常审计，不得据此删除任何文档。
- `templates/partials/*.html` **不作独立镜像文档**：项目只镜像顶层 `templates/*.html`，脚本递归扫描会把 9 个 partial 列为「需新建」，属预期误报。不要为 partial 新建 `.md`，只在 `index.html ↔ index.md` 的审计中核对 `index.md` 对 partial 的描述与源码是否一致。

## 输出补充要求

- 前端文档优先说明“页面职责、初始化顺序、模块之间如何协作”
- 仅在确有必要时列出关键 DOM id/class，避免堆砌实现细节

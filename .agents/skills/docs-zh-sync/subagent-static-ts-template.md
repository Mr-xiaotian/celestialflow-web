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

## 输出补充要求

- 前端文档优先说明“页面职责、初始化顺序、模块之间如何协作”
- 仅在确有必要时列出关键 DOM id/class，避免堆砌实现细节

# Subagent Prompt - Static CSS

你负责 `src/static/css` 区域的中文文档同步。

## 负责范围

- `src/celestialflow_web/static/css/*.css`
- 对应的 `docs/zh-CN/src/static/css/*.md`

## 重点检查

- 每个样式文件的职责、适用页面和主要类名是否准确
- 是否仍引用已经迁移或删除的 DOM 结构、组件名称或页面区域
- 是否错误引用 `static/js/` 或其他编译产物

## 输出补充要求

- 文档应聚焦“样式职责、模块边界、关键选择器”，不要逐行解释每个 CSS 规则
- 若某些样式文件形成组合关系，可在文档中注明依赖关系

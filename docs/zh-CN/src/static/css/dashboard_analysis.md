# dashboard_analysis.css

> 📅 最后更新日期: 2026/08/19

负责仪表盘左下角"图分析信息"卡片的样式定义。

> 注：图级执行模式（`graphMode`）字段取代了已移除的 `scheduleMode`，由 `dashboard_analysis.ts` 通过 `.analysis-value` 渲染，本 CSS 文件未引入新选择器。

## 布局设计 (`.analysis-info`)

- **结构**: 采用纵向 `flex` 布局展示键值对列表。
- **字体**: 使用小号字体（`0.75rem`），以容纳更多元数据信息。

## 数据行样式 (`.analysis-row`)

- **左右对齐**: 标签名（Label）靠左，具体数值（Value）靠右。
- **状态颜色 (`.analysis-value`)**:
  - `.ok`: 绿色（`--jade-600`），表示符合预期（如：是 DAG）。
  - `.warn`: 红色（`--crimson-600`），表示潜在风险（如：存在环路）。

## 关联模块

- 数据渲染由 `dashboard_analysis.ts` 负责，该脚本会根据后端返回的分析结果（是否为 DAG、图级执行模式 `graphMode` 等）动态分配 `ok` 或 `warn` 类。

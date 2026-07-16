# dashboard_error_types.css

> 📅 最后更新日期: 2026/07/16

负责仪表盘"错误类型分布"面板的样式定义，采用环形图加图例的方式展示各节点下错误类型的占比分布。

## 面板容器 (`.error-types-card`)

作为整个错误类型面板的根容器，内部所有子样式均通过嵌套规则限定在其作用域内。

### 面板头部 (`.error-types-card-header`)

使用 `flex` 布局，`space-between` 对齐，左边为标题 `.card-title`（已在 `dashboard.css` 中统一定义），右边为节点筛选下拉框。

### 节点筛选器 (`.error-type-node-filter`)

- 最小宽度 `9rem`，圆角按钮风格。
- 边框使用 `--carbon-300`，暗黑模式下切换为 `--carbon-600`。
- 暗黑模式下背景色与文字色反转，保持视觉一致性。

### 总数统计 (`.error-type-total`)

- 位于面板头部下方，字号 `0.9rem`，灰色文字。
- 暗黑模式下自动切换为浅色。

## 图表区域

### 图表外壳 (`.error-type-chart-shell`)

- 使用 `flex` 居中布局，最小高度 `13rem`。
- 作为 Chart.js 环形图（doughnut）的容器，提供稳定的绘制空间。

### 图表画布 (`#error-type-chart`)

- 通过 ID 选择器固定宽高为 `min(100%, 13rem)`，使用 `!important` 覆盖 Chart.js 自动计算尺寸。
- 确保在不同面板宽度下图表始终保持正方形且不超出容器。

## 图例 (`.error-type-legend`)

纵向排列的图例列表，使用 `flex-direction: column` 和 `0.5rem` 间距。

### 图例行 (`.error-type-legend-row`)

每行包含颜色圆点、错误类型名称和计数三项：

| 子元素 | 类名 | 说明 |
|--------|------|------|
| 颜色圆点 | `.error-type-legend-color` | `0.8rem × 0.8rem` 圆形，`border-radius: 50%`，由 JS 动态设置背景色 |
| 类型名称 | `.error-type-legend-label` | `flex: 1`，支持长文本自动换行（`word-break: break-word`） |
| 计数值 | `.error-type-legend-count` | 右对齐，等宽数字字体（`tabular-nums`），便于数值对比 |

图例行背景为 `--carbon-50` 浅灰，暗黑模式下切换为 `--carbon-800` 深色。

## 暗黑模式适配

所有涉及文字颜色、背景色和边框色的选择器均通过 `.dark-theme &` 嵌套规则提供暗黑模式样式，统一使用 Carbon 色系：

| 元素 | 亮色模式 | 暗黑模式 |
|------|---------|---------|
| 筛选框背景 | `--white` | `--carbon-800` |
| 筛选框边框 | `--carbon-300` | `--carbon-600` |
| 筛选框/图例文字 | `--carbon-800` | `--carbon-100` |
| 辅助文字（总数、计数） | `--carbon-600` | `--carbon-300` |
| 图例行背景 | `--carbon-50` | `--carbon-800` |

## 关联模块

- 图表数据和交互逻辑由 `dashboard_analysis.ts` 驱动，负责根据节点筛选器切换重新渲染 Chart.js 环形图并更新图例。
- 面板整体布局（卡片圆角、阴影、标题样式）由 `dashboard.css` 统一定义。

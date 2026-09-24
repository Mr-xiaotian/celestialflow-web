# src/celestialflow_web/templates/index.html

> 📅 最后更新日期: 2026/09/24

Web UI 的 Jinja2 模板文件，定义了监控系统的完整页面结构。

## 整体布局

页面分为三个主要区域：

```
<header>  — 顶部控制栏（设置面板、主题切换）
<main>
  ├─ .tabs           — 标签页导航（仪表盘 / 错误日志 / 任务注入）
  ├─ #dashboard      — 仪表盘（三栏布局）
  ├─ #errors         — 错误日志
  └─ #task-injection  — 任务注入
```

模板使用 Jinja2 的 `{% include %}` 将各职责区域拆为子模板：

| Partial | 职责 |
|---------|------|
| `partials/head.html` | `<head>` 区块：favicon、CSS、CDN 库（Chart.js、SortableJS、Mermaid） |
| `partials/header.html` | 顶部控制栏与设置按钮、`#settings-panel` 的容器 |
| `partials/settings_panel.html` | 设置面板中的语言、刷新率、自动刷新、错误分页/排序/跳转/字段编辑、仪表盘历史/边增量/等待模式/布局编辑、注入页"仅可注入"等控件 |
| `partials/tab_dashboard.html` | 仪表盘 tab 容器，含 `.left-panel` / `.middle-panel` / `.right-panel` 三个空栏位和隐藏的 `#card-pool` |
| `partials/tab_errors.html` | 错误日志 tab：搜索框、节点筛选、错误表格、分页容器 |
| `partials/tab_injection.html` | 任务注入 tab：节点浏览、当前节点编辑、待发送数据预览、提交与状态消息 |
| `partials/modal_layout_editor.html` | 仪表盘卡片布局编辑弹窗（`#layout-editor-overlay`） |
| `partials/modal_error_columns_editor.html` | 错误表格字段编辑弹窗（`#errors-columns-editor-overlay`） |
| `partials/scripts.html` | 以原生 ESM 方式引入唯一入口 `js/main.js`（见下） |

## Header 控制栏

| 元素 | ID / Class | 说明 |
|------|-----------|------|
| 设置按钮 | `#settings-btn` | 点击打开设置面板，带 a11y 属性 |
| 设置面板 | `#settings-panel` | 包含刷新、历史、语言、分页、增量开关等设置 |
| 界面语言 | `#language-select` | 支持中、英、日三语切换 |
| 结构图增量 | `#structure-edge-delta` | 开关，控制 Mermaid 图边上是否显示成功数增量 |
| 主题切换 | `#theme-toggle` | 圆角胶囊按钮，切换明暗模式 |

## Dashboard 三栏结构

`tab_dashboard.html` 中只提供三个空栏位容器和隐藏的 `#card-pool`。所有卡片 DOM 由 `web_config.ts` 在模块加载时根据 `CARD_TEMPLATES` 注入到 `#card-pool`，再由 `applyDashboardLayout()` 按 `webConfig.dashboard.layout` 移动到三栏。

### 左栏 `.left-panel`

| 卡片 | Class | 说明 |
|------|-------|------|
| 任务结构图 | `.mermaid-card` | Mermaid 流程图，支持节点着色和边增量 |
| 图分析信息 | `.analysis-card` | 拓扑结构洞察信息 |

### 中栏 `.middle-panel`

| 卡片 | Class | 说明 |
|------|-------|------|
| 节点运行状态 | `.status-card` | 动态节点卡片，含进度条和实时增量统计 |

### 右栏 `.right-panel`

| 卡片 | Class | 说明 |
|------|-------|------|
| 节点指标走向 | `.progress-card` | 支持指标切换（完成/成功/错误/重复/等待）的历史折线图 |
| 错误类型分布 | `.error-types-card` | 按节点筛选的错误类型 doughnut 图与图例 |
| 总体状态摘要 | `.summary-card` | 全局 6 格统计看板 |

## 外部依赖（CDN）

| 库 | 版本 | 用途 |
|----|------|------|
| Chart.js | 未固定（CDN latest） | 折线图绘制 |
| SortableJS | `@latest` | 仪表盘布局与错误表格字段的拖拽排序 |
| Mermaid | `^10`（ESM） | 任务图可视化渲染 |

## JS 模块加载

前端使用原生 ESM，`partials/scripts.html` 只引入唯一入口 `js/main.js`，其余模块由其静态 `import` 串联：

```html
<script
    type="module"
    src="{{ request.url_for('static', path='js/main.js') }}"
></script>
```

入口的 import 顺序决定模块求值顺序：

```html
i18n.js               ← 国际化支持
utils.js              ← 通用工具函数
web_config.js         ← 配置管理逻辑 + 卡片 DOM 注入（模块加载时调用 ensureAllCards）
loaders.js            ← 数据层：状态/图元信息拉取与本地派生
util_estimators.js    ← 图级派生指标估算
dashboard_statuses.js ← 节点状态卡渲染
dashboard_structure.js← 结构图渲染
errors.js             ← 错误日志分页 + 字段编辑器
dashboard_analysis.js ← 拓扑分析展示
dashboard_error_types.js ← 错误类型分布卡片
dashboard_summary.js  ← 汇总统计
dashboard_history.js  ← 历史图表
injection.js          ← 任务注入逻辑
layout_editor.js      ← 卡片布局编辑器（依赖 web_config 的 CARD_TEMPLATES、PANEL_SELECTOR_MAP 及 applyDashboardLayout）
main.js               ← 全局入口与轮询协调
```

> 注意：`web_config.js` 在模块加载时会立即调用 `ensureAllCards()`，把全部卡片 DOM 提前注入到 `#card-pool`。因此入口必须最先 import 它，保证后续 `dashboard_*` 模块顶层的 `getElementById` 能找到对应节点；`tests/test_server.py` 通过模块求值顺序测试校验这一约束。所有编译产物都必须能从 `main.js` 出发经 `import` 到达。

## CSS 样式引用

```html
css/_colors.css             ← 颜色变量定义
css/base.css                ← 全局基础样式与设置面板
css/dashboard.css           ← 仪表盘布局与 Tab 容器
css/dashboard_structure.css  ← 结构图专属样式
css/dashboard_analysis.css   ← 分析卡片专属样式
css/dashboard_statuses.css   ← 节点卡片专属样式
css/dashboard_summary.css    ← 汇总面板专属样式
css/dashboard_history.css    ← 历史图专属样式
css/dashboard_error_types.css ← 错误类型分布卡片专属样式
css/errors.css              ← 错误日志页样式
css/injection_layout.css     ← 注入页布局样式
css/injection_nodes.css      ← 注入页节点列表样式
css/injection_editor.css     ← 注入页编辑器样式
css/injection_preview.css    ← 注入页预览样式
```

## 卡片布局编辑器模态窗 (`#layout-editor-overlay`)

悬浮模态窗（默认 `.overlay.hidden` 隐藏），支持拖拽排序三栏仪表盘卡片。

- **遮罩层**: `#layout-editor-overlay` / `.overlay` — 全屏半透明黑色背景
- **编辑器主体**: `#layout-editor` / `.layout-editor` — 圆角卡片容器
- **三栏放置区**: 左中右三个 drop zone（`#layout-dropzone-left`、`#layout-dropzone-middle`、`#layout-dropzone-right`），基于 SortableJS 实现拖拽
- **未使用池**: `#layout-dropzone-unused` — 容纳被移出三栏的卡片
- **底部按钮**: 保存（`#layout-save-btn`）和重置默认（`#layout-reset-btn`）
- 通过设置面板中的 `#open-layout-editor` 按钮打开；点击 `#layout-editor-close` 或遮罩外部关闭
- 保存时调用 `applyDashboardLayout()` 立即生效，再调用 `saveWebConfig()` 持久化到后端

## 错误表格字段编辑器模态窗 (`#errors-columns-editor-overlay`)

由 `partials/modal_error_columns_editor.html` 引入：

- **遮罩层**: `#errors-columns-editor-overlay` / `.overlay` — 复用与布局编辑器相同的遮罩样式
- **主体**: `#errors-columns-editor` / `.layout-editor.error-columns-editor` — 含两个 dropzone：`#errors-columns-dropzone-visible` 与 `#errors-columns-dropzone-hidden`
- **底部按钮**: 保存（`#errors-columns-save-btn`）和重置默认（`#errors-columns-reset-btn`）
- 通过设置面板中的 `#open-error-columns-editor` 按钮打开；点击 `#errors-columns-editor-close` 或遮罩外部关闭
- 由 `errors.ts` 的 `openErrorColumnsEditor()` / `saveErrorColumns()` 负责逻辑，详见 `errors.md`

## 使用示例

### 通过浏览器访问

启动 Web 服务器后，在浏览器地址栏访问：

```
http://127.0.0.1:5000
```

启动命令：

```bash
# 命令行启动（默认 0.0.0.0:5000）
celestialflow-web

# 或在 Python 中启动
python -c "from celestialflow_web import TaskWebServer; TaskWebServer(host='127.0.0.1', port=5000).start_server()"
```

浏览器打开后可见三个标签页：
- **仪表盘 (Dashboard)**: 实时显示任务图的结构图、节点运行状态、指标走向和总体摘要
- **错误日志 (Errors)**: 分页查看和搜索错误记录
- **任务注入 (Task Injection)**: 向指定节点注入新任务

### 修改模板示例

`index.html` 使用 Jinja2 模板引擎，可以通过自定义模板变量或直接修改 HTML 来自定义界面。

#### 修改页面标题

编辑 `index.html` 找到 `<title>` 标签：

```html
<!-- 原内容 -->
<title>任务图监控系统</title>

<!-- 修改为自定义标题 -->
<title>我的任务监控</title>
```

#### 调整仪表盘布局

> ⚠️ `tab_dashboard.html` 中**只提供**三个空栏位容器（`.left-panel` / `.middle-panel` / `.right-panel`）和隐藏的 `#card-pool`。**不要直接修改 HTML 中的卡片顺序**，所有卡片由 `web_config.ts` 在模块加载时通过 `CARD_TEMPLATES` 注入 `#card-pool`，再由 `applyDashboardLayout()` 按 `webConfig.dashboard.layout` 移动到三栏。

如需调整三栏布局，优先通过以下两种方式：

1. **运行时**：打开设置面板中的“编辑仪表盘布局”（`#open-layout-editor`），在 `#layout-editor-overlay` 弹窗中拖拽卡片到目标栏位后保存。
2. **默认值**：编辑 `src/celestialflow_web/static/ts/web_config.ts` 中的 `DEFAULT_WEB_CONFIG.dashboard.layout`，例如：

```typescript
dashboard: {
    layout: {
        left: ["analysis", "mermaid"],   // 将分析卡片放在最上方
        middle: ["status"],
        right: ["progress", "summary", "error-types"],
    },
}
```

可用卡片 key：`mermaid`、`analysis`、`status`、`progress`、`error-types`、`summary`。

#### 通过配置动态控制

运行时的全部 UI 偏好由分组 `WebConfig` 控制，包含 `global` / `dashboard` / `errors` / `injection` 四个子节。`web_config.ts` 在启动时通过 `GET /api/pull_config` 读取用户配置；保存时调用 `POST /api/push_config` 整体覆盖。可以通过后端 `config.json` 提供初始值：

```json
{
    "global": {
        "theme": "dark",
        "language": "zh-CN",
        "autoRefreshEnabled": true,
        "refreshInterval": 5000
    },
    "dashboard": {
        "historyLimit": 20,
        "showStructureEdgeDelta": true,
        "useTotalPendingInStatus": true,
        "layout": {
            "left": ["mermaid", "analysis"],
            "middle": ["status"],
            "right": ["progress", "error-types", "summary"]
        }
    },
    "errors": {
        "pageSize": 50,
        "sortOrder": "newest",
        "jumpToInjectionAfterRetry": true,
        "columns": ["index", "event_id", "message", "stage", "task", "time", "retry"]
    },
    "injection": {
        "showInjectableOnly": true
    }
}
```

> 字段详细说明参见 [`web_config.md`](../static/ts/web_config.md)。修改后通过设置面板的“保存设置”按钮或等待 `saveWebConfig()` 自动触发即可生效。

#### 添加自定义 CSS

将自定义样式文件放入 `src/celestialflow_web/static/css/` 目录，并在 `partials/head.html` 中用 Jinja2 的 `request.url_for` 引入，确保路径在挂载到非根路径时仍能正确解析：

```html
<link
    rel="stylesheet"
    href="{{ request.url_for('static', path='css/custom.css') }}"
/>
```

JS 脚本同理使用 `{{ request.url_for('static', path='js/xxx.js') }}`。

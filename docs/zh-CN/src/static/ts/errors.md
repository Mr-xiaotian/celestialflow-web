# src/celestialflow_web/static/ts/errors.ts

> 📅 最后更新日期: 2026/09/24

错误日志分页与过滤模块。负责错误记录的异步拉取、前端分页逻辑、按节点/关键词搜索的过滤展示，以及表格字段顺序的运行时编辑（`#errors-columns-editor-overlay`）。

## 类型定义

`ErrorData`、`ErrorsPullResponse`、`ErrorColumnKey` 等契约类型统一声明于 [`types.d.ts`](types.d.md)。本模块内部还定义了字段元信息类型：

```typescript
type ErrorColumnMeta = {
  labelKey: string;         // 列标题对应的国际化 key
  headerClassName?: string; // 表头额外样式类
  cellClassName?: string;   // 单元格额外样式类
};
```

## 全局变量

| 变量 | 类型 | 说明 |
|------|------|------|
| `errors` | `ErrorData[]` | 当前页错误记录列表 |
| `currentPage` | `number` | 当前分页页码，默认 `1` |
| `pageSize` | `number` | 每页显示条数，默认 `10`，由 `webConfig.errors.pageSize` 同步 |
| `errorSortOrder` | `"newest" \| "oldest"` | 当前错误日志排序方式，默认 `"newest"` |
| `totalPages` | `number` | 总页数，默认 `1` |
| `errorsRev` | `number` | 数据版本号，用于增量拉取，默认 `-1` |
| `lastQueryKey` | `string` | 上次查询缓存键，用于判断筛选条件是否变化 |
| `errorsRequestSeq` | `number` | 请求序列号，防止旧响应覆盖新结果 |
| `originalErrorColumns` | `ErrorColumnKey[]` | 打开字段编辑器时的字段快照 |
| `errorColumnSortableInstances` | `Partial<Record<..., SortableInstance>>` | 字段编辑器拖拽实例缓存 |
| `ERROR_COLUMN_META` | `Record<ErrorColumnKey, ErrorColumnMeta>` | 每个字段的 i18n key 与单元格/表头类名 |
| `ALL_ERROR_COLUMN_IDS` | `ErrorColumnKey[]` | 字段编辑器可选的全部字段 key |
| `ERROR_COLUMNS_ZONE_IDS` | `readonly [...]` | 字段编辑器中"已显示/未显示"两个 dropzone 的 ID 列表 |

## DOM 元素引用

| 变量 | DOM 选择器 | 说明 |
|------|-----------|------|
| `searchInput` | `#error-search` | 关键词搜索输入框 |
| `nodeFilter` | `#node-filter` | 按节点筛选下拉框 |
| `errorSortSelect` | `#error-sort-order` | 排序方式下拉框 |
| `errorsTableHeadRow` | `#errors-table thead tr` | 错误表格表头行 |
| `errorsTableBody` | `#errors-table tbody` | 错误表格主体 |
| `paginationContainer` | `#pager-container` | 分页控件容器 |
| `openErrorColumnsEditorBtn` | `#open-error-columns-editor` | 设置面板中"编辑表格字段"按钮 |
| `errorColumnsEditorOverlay` | `#errors-columns-editor-overlay` | 字段编辑器遮罩层 |
| `errorColumnsEditorCloseBtn` | `#errors-columns-editor-close` | 字段编辑器关闭按钮 |
| `errorColumnsSaveBtn` | `#errors-columns-save-btn` | 字段编辑器保存按钮 |
| `errorColumnsResetBtn` | `#errors-columns-reset-btn` | 字段编辑器重置默认按钮 |

## 函数

### `buildErrorsQueryKey(page, pageSizeValue, node, keyword, sortOrder): string`

构建包含分页、页大小、节点筛选、关键词和排序方式的查询缓存键，用于判断是否需要强制全量拉取。

### `loadErrors(forceReload = false): Promise<boolean>`

从后端 `GET /api/pull_errors` 拉取当前筛选条件下的错误日志。

- **查询参数**：`known_rev`、`page`、`page_size`、`node`、`keyword`、`sort_order`。
- **缓存策略**：当筛选条件（`lastQueryKey`）变化或 `forceReload=true` 时，`known_rev` 重置为 `-1` 强制全量拉取。
- **竞态保护**：使用 `errorsRequestSeq` 丢弃过期响应。
- **返回值**：当后端返回了新的错误记录数据时返回 `true`。

### `renderErrors(): void`

将 `errors` 数组渲染到表格中。每行包含错误序号、事件 ID、错误信息、节点、任务数据、发生时间和重试按钮。

- 当 `task_json !== undefined` 时显示可点击的“任务注入”重试链接，否则显示不可用的“格式未知”占位。
- 重试点击调用 `preloadInjectionDraftFromError(stage, task_json, webConfig.errors.jumpToInjectionAfterRetry)`。
- 无记录时显示空态占位。

### `goToErrorsPage(nextPage): Promise<void>`

跳转到指定页码并重新加载数据。目标页码会被限制在 `[1, totalPages]` 范围内。

### `buildPageList(current, total): Array<number \| string>`

生成分页页码列表，包含首尾、当前页及前后页，间隔超过 1 时插入省略号 `…`。

### `renderPaginationControls(totalPages): void`

渲染分页控件，包括“上一页/下一页”按钮和带省略号的数字页码区。当总页数 `<= 1` 时不渲染。

### `populateNodeFilter(statuses): void`

根据当前节点状态快照填充节点筛选下拉框，并尽量保留用户之前的筛选值。若已选节点已消失则恢复为“全部节点”。

### 字段编辑器（运行时配置错误表格字段顺序与显隐）

- `getActiveErrorColumns()`: 读取 `webConfig.errors.columns` 并交由 `web_config.normalizeErrorColumns()` 归一化。
- `normalizeErrorColumns(rawColumns)`（来自 `web_config.ts`）: 以默认字段列表为白名单去重并过滤非法字段。
- `renderErrorColumnsEditor(visibleColumns)`: 按给定顺序渲染“已显示”和“未显示”两个 dropzone，并初始化 SortableJS。
- `openErrorColumnsEditor()` / `closeErrorColumnsEditor(restore = true)`: 打开/关闭字段编辑器；关闭且 `restore=true` 时回滚到 `originalErrorColumns` 快照。
- `initErrorColumnSortable()` / `destroyErrorColumnSortable()`: 创建/销毁 dropzone 上的 SortableJS 实例（共用 `errors-columns` 分组）。
- `syncErrorColumnsFromEditor()`: 把当前 dropzone 顺序写回 `webConfig.errors.columns`。
- `saveErrorColumns()`: 写回顺序并调用 `saveWebConfig()` 持久化；保存成功后关闭编辑器。
- `resetErrorColumns()`: 将 `webConfig.errors.columns` 重置为 `DEFAULT_WEB_CONFIG.errors.columns` 拷贝。
- `renderErrorsTableHeader()`: 按当前字段顺序重绘 `<thead>` 行；会被 `applyConfig()` 和 `closeErrorColumnsEditor(restore=true)` 共同调用。

## 事件绑定

| 元素 | 事件 | 行为 |
|------|------|------|
| `searchInput` | `input` | 回到第一页，强制重新拉取并渲染 |
| `nodeFilter` | `change` | 回到第一页，强制重新拉取并渲染 |
| `errorSortSelect` | `change` | 更新 `errorSortOrder` 与 `webConfig.errors.sortOrder`，回到第一页，拉取渲染，并调用 `saveWebConfig()` 保存设置 |
| `openErrorColumnsEditorBtn` | `click` | 打开错误字段编辑器 |
| `errorColumnsEditorCloseBtn` | `click` | 关闭字段编辑器并恢复原顺序 |
| `errorColumnsEditorOverlay` | `click` | 点击遮罩外层时关闭编辑器（`restore=true`） |
| `errorColumnsSaveBtn` | `click` | 保存当前字段顺序并持久化 |
| `errorColumnsResetBtn` | `click` | 重置字段顺序为默认值 |

## 数据流

```mermaid
sequenceDiagram
    participant User as 用户
    participant Main as main.ts
    participant Errors as errors.ts
    participant API as /api/pull_errors
    participant Injection as injection.ts

    User->>Main: 切换错误页 / 输入筛选
    Main->>Errors: loadErrors(true)
    Errors->>API: GET 带分页/筛选参数
    API-->>Errors: { rev, page, total_pages, data }
    Errors->>Errors: 更新 errors / totalPages
    Errors->>Errors: renderErrors()
    Errors->>Errors: renderPaginationControls()
    User->>Errors: 点击 retry-link
    Errors->>Injection: preloadInjectionDraftFromError(stage, task_json, jumpToInjection)
```

## 使用示例

```typescript
// 直接跳转到第 3 页
await goToErrorsPage(3);

// 按节点筛选（等效于设置 nodeFilter 并触发 change）
nodeFilter.value = "Processor";
nodeFilter.dispatchEvent(new Event("change"));

// 构建查询缓存键
const key = buildErrorsQueryKey(1, 10, "Processor", "timeout", "newest");
// "1|10|Processor|timeout|newest"

// renderErrors 会读取全局 errors 并渲染表格
// renderPaginationControls(totalPages) 会渲染底部分页
```

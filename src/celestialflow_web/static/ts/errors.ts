/**
 * 错误日志分页与过滤模块
 * 处理错误记录的异步拉取、前端分页逻辑以及按节点/关键词搜索的过滤展示
 */

/** 单条错误数据定义 */
type ErrorData = {
  ts: number; // 生命周期时间戳，单位为秒
  stage: string; // 错误发生的节点/阶段名称，用于节点筛选
  event_id: number; // 失败事件的唯一标识 ID，全局唯一
  error_type: string; // 错误的分类类型，用于区分不同类别的错误
  error_message: string; // 错误的具体描述信息，是错误的详细文本内容
  task_json: unknown; // 触发该错误的任务数据，同时用于展示与重试回填
  result_json: unknown; // 成功结果或失败时的占位结果
};

type ErrorColumnMeta = {
  labelKey: string; // 列标题对应的国际化 key
  headerClassName?: string; // 表头额外样式类
  cellClassName?: string; // 单元格额外样式类
};

const ERROR_COLUMN_META: Record<ErrorColumnKey, ErrorColumnMeta> = {
  index: { labelKey: "errors.colIndex" },
  event_id: { labelKey: "errors.colId", cellClassName: "error-id" },
  message: {
    labelKey: "errors.colMessage",
    cellClassName: "error-cell",
  },
  stage: { labelKey: "errors.colNode" },
  task: { labelKey: "errors.colTask" },
  time: { labelKey: "errors.colTime" },
  retry: { labelKey: "errors.colRetry" },
}; // 错误日志字段元信息

const ALL_ERROR_COLUMN_IDS: ErrorColumnKey[] = Object.keys(
  ERROR_COLUMN_META,
) as ErrorColumnKey[]; // 当前支持进入字段编辑器的全部列 key

const ERROR_COLUMNS_ZONE_IDS = [
  "errors-columns-dropzone-visible",
  "errors-columns-dropzone-hidden",
] as const; // 字段编辑器中支持互拖的全部区域 ID

// 全局状态
let errors: ErrorData[] = []; // 错误记录列表
let currentPage = 1; // 当前分页页码
let pageSize = 10; // 每页显示条数
let errorSortOrder: "newest" | "oldest" = "newest"; // 错误日志默认排序
let totalPages = 1; // 总页数
let errorsRev = -1; // 数据版本号，用于增量拉取
let lastQueryKey = ""; // 上次查询的缓存键，用于判断筛选条件是否变化
let errorsRequestSeq = 0; // 请求序列号，防止旧请求覆盖新结果
let originalErrorColumns: ErrorColumnKey[] = []; // 打开字段编辑器时的字段快照
let errorColumnSortableInstances: Partial<
  Record<(typeof ERROR_COLUMNS_ZONE_IDS)[number], SortableInstance>
> = {}; // 字段编辑器拖拽实例缓存

// DOM 元素引用（错误页）
const searchInput = document.getElementById("error-search") as HTMLInputElement;
const nodeFilter = document.getElementById("node-filter") as HTMLSelectElement;
const errorSortSelect = document.getElementById("error-sort-order") as HTMLSelectElement;
const errorsTableHeadRow = document.querySelector(
  "#errors-table thead tr",
) as HTMLTableRowElement;
const errorsTableBody = document.querySelector("#errors-table tbody") as HTMLTableSectionElement;
const paginationContainer = document.getElementById("pager-container") as HTMLElement;
const openErrorColumnsEditorBtn = document.getElementById(
  "open-error-columns-editor",
) as HTMLButtonElement;
const errorColumnsEditorOverlay = document.getElementById(
  "errors-columns-editor-overlay",
) as HTMLElement;
const errorColumnsEditorCloseBtn = document.getElementById(
  "errors-columns-editor-close",
) as HTMLButtonElement;
const errorColumnsSaveBtn = document.getElementById(
  "errors-columns-save-btn",
) as HTMLButtonElement;
const errorColumnsResetBtn = document.getElementById(
  "errors-columns-reset-btn",
) as HTMLButtonElement;

/**
 * 读取当前配置中的错误字段顺序；缺省时返回默认值。
 * @returns {ErrorColumnKey[]} 当前生效的错误字段顺序。
 */
function getActiveErrorColumns(): ErrorColumnKey[] {
  return normalizeErrorColumns(webConfig.errors.columns);
}

/**
 * 将任意任务对象稳定格式化为错误表格文本。
 * @param {unknown} taskData - 当前错误记录中的任务数据。
 * @returns {string} 可直接展示与 tooltip 使用的字符串。
 */
function getErrorTaskText(taskData: unknown): string {
  if (typeof taskData === "string") {
    return taskData;
  }
  if (taskData === undefined) {
    return "undefined";
  }
  if (taskData === null) {
    return "null";
  }
  const serialized = JSON.stringify(taskData);
  return serialized ?? String(taskData);
}

/**
 * 创建字段编辑器中的一张可拖拽字段卡片。
 * @param {ErrorColumnKey} columnId - 字段 key。
 * @returns {HTMLElement} 字段卡片节点。
 */
function renderErrorColumnCard(columnId: ErrorColumnKey): HTMLElement {
  const el = document.createElement("div");
  el.className = "layout-card";
  el.dataset.columnId = columnId;
  el.innerHTML = `
    <span class="layout-card-name">${t(ERROR_COLUMN_META[columnId].labelKey)}</span>
    <span class="layout-card-handle" aria-hidden="true">::</span>`;
  return el;
}

/**
 * 读取字段编辑器中某个区域的字段顺序。
 * @param {"visible" | "hidden"} zone - 目标区域。
 * @returns {ErrorColumnKey[]} 区域中的字段顺序。
 */
function getEditorColumns(zone: "visible" | "hidden"): ErrorColumnKey[] {
  const dropzone = document.getElementById(
    `errors-columns-dropzone-${zone}`,
  ) as HTMLElement;
  return Array.from(dropzone.querySelectorAll<HTMLElement>(".layout-card")).map(
    (card) => card.dataset.columnId as ErrorColumnKey,
  );
}

/**
 * 渲染字段编辑器中的显示区与隐藏区。
 * @param {ErrorColumnKey[]} visibleColumns - 当前显示字段顺序。
 * @returns {void}
 */
function renderErrorColumnsEditor(
  visibleColumns: ErrorColumnKey[],
): void {
  const visibleZone = document.getElementById(
    "errors-columns-dropzone-visible",
  ) as HTMLElement;
  const hiddenZone = document.getElementById(
    "errors-columns-dropzone-hidden",
  ) as HTMLElement;
  const visibleSet = new Set(visibleColumns);

  visibleZone.innerHTML = "";
  hiddenZone.innerHTML = "";

  for (const columnId of visibleColumns) {
    visibleZone.appendChild(renderErrorColumnCard(columnId));
  }
  for (const columnId of ALL_ERROR_COLUMN_IDS) {
    if (!visibleSet.has(columnId)) {
      hiddenZone.appendChild(renderErrorColumnCard(columnId));
    }
  }

  initErrorColumnSortable();
}

/**
 * 打开错误字段编辑器，读取当前配置并渲染。
 * @returns {void}
 */
function openErrorColumnsEditor(): void {
  errorColumnsEditorOverlay.classList.remove("hidden");
  originalErrorColumns = [...getActiveErrorColumns()];
  renderErrorColumnsEditor(originalErrorColumns);
}

/**
 * 关闭错误字段编辑器。
 * @param {boolean} [restore=true] - 是否恢复打开前的字段顺序。
 * @returns {void}
 */
function closeErrorColumnsEditor(restore: boolean = true): void {
  errorColumnsEditorOverlay.classList.add("hidden");
  destroyErrorColumnSortable();
  if (!restore) return;
  webConfig.errors.columns = [...originalErrorColumns];
  renderErrorsTableHeader();
  renderErrors();
}

/**
 * 初始化字段编辑器中的拖拽区域。
 * @returns {void}
 */
function initErrorColumnSortable(): void {
  destroyErrorColumnSortable();

  for (const id of ERROR_COLUMNS_ZONE_IDS) {
    const zone = document.getElementById(id);
    if (!zone) continue;
    errorColumnSortableInstances[id] = Sortable.create(zone, {
      group: "errors-columns",
      animation: 150,
      ghostClass: "dragging",
      dragClass: "dragging",
    });
  }
}

/**
 * 销毁字段编辑器中的拖拽实例。
 * @returns {void}
 */
function destroyErrorColumnSortable(): void {
  for (const id of ERROR_COLUMNS_ZONE_IDS) {
    errorColumnSortableInstances[id]?.destroy();
  }
  errorColumnSortableInstances = {};
}

/**
 * 将字段编辑器中的当前顺序写回配置。
 * @returns {void}
 */
function syncErrorColumnsFromEditor(): void {
  webConfig.errors.columns = getEditorColumns("visible");
}

/**
 * 保存当前字段顺序到配置并刷新表格。
 * @returns {Promise<void>}
 */
async function saveErrorColumns(): Promise<void> {
  syncErrorColumnsFromEditor();
  renderErrorsTableHeader();
  renderErrors();
  const saved = await saveWebConfig();
  if (saved) {
    closeErrorColumnsEditor(false);
    showSettingsSaveStatus("settings.saveSuccess");
  } else {
    showSettingsSaveStatus("settings.saveFailed");
  }
}

/**
 * 将字段编辑器恢复到默认字段顺序。
 * @returns {void}
 */
function resetErrorColumns(): void {
  webConfig.errors.columns = [...DEFAULT_WEB_CONFIG.errors.columns];
  renderErrorColumnsEditor(webConfig.errors.columns);
}

/**
 * 根据当前配置重绘错误日志表头。
 * @returns {void}
 */
function renderErrorsTableHeader(): void {
  const visibleColumns = getActiveErrorColumns();
  errorsTableHeadRow.innerHTML = "";
  for (const columnId of visibleColumns) {
    const th = document.createElement("th");
    th.textContent = t(ERROR_COLUMN_META[columnId].labelKey);
    if (ERROR_COLUMN_META[columnId].headerClassName) {
      th.className = ERROR_COLUMN_META[columnId].headerClassName!;
    }
    errorsTableHeadRow.appendChild(th);
  }
}

/**
 * 创建普通文本单元格。
 * @param {ErrorColumnKey} columnId - 字段 key。
 * @param {string} text - 单元格文本。
 * @param {string} [title] - 可选 tooltip。
 * @returns {HTMLTableCellElement} 单元格节点。
 */
function createErrorTextCell(
  columnId: ErrorColumnKey,
  text: string,
  title?: string,
): HTMLTableCellElement {
  const td = document.createElement("td");
  td.dataset.label = t(ERROR_COLUMN_META[columnId].labelKey);
  td.textContent = text;
  if (title) {
    td.title = title;
  }
  const className = ERROR_COLUMN_META[columnId].cellClassName;
  if (className) {
    td.classList.add(className);
  }
  return td;
}

/**
 * 创建重试操作单元格。
 * @param {ErrorData} errorData - 当前错误记录。
 * @returns {HTMLTableCellElement} 重试单元格节点。
 */
function createRetryCell(errorData: ErrorData): HTMLTableCellElement {
  const canRetry = errorData.task_json !== undefined;
  const retryLabel = canRetry
    ? t("errors.retryInject")
    : t("errors.retryUnavailable");
  const retryClass = canRetry ? "retry-link" : "retry-disabled";
  const td = createErrorTextCell("retry", "");
  const action = document.createElement("div");
  action.className = retryClass;
  action.setAttribute("role", canRetry ? "button" : "note");
  action.tabIndex = canRetry ? 0 : -1;
  action.textContent = retryLabel;
  if (canRetry) {
    const retryFromCurrentError = (): void => {
      preloadInjectionDraftFromError(
        errorData.stage,
        errorData.task_json,
        webConfig.errors.jumpToInjectionAfterRetry,
      );
    };
    action.addEventListener("click", retryFromCurrentError);
    action.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      retryFromCurrentError();
    });
  }
  td.appendChild(action);
  return td;
}

/**
 * 根据字段 key 生成一格错误日志单元格。
 * @param {ErrorColumnKey} columnId - 字段 key。
 * @param {ErrorData} errorData - 当前错误记录。
 * @param {number} index - 当前分页下的全局序号。
 * @returns {HTMLTableCellElement} 单元格节点。
 */
function createErrorCell(
  columnId: ErrorColumnKey,
  errorData: ErrorData,
  index: number,
): HTMLTableCellElement {
  const errorText = `${errorData.error_type}(${errorData.error_message})`;
  const errorRepr = format_repr(errorText, 30);
  const taskText = getErrorTaskText(errorData.task_json);
  const taskRepr = format_repr(taskText, 30);

  switch (columnId) {
    case "index":
      return createErrorTextCell("index", String(index));
    case "event_id":
      return createErrorTextCell("event_id", String(errorData.event_id));
    case "message":
      return createErrorTextCell("message", errorRepr, errorText);
    case "stage":
      return createErrorTextCell("stage", errorData.stage);
    case "task":
      return createErrorTextCell("task", taskRepr, taskText);
    case "time":
      return createErrorTextCell("time", formatTimestamp(errorData.ts));
    case "retry":
      return createRetryCell(errorData);
  }
}

/**
 * 构建错误查询缓存键
 * @param {number} page - 当前页码
 * @param {number} pageSizeValue - 每页大小
 * @param {string} node - 节点筛选条件
 * @param {string} keyword - 搜索关键词
 * @param {string} sortOrder - 排序顺序（"newest" 或 "oldest"）
 * @returns {string} 组合后的查询键
 */
function buildErrorsQueryKey(
  page: number,
  pageSizeValue: number,
  node: string,
  keyword: string,
  sortOrder: string,
): string {
  return `${page}|${pageSizeValue}|${node}|${keyword}|${sortOrder}`;
}

/**
 * 从后端加载错误日志数据
 * @param {boolean} [forceReload=false] - 是否忽略当前查询缓存与 `known_rev`，强制重新拉取。
 * @returns {Promise<boolean>} 当后端返回了新的错误记录数据时返回 `true`，否则返回 `false`。
 */
async function loadErrors(forceReload = false): Promise<boolean> {
  try {
    const node = nodeFilter.value.trim(); // 当前节点筛选值
    const keyword = (searchInput.value || "").trim(); // 当前关键词筛选值
    const queryKey = buildErrorsQueryKey(
      currentPage,
      pageSize,
      node,
      keyword.toLowerCase(),
      errorSortOrder,
    );
    const knownRev = forceReload || queryKey !== lastQueryKey ? -1 : errorsRev; // 条件变化时强制全量拉取
    const requestSeq = ++errorsRequestSeq; // 为当前请求分配递增序号

    // 将分页、排序和筛选条件编码进查询参数。
    const params = new URLSearchParams({
      known_rev: String(knownRev),
      page: String(currentPage),
      page_size: String(pageSize),
      node,
      keyword,
      sort_order: errorSortOrder,
    });
    const res = await fetch(`/api/pull_errors?${params.toString()}`);
    if (!res.ok) return false;
    const data = (await res.json()) as ErrorsPullResponse;

    if (requestSeq !== errorsRequestSeq) return false; // 丢弃已过时请求的返回结果

    currentPage = Number(data.page || currentPage);
    totalPages = Number(data.total_pages || 1);
    errorSortOrder = data.sort_order === "oldest" ? "oldest" : "newest";
    lastQueryKey = queryKey;

    if (data.data === null) {
      return false;
    }

    errors = data.data;
    const changed = errorsRev !== Number(data.rev); // 对比版本号判断是否有新内容
    errorsRev = Number(data.rev);
    return changed || forceReload;
  } catch (e) {
    console.error("错误日志加载失败", e);
    return false;
  }
}

/**
 * 渲染错误列表表格和分页控件
 * 将获取到的错误记录填充到表格中，并根据总页数生成分页按钮
 */
function renderErrors(): void {
  const pageItems = errors; // 后端已按分页返回当前页数据
  const visibleColumns = getActiveErrorColumns();

  errorsTableBody.innerHTML = "";

  if (!visibleColumns.length) {
    errorsTableBody.innerHTML = `<tr><td colspan="1" class="empty-placeholder">${t("errors.noVisibleColumns")}</td></tr>`;
    renderPaginationControls(totalPages);
    return;
  }

  if (!pageItems.length) {
    errorsTableBody.innerHTML = `<tr><td colspan="${visibleColumns.length}" class="empty-placeholder">${t("errors.noRecords")}</td></tr>`;
  } else {
    for (let i = 0; i < pageItems.length; i++) {
      const errorData = pageItems[i]; // 当前错误记录
      const index = (currentPage - 1) * pageSize + i + 1; // 全局展示序号
      const row = document.createElement("tr"); // 当前表格行
      for (const columnId of visibleColumns) {
        row.appendChild(createErrorCell(columnId, errorData, index));
      }
      errorsTableBody.appendChild(row);
    }
  }

  renderPaginationControls(totalPages);
}

/**
 * 跳转到指定错误页码并重新加载数据
 * @param {number} nextPage - 目标页码
 * @returns {Promise<void>}
 */
async function goToErrorsPage(nextPage: number): Promise<void> {
  const normalizedPage = Math.max(1, Math.min(totalPages || 1, nextPage)); // 将目标页码限制在合法范围内
  if (normalizedPage === currentPage) return;
  currentPage = normalizedPage;
  await loadErrors(true);
  renderErrors();
}

/**
 * 生成分页页码列表，包含首尾、当前及前后页，自动插入省略号
 * @param {number} current - 当前页码
 * @param {number} total - 总页数
 * @returns {Array<number|string>} 页码数组（数字或省略号）
 */
function buildPageList(current: number, total: number): Array<number | string> {
  // 想显示哪些关键页：首尾、当前、前后1-2页
  const pages = new Set([1, total, current, current-1, current+1, current-2, current+2]);
  const list = [...pages].filter(p => p >= 1 && p <= total).sort((a,b)=>a-b); // 去掉越界页码后升序排列

  const out: Array<number | string> = [];
  for (let i = 0; i < list.length; i++) {
    out.push(list[i]);
    if (i < list.length - 1 && list[i+1] - list[i] > 1) out.push("…"); // 插入省略号
  }
  return out;
}

/**
 * 渲染分页控件（上一页、页码、下一页）
 * @param {number} totalPages - 总页数
 * @returns {void}
 */
function renderPaginationControls(totalPages: number): void {
  paginationContainer.innerHTML = "";
  if (totalPages <= 1) return;

  // 上一页
  const prevBtn = document.createElement("button");
  prevBtn.textContent = t("errors.prevPage");
  prevBtn.className = "pager-btn";
  prevBtn.disabled = currentPage === 1;
  prevBtn.onclick = async () => { await goToErrorsPage(currentPage - 1); };

  // 数字页码区
  const pageBar = document.createElement("div"); // 中间页码容器
  pageBar.className = "pager";

  const pages = buildPageList(currentPage, totalPages); // 带省略号的页码模型
  pages.forEach(p => {
    const span = document.createElement("span"); // 单个页码或省略号元素
    span.textContent = p.toString();
       if (p === "…") {
      span.className = "dots";
    } else if (p === currentPage) {
      span.className = "pager-current";
    } else {
      span.className = "pager-link";
      span.onclick = async () => {
        await goToErrorsPage(Number(p));
      };
    }
    pageBar.appendChild(span);
  });

  // 下一页
  const nextBtn = document.createElement("button");
  nextBtn.textContent = t("errors.nextPage");
  nextBtn.className = "pager-btn";
  nextBtn.disabled = currentPage === totalPages;
  nextBtn.onclick = async () => { await goToErrorsPage(currentPage + 1); };

  paginationContainer.appendChild(prevBtn);
  paginationContainer.appendChild(pageBar);
  paginationContainer.appendChild(nextBtn);
}

/**
 * 根据节点状态填充错误筛选下拉框
 * @param {Record<string, NodeStatus>} statuses - 节点状态映射
 * @returns {void}
 */
function populateNodeFilter(statuses: Record<string, NodeStatus>): void {
  const nodes = Object.keys(statuses); // 当前可供筛选的节点名列表
  const previousValue = nodeFilter.value; // 尽量保留用户当前筛选条件

  nodeFilter.innerHTML = `<option value="">${t("errors.allNodes")}</option>`;
  for (const node of nodes) {
    const option = document.createElement("option"); // 单个节点下拉项
    option.value = node;
    option.textContent = node;
    nodeFilter.appendChild(option);
  }

  if (nodes.includes(previousValue)) {
    nodeFilter.value = previousValue;
  } else {
    nodeFilter.value = "";
  }
}

openErrorColumnsEditorBtn.addEventListener("click", openErrorColumnsEditor);
errorColumnsEditorCloseBtn.addEventListener("click", () => {
  closeErrorColumnsEditor();
});
errorColumnsEditorOverlay.addEventListener("click", (event) => {
  if ((event.target as HTMLElement).id === "errors-columns-editor-overlay") {
    closeErrorColumnsEditor();
  }
});
errorColumnsSaveBtn.addEventListener("click", saveErrorColumns);
errorColumnsResetBtn.addEventListener("click", resetErrorColumns);

// 输入搜索关键词时立即重新筛选错误列表并回到第一页。
searchInput.addEventListener("input", async () => {
  currentPage = 1;
  await loadErrors(true);
  renderErrors();
});

// 切换节点筛选时刷新当前错误列表。
nodeFilter.addEventListener("change", async () => {
  currentPage = 1; // 切换节点时回到第一页
  await loadErrors(true);
  renderErrors();
});

// 切换默认排序方式时刷新错误页并保存当前设置。
errorSortSelect.addEventListener("change", async () => {
  errorSortOrder = errorSortSelect.value === "oldest" ? "oldest" : "newest";
  if (webConfig) {
    webConfig.errors.sortOrder = errorSortOrder;
  }
  currentPage = 1;
  await loadErrors(true);
  renderErrors();
  if (webConfig) {
    showSettingsSaveStatus(
      (await saveWebConfig()) ? "settings.saveSuccess" : "settings.saveFailed",
    );
  }
});

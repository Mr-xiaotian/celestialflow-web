/**
 * 前后端契约类型声明
 *
 * 只收纳"从本前端之外送来"的数据形状：HTTP 接口的 payload / 响应，以及配置文件结构。
 * 前端本地派生（如 `NodeEstimate`）或只服务于单个渲染器的词汇（如 `NodeShape`）
 * 留在各自文件里，不往这里搬。
 *
 * 本文件是纯类型声明（.d.ts），不产生 .js 产物，因此无需在 scripts.html 中引用。
 */

// ==== 通用 ====

export type Lang = "zh-CN" | "en" | "ja"; // 支持的界面语言

type ApiVersionedResponse<T> = {
  rev: number; // 当前数据版本号
  data: T | null; // 当 known_rev 未变化时可能返回 null
};

// ==== 节点状态：/api/pull_status ====

/** 节点运行时状态快照定义（与后端 payload 的字段形状一致） */
export type NodeStatus = {
  status: number; // 状态码：0-未运行, 1-运行中, 2-已停止
  tasks_processed: number; // 已处理任务总数
  tasks_pending: number; // 队列中等待的任务数
  tasks_succeeded: number; // 成功处理的任务数
  tasks_failed: number; // 处理失败的任务数
  tasks_duplicated: number; // 被去重过滤的任务数
  upstream_counts: Record<string, number>; // 各上游节点传输给本节点的任务数量
  downstream_counts: Record<string, number>; // 本节点传输给各下游节点的任务数量
  start_time: number; // 启动 Unix 时间戳
  elapsed_time: number; // 已运行秒数
};

export type StatusPullResponse = ApiVersionedResponse<Record<string, NodeStatus>> & {
  timestamp: number; // 本次状态快照的统一时间戳
};

// ==== 图元信息：/api/pull_graph_meta ====

/** 节点的构建期元信息，不进每轮状态快照 */
type NodeMeta = {
  class_name: string; // 节点类名（TaskStage/TaskSplitter/TaskRouter）
  execution_mode: string; // 运行模式（serial/thread/async）
  max_workers: number; // 最大并发数
};

/** 图拓扑分析结果，随图元信息一次性到达 */
type AnalysisData = {
  name: string; // 任务图名称
  startTime: number; // 任务图启动时间戳
  className: string; // 图结构分类名称
  isDAG: boolean; // 当前任务图是否为 DAG
  graphMode: string; // 图级执行模式名称
  layersDict: Record<string, unknown>; // 层级分析结果，键数量可用于统计层数
};

/**
 * 图元信息：图拓扑、各节点构建期元信息与图分析结果
 *
 * 三者由 reporter 在同一次 push 中原子写入，因此 `nodes` 非空即表示
 * 拓扑、`node_meta` 与 `analysis` 均已就绪。
 */
export type GraphMeta = {
  nodes: string[]; // 全量节点名列表
  edges: Record<string, string[]>; // 有向边邻接表
  source_nodes: string[]; // 入度为 0 的源节点列表
  node_meta: Record<string, NodeMeta>; // 各节点的构建期元信息
  analysis: AnalysisData | null; // 图分析结果；reporter 尚未推送时为 null
};

export type GraphMetaPullResponse = ApiVersionedResponse<GraphMeta>; // 图元信息拉取响应

// ==== 错误日志：/api/pull_errors ====

/** 单条错误数据定义 */
export type ErrorData = {
  ts: number; // 生命周期时间戳，单位为秒
  stage: string; // 错误发生的节点/阶段名称，用于节点筛选
  event_id: number; // 失败事件的唯一标识 ID，全局唯一
  error_type: string; // 错误的分类类型，用于区分不同类别的错误
  error_message: string; // 错误的具体描述信息，是错误的详细文本内容
  task_json: unknown; // 触发该错误的任务数据，同时用于展示与重试回填
  result_json: unknown; // 成功结果或失败时的占位结果
};

export type ErrorsPullResponse = {
  rev: number; // 错误数据版本号
  page: number; // 当前页码
  page_size: number; // 每页条数
  total: number; // 总记录数
  total_pages: number; // 总页数
  sort_order: "newest" | "oldest"; // 当前排序顺序
  data: ErrorData[] | null; // 当前页的错误记录
};

// ==== 错误类型聚合：/api/pull_error_type_counts ====

export type ErrorTypeCount = {
  error_type: string; // 错误类型名称
  count: number; // 该类型的错误条数
};

export type ErrorTypeCountsPullResponse = ApiVersionedResponse<ErrorTypeCount[]>; // 错误类型聚合响应

// ==== 配置：/api/pull_config ====

export type DashboardColumnKey = "left" | "middle" | "right"; // 仪表盘三栏布局 key

export type DashboardLayout = Record<DashboardColumnKey, string[]>; // 每个栏位内的卡片 ID 顺序

export type ErrorColumnKey =
  | "index"
  | "event_id"
  | "message"
  | "stage"
  | "task"
  | "time"
  | "retry"; // 错误日志表格可配置字段 key

export type StructureEdgeLabel = "none" | "delta" | "cumulative"; // 结构图边标签显示模式：无 / 增量 / 累计

type WebGlobalConfig = {
  theme: "light" | "dark"; // 界面主题
  autoRefreshEnabled: boolean; // 是否启用自动轮询刷新
  refreshInterval: number; // 全局轮询刷新间隔（毫秒）
  language: Lang; // 界面语言
};

type WebDashboardConfig = {
  historyLimit: number; // 节点处理历史记录保留条数
  structureEdgeLabel: StructureEdgeLabel; // 结构图边标签显示模式
  useTotalPendingInStatus: boolean; // 节点状态卡是否使用 total_tasks_pending
  layout: DashboardLayout; // 仪表盘左右中三栏的卡片布局
};

type WebErrorsConfig = {
  pageSize: number; // 错误日志每页显示条数
  sortOrder: "newest" | "oldest"; // 错误日志默认排序方式
  jumpToInjectionAfterRetry: boolean; // 错误日志点击任务注入后是否切换到任务注入页
  columns: ErrorColumnKey[]; // 错误日志表格当前显示字段与顺序
};

type WebInjectionConfig = {
  showInjectableOnly: boolean; // 注入页是否只显示可注入节点
};

export type WebConfig = {
  global: WebGlobalConfig; // 全局共享配置
  dashboard: WebDashboardConfig; // 仪表盘页配置
  errors: WebErrorsConfig; // 错误页配置
  injection: WebInjectionConfig; // 注入页配置
};

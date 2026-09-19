/**
 * 全局类型声明文件
 *
 * 只含两部分：外部库（Chart.js / Sortable.js / Mermaid）的最小类型定义，
 * 以及由其他脚本导出的全局变量与函数声明。
 * 前后端契约类型见 types.d.ts。
 */

declare function preloadInjectionDraftFromError(
  nodeName: string,
  taskData: unknown,
  jumpToInjection?: boolean,
): void;

type ChartPoint = { x: number; y: number }; // Chart.js 折线图点坐标

type ChartDataset = {
  label: string; // 数据集标签，通常为节点名
  data: ChartPoint[] | number[]; // 折线图点集合或环形图数值集合
  borderColor?: string | string[]; // 线条颜色或扇区边框色
  backgroundColor?: string | string[]; // 扇区背景色
  borderWidth?: number; // 边框宽度
  fill?: boolean; // 是否填充区域
  tension?: number; // 曲线平滑程度
  hidden?: boolean; // 是否隐藏该数据集
};

type ChartLegendItem = {
  datasetIndex: number; // 对应的数据集索引
  hidden?: boolean; // 当前图例项是否隐藏
};

type ChartLegend = {
  legendItems: ChartLegendItem[]; // 当前图例项集合
};

type ChartScaleConfig = {
  ticks: { color: string }; // 坐标刻度文字配置
  grid: { color: string }; // 网格线配置
  title: {
    display: boolean; // 是否显示标题
    text: string; // 轴标题文案
    color: string; // 标题颜色
  };
  border: { color: string }; // 轴边框颜色
};

type ChartOptions = {
  animation: boolean; // 是否启用动画
  responsive: boolean; // 是否自适应容器尺寸
  plugins: {
    legend?: {
      display?: boolean; // 是否显示内建图例
      labels?: {
        color: string; // 图例文字颜色
      };
      onClick?: (
        event: Event,
        legendItem: ChartLegendItem,
        legend: { chart: ChartInstance },
      ) => void; // 图例点击回调
    };
  };
  interaction?: {
    intersect: boolean; // 是否要求鼠标必须与点相交
    mode: string; // 交互模式
  };
  scales?: {
    x: ChartScaleConfig; // X 轴配置
    y: ChartScaleConfig; // Y 轴配置
  };
  cutout?: string; // 环形图内圈大小
};

interface ChartInstance {
  data: {
    labels: string[]; // 横轴标签
    datasets: ChartDataset[]; // 所有折线数据集
  };
  options: ChartOptions; // 图表配置
  legend?: ChartLegend; // 图例运行时对象
  destroy(): void; // 销毁实例
  update(): void; // 触发重绘
  getDatasetMeta(index: number): { hidden: boolean | null }; // 获取数据集元信息
}

declare const Chart: {
  new (
    ctx: CanvasRenderingContext2D | null,
    config: {
      type: string;
      data: ChartInstance["data"];
      options: ChartOptions;
    },
  ): ChartInstance;
};

type SortableInstance = {
  destroy(): void; // 销毁当前拖拽实例并释放监听器
};

declare const Sortable: {
  create(
    element: HTMLElement,
    options: {
      group: string;
      animation: number;
      ghostClass: string;
      dragClass: string;
    },
  ): SortableInstance; // 创建一个可拖拽区域
};

type MermaidApi = {
  run(): void; // 扫描页面中的 Mermaid 源码并执行渲染
};

interface Window {
  mermaid: MermaidApi; // 挂在 window 上的 Mermaid 运行时对象
}

/** 支持的界面语言类型 */
type Lang = "zh-CN" | "en" | "ja";

/** 当前选中的语言标识 */
declare var currentLang: Lang;

/** 设置当前语言并更新 HTML 根节点 */
declare function setLang(lang: Lang): void;

/** 根据翻译键获取当前语言的文本 */
declare function t(key: string, ...args: string[]): string;

/** 将国际化属性应用到 DOM 元素 */
declare function applyI18nDOM(): void;

/** 根据当前配置重绘错误日志表头 */
declare function renderErrorsTableHeader(): void;

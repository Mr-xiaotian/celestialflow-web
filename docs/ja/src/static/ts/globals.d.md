# src/celestialflow_web/static/ts/globals.d.ts

> 📅 最終更新日: 2026/09/24

グローバル型宣言ファイル。CDN の外部スクリプトによって注入され、グローバルに可視化する必要がある最小限の型（Chart.js、Sortable.js、Mermaid）のみを含みます。

> フロントエンド／バックエンドの契約型（インターフェース payload / レスポンス、設定構造など）は [`types.d.ts`](types.d.md) に一括して置かれます。本ファイルは純粋な型宣言（`.d.ts`）であり、`.js` 成果物を生成しないため、`scripts.html` で参照する必要はありません。

## Chart.js の型

```typescript
type ChartPoint = { x: number; y: number };

type ChartDataset = {
  label: string;
  data: ChartPoint[] | number[];
  borderColor?: string | string[];
  backgroundColor?: string | string[];
  borderWidth?: number;
  fill?: boolean;
  tension?: number;
  hidden?: boolean;
};

type ChartLegendItem = {
  datasetIndex: number;
  hidden?: boolean;
};

type ChartLegend = {
  legendItems: ChartLegendItem[];
};

type ChartScaleConfig = {
  ticks: { color: string };
  grid: { color: string };
  title: { display: boolean; text: string; color: string };
  border: { color: string };
};

type ChartOptions = {
  animation: boolean;
  responsive: boolean;
  plugins: {
    legend?: {
      display?: boolean;
      labels?: { color: string };
      onClick?: (event: Event, legendItem: ChartLegendItem, legend: { chart: ChartInstance }) => void;
    };
  };
  interaction?: { intersect: boolean; mode: string };
  scales?: { x: ChartScaleConfig; y: ChartScaleConfig };
  cutout?: string;
};

interface ChartInstance {
  data: { labels: string[]; datasets: ChartDataset[] };
  options: ChartOptions;
  legend?: ChartLegend;
  destroy(): void;
  update(): void;
  getDatasetMeta(index: number): { hidden: boolean | null };
}

declare const Chart: {
  new (ctx: CanvasRenderingContext2D | null, config: {
    type: string;
    data: ChartInstance["data"];
    options: ChartOptions;
  }): ChartInstance;
};
```

## Sortable.js の型

```typescript
type SortableInstance = {
  destroy(): void;
};

declare const Sortable: {
  create(element: HTMLElement, options: {
    group: string;
    animation: number;
    ghostClass: string;
    dragClass: string;
  }): SortableInstance;
};
```

## Mermaid の型

```typescript
type MermaidApi = {
  run(): void; // ページ内の Mermaid ソースをスキャンしてレンダリングを実行
};

interface Window {
  mermaid: MermaidApi;
}
```

`mermaid` は `partials/head.html` 内の ESM `<script type="module">` によって初期化され `window` にマウントされ、`dashboard_structure.ts` が `window.mermaid.run()` を呼び出すために使用します。

## 型の関係

```mermaid
flowchart LR
    subgraph "globals.d.ts"
        direction TB
        subgraph "Chart.js"
            CPT[ChartPoint]
            CDS[ChartDataset]
            CLI[ChartLegendItem]
            CLE[ChartLegend]
            CSC[ChartScaleConfig]
            COP[ChartOptions]
            CI[ChartInstance]
        end
        subgraph "外部ライブラリ"
            SORT[Sortable]
            SORTI[SortableInstance]
            MER[MermaidApi]
        end
    end

    subgraph "実装ファイル"
        DH[dashboard_history.ts]
        DET[dashboard_error_types.ts]
        LE[layout_editor.ts]
        ER[errors.ts]
        DST[dashboard_structure.ts]
    end

    CI --> DH
    CI --> DET
    SORT --> LE
    SORT --> ER
    MER --> DST
```

## 使用例

```typescript
// これらの型はグローバル宣言であり、import なしで任意の TS モジュールから直接使用できます：
const ctx = (document.getElementById("node-progress-chart") as HTMLCanvasElement).getContext("2d");
const chart: ChartInstance = new Chart(ctx, {
  type: "line",
  data: { labels: [], datasets: [] },
  options: { animation: false, responsive: true },
});
chart.destroy();

const zone = document.getElementById("layout-dropzone-left")!;
const sortable = Sortable.create(zone, {
  group: "dashboard-layout",
  animation: 150,
  ghostClass: "dragging",
  dragClass: "dragging",
});
sortable.destroy();

window.mermaid.run();
```

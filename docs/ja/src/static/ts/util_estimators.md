# src/celestialflow_web/static/ts/util_estimators.ts

> 📅 最終更新日: 2026/09/24

グラフレベル派生指標の推定モジュール。フロントエンド独自のグラフレベル推定：同一の状態スナップショット内の生のカウントと静的なトポロジのみに依存し、各ノードのグローバルな待機タスク量と予想残り時間を推算します。

## 型定義

```typescript
/** 有向辺の隣接リスト：{上流ノード: [下流ノード, ...]} */
type GraphEdges = Record<string, string[]>;

/** ノード名をキーとするカウントマップ */
export type CountMap = Record<string, number>;

/** 各ノードが各下流へ送るタスク数：{上流ノード: {下流ノード: タスク数}} */
export type DownstreamMap = Record<string, Record<string, number>>;

/** グラフトポロジインデックス：ノード全集と前駆隣接リスト */
type GraphIndex = {
  nodes: string[];                        // 全ノード名。辺リストのキー集合と一致
  predecessors: Record<string, string[]>; // 各ノードの前駆リスト
};
```

## 関数

### `calcGlobalPending(edges, processedMap, pendingMap, downstreamMap): CountMap`

タスクグラフ（DAG）に基づいて各ノードのグローバルな待機タスク数を推定します（保守的／輻輳増幅型）。

**アルゴリズム：** 上流－下流の各組み合わせに対して独立した増幅係数を維持します：

```
scale[u][w] = total_u * output_u->w / max(1, proc_u)
```

ここで `output_u->w / proc_u` は u の w に対する産出比で、u 自身の単一スナップショットから取得し（`proc_u` と同源で一致）、ノード間のスナップショット時間差の影響を避けます。これに基づいて各ノードの予想総入力量を再帰的に求めます：

```
total_v = external_v + sum(scale[u][v] for u in preds(v))
```

ここで `external_v = max(0, seen_v - sum(output_u->v))` は外部注入タスク数で、上流の増幅には関与しません。`seen_v = processed_v + pending_v`。予想残りタスク数は `max(pending_v, total_v - processed_v)` です。

トポロジ順に 1 パスで伝播します：あるノードを処理するとき、そのすべての前駆はすでに確定しています。渡されたグラフが DAG でない場合（`topoSort()` が `null` を返す）、`Error("calcGlobalPending() requires a DAG edges map")` をスローします —— 呼び出し元（`loaders.ts`）は先に `analysis.isDAG` で判定し、非 DAG のときはノード自身の待機量に退化させ、本関数を呼び出しません。

| 引数 | 型 | 説明 |
|------|------|------|
| `edges` | `GraphEdges` | 有向辺の隣接リスト。ノードは map の key に対応する必要がある |
| `processedMap` | `CountMap` | 各ノードが完了したタスク数 |
| `pendingMap` | `CountMap` | 各ノードの現在の残りタスク数 |
| `downstreamMap` | `DownstreamMap` | 各ノードが実際に各下流へ送信したタスク数。欠落しているノードや下流は 0 として扱う |

**戻り値：** `CountMap`、推定された各ノードのグローバルな待機タスク数。

### `calcRemaining(processed, pending, elapsed): number`

処理済みタスク、残りタスク、消費済み時間に基づいて予想残り時間を計算します：`pending / processed * elapsed`。`processed` または `pending` が 0 のときは `0` を返します。

| 引数 | 型 | 説明 |
|------|------|------|
| `processed` | `number` | 処理済みタスク数 |
| `pending` | `number` | 待機タスク数 |
| `elapsed` | `number` | 消費済み時間（秒） |

## 内部補助関数（非エクスポート）

- `buildGraphIndex(edges)`：ノード全集と前駆隣接リストを構築。
- `topoSort(edges)`：隣接リストに対して Kahn のトポロジカルソートを実行；グラフに閉路が存在する場合は `null` を返す。

## 使用例

```typescript
import { calcGlobalPending, calcRemaining } from "./util_estimators.js";

const edges = { A: ["B"], B: ["C"], C: [] };
const processed = { A: 100, B: 80, C: 50 };
const pending = { A: 10, B: 20, C: 5 };
const downstream = { A: { B: 100 }, B: { C: 80 }, C: {} };

const totalPending = calcGlobalPending(edges, processed, pending, downstream);
// totalPending["C"] は上流リンクを含むグローバルな待機量の推定

const remaining = calcRemaining(processed["B"], totalPending["B"], 3600);
console.log(totalPending, remaining);
```

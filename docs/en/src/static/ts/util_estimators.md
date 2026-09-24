# src/celestialflow_web/static/ts/util_estimators.ts

> 📅 Last Updated: 2026/09/24

Graph-level derived metric estimation module. Frontend-specific graph-level estimation: relying only on the raw counts within the same status snapshot and the static topology, it infers each node's global pending task count and estimated remaining time.

## Type Definitions

```typescript
/** Directed edge adjacency list: {upstream node: [downstream node, ...]} */
type GraphEdges = Record<string, string[]>;

/** Count mapping keyed by node name */
export type CountMap = Record<string, number>;

/** Number of tasks each node sends to each downstream: {upstream node: {downstream node: task count}} */
export type DownstreamMap = Record<string, Record<string, number>>;

/** Graph topology index: full node set and predecessor adjacency list */
type GraphIndex = {
  nodes: string[];                        // All node names, consistent with the edge table key set
  predecessors: Record<string, string[]>; // Predecessor list of each node
};
```

## Functions

### `calcGlobalPending(edges, processedMap, pendingMap, downstreamMap): CountMap`

Estimates each node's global pending task count based on the task graph (DAG) (conservative / congestion-amplified).

**Algorithm:** maintains an independent amplification factor for each upstream-downstream pair:

```
scale[u][w] = total_u * output_u->w / max(1, proc_u)
```

Here `output_u->w / proc_u` is the output ratio of u to w, taken from u's own single snapshot (from the same source as `proc_u`), avoiding the impact of snapshot time differences across nodes. Based on this, each node's estimated total input is recursively computed:

```
total_v = external_v + sum(scale[u][v] for u in preds(v))
```

Here `external_v = max(0, seen_v - sum(output_u->v))` is the number of externally injected tasks and does not participate in upstream amplification; `seen_v = processed_v + pending_v`. The estimated remaining task count is `max(pending_v, total_v - processed_v)`.

Single-pass propagation in topological order: by the time any node is processed, all of its predecessors have been finalized. If the passed-in graph is not a DAG (`topoSort()` returns `null`), it throws `Error("calcGlobalPending() requires a DAG edges map")` — the caller (`loaders.ts`) first checks with `analysis.isDAG`, and degrades to the node's own pending amount without calling this function when it is not a DAG.

| Parameter | Type | Description |
|------|------|------|
| `edges` | `GraphEdges` | Directed edge adjacency list; nodes must correspond to the map's keys |
| `processedMap` | `CountMap` | Number of tasks each node has completed |
| `pendingMap` | `CountMap` | Number of tasks each node currently has remaining |
| `downstreamMap` | `DownstreamMap` | Number of tasks each node actually sent to each downstream; missing nodes or downstreams are treated as 0 |

**Returns:** `CountMap`, the estimated global pending task count of each node.

### `calcRemaining(processed, pending, elapsed): number`

Computes the estimated remaining time based on processed tasks, remaining tasks, and elapsed time: `pending / processed * elapsed`. Returns `0` when `processed` or `pending` is 0.

| Parameter | Type | Description |
|------|------|------|
| `processed` | `number` | Number of processed tasks |
| `pending` | `number` | Number of pending tasks |
| `elapsed` | `number` | Elapsed time (seconds) |

## Internal Helper Functions (not exported)

- `buildGraphIndex(edges)`: builds the full node set and predecessor adjacency list.
- `topoSort(edges)`: performs Kahn topological sort on the adjacency list; returns `null` when the graph contains a cycle.

## Usage Examples

```typescript
import { calcGlobalPending, calcRemaining } from "./util_estimators.js";

const edges = { A: ["B"], B: ["C"], C: [] };
const processed = { A: 100, B: 80, C: 50 };
const pending = { A: 10, B: 20, C: 5 };
const downstream = { A: { B: 100 }, B: { C: 80 }, C: {} };

const totalPending = calcGlobalPending(edges, processed, pending, downstream);
// totalPending["C"] is the global pending estimate including upstream chains

const remaining = calcRemaining(processed["B"], totalPending["B"], 3600);
console.log(totalPending, remaining);
```

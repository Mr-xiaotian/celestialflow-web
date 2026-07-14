# Subagent Base Rules（celestialflow-web 项目专属）

> 本文件定义 `celestialflow-web` 项目的专属路径映射规则。
>
> 通用规则（输出格式、源文件删除/移动处理等）请参阅 `~/.agents/skills/docs-zh-sync/_subagent-base.md`。
>
> 开始工作前，请按顺序阅读：
> 1. `~/.agents/skills/docs-zh-sync/_subagent-base.md`
> 2. `~/.agents/skills/docs-zh-sync/_subagent-audit.md`
> 3. `~/.agents/skills/docs-zh-sync/_subagent-writing.md`
> 4. 本文件
> 5. 主 agent 指定的区域 `subagent-*.md`

---

## 路径映射规则

### 根目录映射

| 代码路径 | 文档路径 |
|---------|---------|
| `src/celestialflow_web/...` | `docs/zh-CN/src/...` |
| `tests/...` | `docs/zh-CN/tests/...` |

### 后缀映射

| 代码后缀 | 文档后缀 |
|:-------:|:-------:|
| `.py` | `.md` |
| `.ts` | `.md` |
| `.html` | `.md` |
| `.css` | `.md` |
| `__init__.py` | `__init__.md` |
| `.d.ts` | `.d.md` |

### 示例

| 代码文件 | 文档文件 |
|---------|---------|
| `src/celestialflow_web/server/core_server.py` | `docs/zh-CN/src/server/core_server.md` |
| `src/celestialflow_web/routes/core_pull.py` | `docs/zh-CN/src/routes/core_pull.md` |
| `src/celestialflow_web/runtime/util_models.py` | `docs/zh-CN/src/runtime/util_models.md` |
| `src/celestialflow_web/static/ts/main.ts` | `docs/zh-CN/src/static/ts/main.md` |
| `src/celestialflow_web/static/ts/globals.d.ts` | `docs/zh-CN/src/static/ts/globals.d.md` |
| `src/celestialflow_web/static/css/dashboard.css` | `docs/zh-CN/src/static/css/dashboard.md` |
| `src/celestialflow_web/templates/index.html` | `docs/zh-CN/src/templates/index.md` |
| `tests/test_server.py` | `docs/zh-CN/tests/test_server.md` |

## 项目特有注意事项

- 当前仓库已经从 `CelestialFlow` 主仓库拆分出来，若发现文档仍保留 `celestialflow.web.*`、`src/celestialflow/web/...` 等旧路径，应视为高优先级过期内容。
- 当前后端结构以 `server/`、`routes/`、`runtime/` 为准；若发现旧的平铺文档路径（如 `docs/zh-CN/src/core_server.md`、`docs/zh-CN/src/util_*.md`），优先迁移到镜像路径并清理旧文档。
- `static/js/` 为编译产物，默认不审计；前端文档以 `static/ts/` 与 `templates/` 为准。
- `package.json`、`package-lock.json`、`tsconfig.json`、`config.json` 默认不镜像为中文文档。
- 若源码文件发生重命名，例如 `pull_routes.py` → `core_pull.py`，应同步执行文档重命名，并检查其他文档中的交叉引用是否仍指向旧名称。

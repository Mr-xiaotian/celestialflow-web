# Agents

## 环境

- uv: 0.10.6
- Python: 3.14.3

## 代码规范

### 风格

- 不要做任何兼容性修改。
- 除非特意要求，否则不必要修改 `docs` 目录下的文件。

### 修改完文件

- 如果修改对象是 `.py` 文件, 执行 `uv run ruff check --fix .` 与 `uv run pyright .` 检查并修复代码格式与类型错误。
- 如果修改对象是 `.py` 文件, 执行 `uv run pytest <相关测试文件>` 运行相关测试。
- 如果修改对象是代码文件, 为代码添加或者更新reST风格的doc-string, 并保持与代码逻辑一致。
- 除非特意要求, 不必同步更改docs/下的相应文档。

## 与其他项目的关联

### CelestialFlow

- 位于: ../CelestialFlow
- 关系: 本项目为 CelestialFlow 提供可视化的web界面

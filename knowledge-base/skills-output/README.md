# Skills 输出目录

本目录存放由 skill-generator 自动生成的 Skill 副本。

## 使用方式

通过 `/skill-generator` 生成的 Skill 会自动安装到 `.claude/skills/`，并在本目录保存一份 Markdown 备份。

## 项目颜色图例

| 颜色 | 项目 | 色值 | 含义 |
|------|------|------|------|
| 🔵 | `cae-agent` | `#2563EB` | CAE 仿真分析 |
| 🟢 | `reasonix` | `#16A34A` | 知识/Skill 系统 |
| 🟣 | `obsidian-stack` | `#7C3AED` | 上游融合来源 |
| 🟠 | `ansys-tools` | `#EA580C` | ANSYS 执行工具 |
| ⚪ | `fable5` | `#6B7280` | 跨项目通用模板 |

## 已生成

| Skill | 项目 | 类型 | 模块 | 生成日期 |
|-------|------|------|------|----------|
| (暂无) | — | — | — | 等待首次 `/skill-generator` 调用 |

## 可以生成的方向

### 🔵 cae-agent 项目
- `modal-analysis-post` — 模态分析后处理 Skill
- `contact-debugger` — 接触问题诊断 Skill
- `material-calibration` — 材料参数校准 Skill
- `solver-report-writer` — 求解分析报告自动生成 Skill
- `mesh-quality-checker` — 网格质量检查 Skill

### 🟢 reasonix 项目
- `knowledge-indexer` — 知识库索引与搜索 Skill
- `workflow-automator` — 多步骤工作流编排 Skill

### 🟠 ansys-tools 项目
- `mapdl-batch-runner` — MAPDL 批量执行 Skill
- `result-extractor` — 求解结果提取与可视化 Skill

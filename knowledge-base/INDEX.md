# 知识库索引

> 按项目颜色分类的知识库全景导航。颜色规则详见 [项目颜色注册表](projects/project-registry.md)。

---

## 🔵 cae-agent（CAE 蓝 `#2563EB`）— 仿真自动化核心

### Skills（`.claude/skills/`）

| Skill | 描述 | 类型 |
|-------|------|------|
| `check-ansys-env` | 检查 LLM + PyMAPDL + PyMechanical 完整环境状态 | 诊断工具 |
| `run-log-analysis` | 分析 ANSYS 求解日志，检测错误 + LLM 诊断 + Markdown 报告 | 分析工具 |
| `run-mapdl-input` | 执行 .inp/.dat/.mac 输入文件，可选自动分析结果 | 执行工具 |
| `batch-contact` | 按 Named Selection 前缀批量创建 Mechanical 接触对（242+） | 自动化工具 |

### 领域知识（`knowledge-base/domain-knowledge/`）

| 文档 | 描述 |
|------|------|
| `contact-analysis-best-practices.md` | ANSYS 接触算法选择、刚度设置、错误排查指南 |

### Python 模块

| 模块 | 职责 |
|------|------|
| `main.py` | FastAPI 入口，9 个 REST 端点 |
| `log_parser.py` | 日志解析 + 正则错误检测（4 类关键词） |
| `llm_analyzer.py` | DeepSeek LLM 分析 + 本地规则回退 |
| `report_generator.py` | Markdown 报告生成 |
| `ansys_runner.py` | PyMAPDL 封装（.inp/.dat/.mac 执行） |
| `mechanical_runner.py` | PyMechanical 242+ 批量接触 |

### MCP 服务器

| Server | 工具数 | 用途 |
|--------|--------|------|
| `ansys-local` | 5 | mapdl_status, mapdl_execute, mapdl_demo, mechanical_status, mechanical_batch_contact |

---

## 🟢 reasonix（知识绿 `#16A34A`）— Skill 生成与工作流

### Skills（`.reasonix/skills/`）

| Skill | 描述 | 类型 |
|-------|------|------|
| `skill-generator` | 📦 元 Skill：读取 Fable5 知识库 → 自动生成专业 Skill | 元工具 |
| `git-workflow` | Git 提交/推送/PR 全流程自动化 | 工作流 |
| `meeting-notes-organizer` | 会议对话 → 结构化 Markdown 笔记 | 生产力 |

### Skill 输出（`knowledge-base/skills-output/`）

| 文件 | 描述 |
|------|------|
| `README.md` | 生成 Skill 的备份目录和说明 |

---

## 🟣 obsidian-stack（上游紫 `#7C3AED`）— 原始上游

| 资源 | 链接/路径 |
|------|----------|
| GitHub 仓库 | https://github.com/R0Bdhc/obsidian_stack |
| 融合分支 | `master`（已合并 main 分支内容） |
| 原始 Skills | Reasonix Knowledge System（13 个文件） |

---

## 🟠 ansys-tools（工具橙 `#EA580C`）— ANSYS 执行工具

### MCP 工具详情

| 工具 | 函数 | 说明 |
|------|------|------|
| `mapdl_status` | 查询 MAPDL 状态 | 检查 PyMAPDL 是否可用、版本信息 |
| `mapdl_execute` | 执行 MAPDL 输入 | 运行 .inp/.dat/.mac 文件 |
| `mapdl_demo` | 运行 MAPDL Demo | 快速验证 MAPDL 功能 |
| `mechanical_status` | 查询 Mechanical 状态 | 检查 PyMechanical 是否可用 |
| `mechanical_batch_contact` | 批量创建接触对 | 按 Named Selection 前缀自动配对 |

### REST API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/analyze-log` | POST | 分析 ANSYS 求解日志 |
| `/run-mapdl-input` | POST | 执行 MAPDL 输入文件 |
| `/batch-contact` | POST | 批量创建 Mechanical 接触对 |
| `/health` | GET | 健康检查 |

---

## ⚪ fable5（模板灰 `#6B7280`）— 提示词工程模板

### 提示词模板（`knowledge-base/prompts/fable5/`）

| 文件 | 描述 |
|------|------|
| `fable5-modules.md` | 10 大行为模块拆解（M1-M9） |
| `fable5-full-prompt.md` | 完整 Fable5 系统提示词参考（164 行） |

### 构造模板（`knowledge-base/templates/`）

| 文件 | 描述 |
|------|------|
| `skill-template.md` | Skill 构造模板（M0-M10，含 CAE 专用模块） |

### 项目配置（`knowledge-base/projects/`）

| 文件 | 描述 |
|------|------|
| `project-registry.md` | 项目颜色注册表（5 项目 + 色值 + 映射规则） |

---

## 颜色速查

```
🔵 #2563EB  cae-agent      仿真分析、ANSYS 自动化
🟢 #16A34A  reasonix        知识管理、Skill 生成
🟣 #7C3AED  obsidian-stack  上游融合来源
🟠 #EA580C  ansys-tools     MAPDL/Mechanical 执行
⚪ #6B7280  fable5          通用模板（横跨项目）
```

---

> **最后更新**: 2026-07-04 | **项目总数**: 5 | **Skills 总数**: 7 | **MCP 工具**: 8

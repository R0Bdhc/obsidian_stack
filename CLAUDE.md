# CLAUDE.md — cae-agent

面向 ANSYS 场景的最小可运行 CAE 智能辅助系统。

## 架构概览

```
main.py          FastAPI 入口，9 个 REST 端点，组装层
├─ log_parser.py      日志解析 + 正则错误检测（4 类关键词）
├─ llm_analyzer.py    DeepSeek LLM 分析 + 本地规则回退
├─ report_generator.py Markdown 报告生成
├─ ansys_runner.py    PyMAPDL 封装（.inp/.dat/.mac 执行）
└─ mechanical_runner.py PyMechanical 242+ 批量接触
```

核心链路：`日志 → 错误检测 → LLM分析 → Markdown报告`

## 常用命令

```bash
# 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 仅安装核心依赖
pip install -r requirements.txt

# 可选：安装 Mechanical 支持
pip install -r requirements-mechanical.txt

# 测试日志分析
curl -X POST http://127.0.0.1:8000/analyze-log \
  -H "Content-Type: application/json" \
  -d '{"log_path": "D:\\ansysagent\\sample_logs\\demo_solver.out"}'
```

## 关键约定

- **两阶段设计**：所有执行端点默认 preview 模式，需显式传 `launch_*=true` 才真实启动求解器
- **运行时目录重定向**：PyMAPDL/PyMechanical 的 `LOCALAPPDATA` 被重定向到 `runtime_data/`，避免 C 盘权限问题
- **LLM 回退**：无 API Key 时自动降级到本地规则分析（覆盖奇异矩阵、不收敛、接触穿透三类）
- **环境变量**：统一由 `.env` 管理，通过 `python-dotenv` 加载
- **日志文件优先级**：`.out > .log > .err`，过滤隐藏文件和临时文件
- **Windows 路径**：默认 ANSYS 安装路径在 `D:\ANSYS Inc\v241\`

## 模块职责边界

| 模块 | 职责 | 禁止 |
|------|------|------|
| `main.py` | 路由、请求校验、模块串联 | 不写业务逻辑 |
| `log_parser.py` | 正则匹配 + 日志截取 | 不调用外部服务 |
| `llm_analyzer.py` | LLM 调用 + 回退规则 | 不读写文件 |
| `report_generator.py` | Markdown 拼装 + 落盘 | 不分析、不调用 API |
| `ansys_runner.py` | MAPDL 生命周期管理 | 不分析日志 |
| `mechanical_runner.py` | Mechanical 批量接触 | 不处理 MAPDL |

## 扩展错误检测

在 `log_parser.py` 的 `ERROR_PATTERNS` 字典中添加：
```python
"new_error": {
    "pattern": r"your\s+regex\s+pattern",
    "title": "错误中文标题",
    "description": "该错误的工程含义。",
}
```

## 环境要求

- Python 3.11+
- Windows + ANSYS 241+（PyMAPDL 真实执行需要）
- ANSYS 242+（PyMechanical 批量接触需要）
- DeepSeek API Key（可选，无 Key 时回退本地规则）

## MCP 服务器

本项目注册了 3 个 MCP 服务器（配置见 `.mcp.json`）：

| MCP Server | 工具 | 用途 |
|-----------|------|------|
| `ansys-local` | `mapdl_status`, `mapdl_execute`, `mapdl_demo`, `mechanical_status`, `mechanical_batch_contact` | PyMAPDL/PyMechanical 执行和状态查询 |
| `deepseek` | `chat_completion`, `completion`, `get_user_balance` | DeepSeek V4 LLM 分析（与 llm_analyzer.py 共用 API Key） |
| `filesystem` | 文件读写 (MCP 标准) | 安全访问工作目录：sample_inputs, sample_logs, ansys_workspace, reports |

**何时使用 MCP vs REST API:**
- MCP: 当用户直接在 Claude Code 对话中操作，MCP 工具更直接（Claude → Python 模块，无 HTTP 中转）
- REST API: 当外部系统/脚本需要调用，或需要 FastAPI 的 OpenAPI 文档和类型校验

## Skills 目录

### `.claude/skills/` — CAE 领域 Skills

| Skill | 描述 | 触发方式 |
|-------|------|---------|
| `check-ansys-env` | 检查 LLM + PyMAPDL + PyMechanical 完整环境 | `/check-ansys-env` |
| `run-log-analysis` | 分析 ANSYS 求解日志，检测错误 + LLM 诊断 + 报告 | `/run-log-analysis` |
| `run-mapdl-input` | 执行 .inp/.dat/.mac 输入文件并可选自动分析 | `/run-mapdl-input` |
| `batch-contact` | 按 Named Selection 前缀批量创建接触对（242+） | `/batch-contact` |

### `.reasonix/skills/` — 通用/元 Skills（来自 obsidian_stack 融合）

| Skill | 描述 | 触发方式 |
|-------|------|---------|
| `skill-generator` | 读取 Fable5 知识库，自动生成专业 Skill | `/skill-generator` |
| `git-workflow` | Git 提交/推送/PR 全流程自动化 | `/git-workflow` |
| `meeting-notes-organizer` | 会议对话 → 结构化 Markdown 笔记 | `/meeting-notes-organizer` |

## 知识库 (knowledge-base/)

知识库内容按项目颜色分类，详见 [INDEX.md](knowledge-base/INDEX.md) 和 [项目颜色注册表](knowledge-base/projects/project-registry.md)。

```
knowledge-base/
├── INDEX.md                     🔍 颜色分类全景索引
├── projects/
│   └── project-registry.md      🎨 项目颜色注册表（5 项目 → 色值映射）
├── prompts/fable5/              ⚪ Fable5 提示词工程模板（跨项目通用）
│   ├── fable5-modules.md        10 大行为模块拆解 (M1-M9)
│   └── fable5-full-prompt.md    完整系统提示词参考
├── templates/
│   └── skill-template.md        Skill 构造模板 (M0-M10, 含项目颜色 M0)
├── domain-knowledge/            🔵 CAE 领域知识积累
│   └── contact-analysis-best-practices.md
└── skills-output/               生成的 Skill 备份（按项目颜色标记）
```

**项目颜色速查：** 🔵 `cae-agent` | 🟢 `reasonix` | 🟣 `obsidian-stack` | 🟠 `ansys-tools` | ⚪ `fable5`

`book/v241/` 目录存放 ANSYS v241 官方 PDF 手册（100+ 本），可通过 Read 工具直接查阅。

## 工具使用指引

- 读取 ANSYS 手册 → `Read` 工具读取 `book/v241/` 中的 PDF（20 页/次）
- 执行 MAPDL → `mcp__ansys-local__mapdl_execute` 或 `POST /run-mapdl-input`
- LLM 分析日志 → `mcp__deepseek__chat_completion` 或 `POST /analyze-log`
- 文件操作 → `mcp__filesystem__*` 或 `Read`/`Write`/`Edit` 工具
- 启动服务 → `bash("uvicorn main:app --reload --host 0.0.0.0 --port 8000")`
- 生成新 Skill → `/skill-generator` 读取知识库自动生成

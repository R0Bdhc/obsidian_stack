# Unified Obsidian Knowledge

将本地 `knowledge-pipeline`（对话自动精炼）与 `obsidian-skills`（通用 Obsidian 操作能力）合并为统一的三阶段工作流。

**核心价值**：让机器做摄入和初加工，让 AI 做精修，让人做判断。

---

## 合并架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Unified Obsidian Knowledge                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Stage 1: INGEST          Stage 2: REFINE          Stage 3: PUBLISH    │
│  ─────────────────        ─────────────────        ─────────────────   │
│                                                                         │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐  │
│  │conversation-to- │     │ knowledge-refine│     │knowledge-publish│  │
│  │   knowledge     │────▶│  (Orchestrator) │────▶│                 │  │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘  │
│           │                       │                                           │
│  ┌─────────────────┐     ┌───────┴───────┐                            │
│  │ subject-        │     │ 底层 Skills:  │                            │
│  │  induction      │     │               │                            │
│  └─────────────────┘     │ • obsidian-   │                            │
│                          │   markdown    │                            │
│  Pipeline 引擎:          │ • json-canvas │                            │
│  • knowledge_refinery.py │ • obsidian-   │                            │
│  • knowledge_deepener.py │   bases       │                            │
│  • unified_entry.py      │ • obsidian-cli│                            │
│                          │ • defuddle    │                            │
│                          │               │                            │
│  辅助 Skills:            │ 辅助 Skills:  │                            │
│  • fable5-code-          │ • subject-    │                            │
│    principle             │   color-tag   │                            │
│                          └───────────────┘                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 三阶段工作流总览

| 阶段 | 触发方式 | 核心 Skill | 笔记状态 | 人工参与 |
|------|----------|-----------|----------|----------|
| **Stage 1: 摄入** | CLI 自动 / 定时 cron | `conversation-to-knowledge` + `subject-induction` | `inbox` | ❌ 全自动 |
| **Stage 2: 精修** | Claude Code 交互 | `knowledge-refine` (Orchestrator) | `inbox → refined` | ✅ 人机协作 |
| **Stage 3: 发布** | Claude Code 交互 | `knowledge-publish` | `refined` | ✅ 按需执行 |

---

## Skill 清单与使用流程

本项目包含 **11 个 Skills**，分为三层：

### 第一层：Pipeline 自动化（Stage 1）

这些 Skill 由 Python 管线引擎驱动，**无需打开 Claude Code** 即可执行。

#### 1. `conversation-to-knowledge`

**功能**：将 `~/.claude/projects/` 下的 JSONL 对话记录自动转化为结构化 Obsidian 笔记。

**触发条件**：
- 需要整理对话历史
- 需要生成项目文档（技术栈、架构、时间线）
- 对话积累到一定数量，需要归档

**执行命令**：
```bash
# 方式1：统一入口（推荐）
python pipeline/unified_entry.py --stage refinery

# 方式2：直接执行 legacy 脚本
python pipeline/knowledge_refinery.py

# 预览模式（不写入文件）
python pipeline/knowledge_refinery.py --dry-run
```

**输入**：
- `~/.claude/projects/*/*.jsonl` — Claude Code 对话记录

**输出**：
- `D:/knowledgement/🏠 知识总览.md`
- `D:/knowledgement/Projects/<项目>/📋 项目总览.md`
- `D:/knowledgement/Projects/<项目>/📈 更新进度.md`
- `D:/knowledgement/Projects/<项目>/🎯 改进方向.md`
- `D:/knowledgement/Projects/<项目>/🔧 技术栈.md`
- `D:/knowledgement/Projects/<项目>/🔄 能力流程.md`
- `D:/knowledgement/Projects/<项目>/🏗️ 架构设计.md`
- `D:/knowledgement/Projects/<项目>/⚙️ 配置管理.md`
- `D:/knowledgement/Projects/<项目>/conversations/*.md`

**笔记状态**：所有生成笔记的 frontmatter 为 `status: inbox`

---

#### 2. `subject-induction`

**功能**：按五大领域对知识库进行结构化整理和深度归纳。

**触发条件**：
- `conversation-to-knowledge` 执行后自动触发
- 需要补充学科深度知识
- `deep_data.json` 内容更新后

**执行命令**：
```bash
# 方式1：统一入口
python pipeline/unified_entry.py --stage deepener

# 方式2：直接执行
python pipeline/knowledge_deepener_v2.py
```

**输入**：
- `pipeline/data/deep_data.json` — 五大领域深度知识库

**输出**：
- `D:/knowledgement/Knowledge/<领域>/📋 索引.md`
- `D:/knowledgement/Knowledge/<领域>/<知识点>.md`

**领域覆盖**：

| 领域 | 颜色 | 图标 |
|------|------|------|
| 计算力学与有限元 | `#e63946` | 🔴 |
| 软件工程与架构 | `#457b9d` | 🔵 |
| 人工智能与LLM | `#9b5de5` | 🟣 |
| 工程仿真自动化 | `#2a9d8f` | 🟢 |
| 知识管理与工具链 | `#e9c46a` | 🟡 |

---

#### 3. `fable5-code-principle`

**功能**：在创建或编辑 Skill 时，强制应用 Fable 5 行为准则。

**触发条件**：
- 创建新 Skill
- 审查现有 Skill 质量
- 需要提升 Skill 输出质量

**用法**：
```markdown
# 在 Claude Code 中
请按 fable5-code-principle 标准审查这个 skill：
skills/my-new-skill/skill.yaml
```

**标准模块**：
- M3 语气：温暖专业，不假设用户能力不足
- M2 拒绝：安全边界清晰，不协助恶意代码
- M7 错误处理：承认错误、修复问题、不自贬
- M9 身份：渐进式披露，Skill < 500 行

---

#### 4. `subject-color-tag`

**功能**：为五大领域分配视觉颜色标记，提升浏览效率。

**触发条件**：
- `subject-induction` 执行后
- 需要美化知识库
- 建立颜色编码体系

**用法**：
```markdown
# 在 Claude Code 中
请为 Knowledge/ 下的五大领域生成颜色主题 CSS，
保存到 .obsidian/snippets/subject-colors.css
```

**颜色映射**：同上表。

---

### 第二层：精修编排（Stage 2）

这些 Skill 在 **Claude Code 交互环境** 中执行，需要人工指令触发。

#### 5. `knowledge-refine` ⭐ Orchestrator

**功能**：编排所有底层 Skill，对 Vault 进行深度精修。**这是 Stage 2 的核心入口。**

**触发条件**：
- Stage 1 执行完毕后
- 用户说"精修知识库"、"整理链接"、"生成 Canvas"
- 发现笔记链接断裂或需要可视化

**执行流程**：

```bash
# Step 1: 进入 Vault
cd D:/knowledgement
claude
```

```markdown
# Step 2: 在 Claude Code 中执行精修指令

─────────────────────────────────────────
指令 A: 批量精修整个 Vault
─────────────────────────────────────────

请对当前 Vault 执行 knowledge-refine：
1. 扫描所有 status: inbox 的笔记
2. 补全缺失的 [[WikiLinks]]，自动创建或链接到已有笔记
3. 检查 Projects/ansysagent/：
   - 如果对话记录 ≥5 篇，生成 Canvas/ansysagent-项目地图.canvas
   - 确保 6 篇分析笔记之间有交叉链接
4. 检查 Knowledge/ 下每个领域：
   - 更新或生成 📋 索引.md（MOC）
   - 确保知识点之间有交叉链接
5. 将所有处理过的笔记状态更新为 refined
6. 为 refined 笔记添加 refined_date 和 reviewed: true
7. 报告处理了多少篇笔记、创建了多少个 Canvas、补全了多少个链接

─────────────────────────────────────────
指令 B: 精修单个项目
─────────────────────────────────────────

请精修 Projects/ansysagent/：
1. 检查 6 篇分析笔记的链接完整性
2. 在 🔧 技术栈 中补充缺失的模块链接（如 [[log_parser]]、[[llm_analyzer]]）
3. 生成项目架构 Canvas，包含模块依赖关系
4. 更新项目笔记的 status 为 refined

─────────────────────────────────────────
指令 C: 精修单个领域
─────────────────────────────────────────

请精修 Knowledge/计算力学与有限元/：
1. 更新 📋 索引.md，确保包含所有知识点
2. 检查每个知识点是否有 "关联主题" 链接
3. 生成领域知识网络 Canvas
4. 更新状态为 refined
```

**底层调用链**：

```
knowledge-refine (用户指令)
    ├── obsidian-markdown
    │      └── 修复 WikiLinks、规范 Frontmatter
    ├── json-canvas
    │      └── 生成 .canvas 关系图
    ├── obsidian-bases
    │      └── 更新项目追踪数据库
    └── subject-color-tag (可选)
           └── 应用颜色标记
```

**输入**：`status: inbox` 的笔记
**输出**：`status: refined` 的笔记 + `.canvas` + `.base`

---

### 第三层：底层原子能力（被 Orchestrator 调用）

这些 Skill 通常不直接由用户调用，而是由 `knowledge-refine` 编排调用。但高级用户可以直接使用。

#### 6. `obsidian-markdown`

**功能**：创建/编辑 Obsidian Flavored Markdown，支持维基链接、Callout、Properties、标签等。

**直接用法**：
```markdown
请用 obsidian-markdown skill 创建一个概念笔记：
标题："接触分析最佳实践"
标签：["FEA", "接触", "ansys"]
内容：包含 Callout、表格、代码块
保存到：Knowledge/计算力学与有限元/接触分析最佳实践.md
```

#### 7. `json-canvas`

**功能**：创建/编辑 `.canvas` 文件，支持节点、边、群组、连接。

**直接用法**：
```markdown
请用 json-canvas skill 生成一个项目架构 Canvas：
节点：main.py、log_parser.py、llm_analyzer.py、ansys_runner.py
边：main.py → log_parser.py，main.py → llm_analyzer.py
保存到：Canvas/ansysagent-架构图.canvas
```

#### 8. `obsidian-bases`

**功能**：创建/编辑 `.base` 数据库视图，支持筛选器、公式、摘要。

**直接用法**：
```markdown
请用 obsidian-bases skill 创建一个项目追踪视图：
字段：项目名称、状态、优先级、最后更新
数据源：Projects/*/
保存到：Bases/项目追踪.base
```

#### 9. `obsidian-cli`

**功能**：通过 Obsidian CLI 与 Vault 交互，支持插件/主题开发。

**直接用法**：
```markdown
请用 obsidian-cli skill 检查 Vault 中所有断裂的链接。
```

#### 10. `defuddle`

**功能**：从网页提取干净 Markdown，去除广告和杂乱内容。

**直接用法**：
```markdown
请用 defuddle skill 提取 https://example.com/article，
保存到 _Inbox/网页摘录.md。
```

---

### 第四层：发布输出（Stage 3）

#### 11. `knowledge-publish`

**功能**：将精修后的笔记导出为可分享的格式。

**触发条件**：
- 需要分享项目文档给团队
- 需要将知识领域导出为手册
- 需要生成周报/月报

**执行流程**：

```bash
cd D:/knowledgement
claude
```

```markdown
─────────────────────────────────────────
指令 A: 导出项目文档
─────────────────────────────────────────

请将 Projects/ansysagent/ 导出为 markdown-clean 格式：
1. 将 [[WikiLinks]] 转换为标题锚点
2. 移除 Obsidian 特定语法（如 Callout 转为普通引用）
3. 排除 conversations/ 目录
4. 保存到 Exports/ansysagent-docs/

─────────────────────────────────────────
指令 B: 生成领域手册
─────────────────────────────────────────

请将 Knowledge/计算力学与有限元/ 导出为 PDF：
1. 按知识点顺序合并为单文件
2. 添加页眉（领域名称）和页脚（页码）
3. 生成目录
4. 保存到 Exports/FEA-Handbook.pdf
（需要本地安装 Pandoc）

─────────────────────────────────────────
指令 C: 编译周报
─────────────────────────────────────────

请编译本周（2026-07-15 至 2026-07-22）的所有 refined 笔记：
1. 按项目/领域分组
2. 每组生成 3 行摘要
3. 添加执行摘要（Executive Summary）
4. 保存到 Exports/Weekly-2026-W29.md
```

---

## 完整运行示例

### 场景：每周知识库维护

```bash
# ========== Stage 1: 自动化摄入（Terminal）==========

# 1. 执行完整管线
python pipeline/unified_entry.py

# 输出：
# ✅ 配置加载: pipeline/config/pipeline_config.yaml
# 📁 Vault 输出: D:/knowledgement
# 📁 对话源: C:/Users/<user>/.claude/projects
# ============================================================
# ▶️  Knowledge Refinery (对话精炼)
# ============================================================
#   项目: ansysagent (12 个对话)
#     ✓ 2026-07-22 — ANSYS 日志分析优化
#     ✓ 2026-07-21 — PyMAPDL 批量处理
#     ...
#   ✓ 知识总览
#   ✓ 12 篇对话 + 6 篇分析笔记
# ============================================================
# ▶️  Knowledge Deepener (知识深化)
# ============================================================
# 📚 计算力学与有限元: 索引
#   ✓ ANSYS-MAPDL-应用 (2450 chars)
#   ✓ PyMAPDL-集成 (1890 chars)
#   ...
# ✅ 共生成 20 篇深度知识文章 → D:/knowledgement/Knowledge
# ============================================================
# 📊 管线执行完成
# ============================================================


# ========== Stage 2: 交互式精修（Claude Code）==========

cd D:/knowledgement
claude

# 在 Claude Code 中粘贴：
"""
请对当前 Vault 执行 knowledge-refine：
1. 扫描所有 status: inbox 的笔记（应包括刚生成的项目笔记和知识点）
2. 补全 Projects/ansysagent/ 下 6 篇分析笔记之间的交叉链接
3. 由于 ansysagent 有 12 篇对话，生成 Canvas/ansysagent-项目地图.canvas
4. 更新 Knowledge/ 下 5 个领域的 📋 索引.md
5. 确保所有知识点之间有 "关联主题" 链接
6. 将所有处理过的笔记状态更新为 refined
7. 报告：处理笔记数、创建 Canvas 数、补全链接数
"""

# Claude Code 执行后输出示例：
# ✅ 处理了 38 篇笔记
# ✅ 创建了 1 个 Canvas（ansysagent-项目地图）
# ✅ 补全了 47 个 WikiLinks
# ✅ 更新了 5 个领域 MOC


# ========== Stage 3: 按需发布（Claude Code）==========

# 在 Claude Code 中：
"""
请将 Projects/ansysagent/ 导出为 markdown-clean 格式，
保存到 Exports/ansysagent-docs-v1.0/，
用于分享给团队成员。
"""
```

---

## 安装与配置

### 1. 依赖安装

```bash
pip install pyyaml requests
# knowledge_refinery.py 和 knowledge_deepener_v2.py 为纯标准库，无需额外依赖
```

### 2. 配置路径

编辑 `pipeline/config/pipeline_config.yaml`：

```yaml
vault_output: "D:/knowledgement"      # ← 你的 Obsidian Vault 路径
sources:
  claude_projects:
    path: "~/.claude/projects"        # ← Claude Code 对话记录路径
```

### 3. 安装 Skills 到 Claude Code

```bash
# 方式1：复制到 Claude Code 全局 skills 目录
cp -r skills/* ~/.claude/skills/

# 方式2：复制到 Vault 本地（推荐，项目隔离）
cp -r skills/* D:/knowledgement/.claude/skills/
```

### 4. 验证

```bash
# 检查 pipeline
python pipeline/unified_entry.py --dry-run

# 检查 skills
claude
/skills
# 应显示：conversation-to-knowledge, knowledge-refine, obsidian-markdown 等
```

---

## 文件映射关系

| 本合并项目 | 来源 | 说明 |
|-----------|------|------|
| `pipeline/knowledge_refinery.py` | 本地 `knowledge-pipeline` | 核心精炼引擎，未修改 |
| `pipeline/knowledge_deepener_v2.py` | 本地 `knowledge-pipeline` | 核心深化引擎，未修改 |
| `pipeline/unified_entry.py` | 🆕 新增 | 统一入口，配置化管理 |
| `skills/conversation-to-knowledge/` | 本地 `knowledge-pipeline` | 新增 skill.yaml |
| `skills/subject-induction/` | 本地 `knowledge-pipeline` | 新增 skill.yaml |
| `skills/fable5-code-principle/` | 本地 `knowledge-pipeline` | 新增 skill.yaml |
| `skills/subject-color-tag/` | 本地 `knowledge-pipeline` | 新增 skill.yaml |
| `skills/obsidian-markdown/` | `kepano/obsidian-skills` | 保留原样 |
| `skills/json-canvas/` | `kepano/obsidian-skills` | 保留原样 |
| `skills/obsidian-bases/` | `kepano/obsidian-skills` | 保留原样 |
| `skills/obsidian-cli/` | `kepano/obsidian-skills` | 保留原样 |
| `skills/defuddle/` | `kepano/obsidian-skills` | 保留原样 |
| `skills/knowledge-refine/` | 🆕 新增 | Stage 2 Orchestrator |
| `skills/knowledge-publish/` | 🆕 新增 | Stage 3 发布 |

---

## 故障速查

| 现象 | 原因 | 解决 |
|------|------|------|
| `knowledge_refinery.py` 输出到错误路径 | 硬编码路径未 patch | 检查 `unified_entry.py` 是否正常 patch |
| Claude Code 找不到 skill | skills 未复制到正确目录 | 执行 `cp -r skills/* ~/.claude/skills/` |
| 生成的笔记 status 不是 inbox | legacy 脚本未写入 status | 正常现象，legacy 脚本不写入 status，由精修阶段补充 |
| Canvas 生成失败 | json-canvas skill 未安装 | 确认 `skills/json-canvas/` 存在 |
| 链接补全不准确 | Vault 中缺少目标笔记 | 先运行 `obsidian-cli` 检查断裂链接 |

---

## 下一步扩展

- [ ] 将 `unified_entry.py` 注册为 Windows 计划任务 / macOS LaunchAgent
- [ ] 添加 `deep_data.json` 的 Web UI 编辑器
- [ ] 扩展 `subject-induction` 支持自定义领域
- [ ] 为 `knowledge-publish` 添加邮件发送能力

---

*合并项目基于：*
- *本地 `knowledge-pipeline`（对话精炼引擎）*
- *`kepano/obsidian-skills`（通用 Obsidian 操作能力）*

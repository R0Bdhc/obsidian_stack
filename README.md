# Reasonix Knowledge System

> 基于 Claude Fable 5 提示词工程的知识库驱动 Skill 生成系统。
> 跨设备、一键部署、Obsidian 深度集成。

---

## 🎯 它能做什么

```
你的需求 → skill-generator 读取 Fable5 知识库 → 自动生成专业 Skill → 安装即用
```

1. **知识库存储** — Fable5 系统提示词被拆解为 10 大行为模块，结构化存储在 Obsidian Vault 中
2. **Skill 自动生成** — `/skill-generator` 读取知识库模板，根据任务自动组合模块生成专业 Skill
3. **跨设备复用** — `git clone` + `./setup.sh` 一键部署到任意 Mac

---

## 🚀 跨设备安装

```bash
# 1. 克隆
git clone <repo-url> && cd reasonix-knowledge-system

# 2. 一键安装
chmod +x setup.sh && ./setup.sh

# 3. 自定义 Vault 路径
./setup.sh --vault ~/Documents/MyVault --readonly
```

### setup.sh 做了什么

| 步骤 | 说明 |
|------|------|
| 检测系统 | 自动识别 x64/arm64 架构 |
| 下载 Node.js | v22.12.0，安装到 `nodejs/` (gitignore 已排除) |
| 安装 enquire-mcp | Obsidian MCP Server (40 工具，混合检索) |
| 同步知识库 | 将 Fable5 模板复制到 Obsidian Vault |
| 注册 MCP | 输出 Reasonix MCP 注册指令 |

---

## 📁 目录结构

```
├── README.md                     # 本文件
├── setup.sh                      # 跨设备一键安装脚本
├── reasonix.toml                 # Reasonix workspace 配置
├── .gitignore
├── AGENTS.md                     # AI Agent 操作指引
│
├── knowledge-base/               # 知识库（源文件）
│   ├── prompts/fable5/
│   │   ├── fable5-modules.md     # 10 大行为模块拆解
│   │   └── fable5-full-prompt.md # 完整系统提示词参考
│   ├── templates/
│   │   └── skill-template.md     # M1-M9 Skill 构造模板
│   ├── domain-knowledge/         # 专业知识积累
│   └── skills-output/            # 生成的 Skill 副本
│
└── skills/                       # Reasonix Skills
    ├── skill-generator/          # 知识库驱动 Skill 生成器
    └── meeting-notes-organizer/  # 会议笔记结构化工具
```

---

## 🔧 核心 Skills

### skill-generator

读取 Fable5 知识库，根据用户需求自动生成专业 Skill。

```
/skill-generator 我需要一个 Python 代码审查 Skill，要求检查类型注解和安全性
```

**工作流**: 分析需求 → 读取知识库 → 匹配 Fable5 模块 → 生成 Skill body → 安装 + 保存到 Obsidian

### meeting-notes-organizer

从会议对话中自动提取议题、决策、行动项、责任人、截止日期。

```
/meeting-notes-organizer [粘贴会议对话内容]
```

---

## 📊 Fable5 模块速查

| 模块 | 用途 | 何时选用 |
|------|------|----------|
| M1 身份声明 | 说明 Skill 身份和能力边界 | 所有 Skill |
| M2 核心能力 | 列出 Skill 能做什么 | 所有 Skill |
| M3 行为规范 | 语气、格式、纠错机制 | 所有 Skill |
| M4 安全边界 | 拒绝恶意代码/武器等 | 代码/安全类 |
| M5 搜索策略 | 联网搜索 + 不过度自信 | 研究分析类 |
| M6 公平性 | 多视角呈现 + 不站队 | 分析建议类 |
| M7 专业边界 | 不提供法律/金融建议 | 顾问类 |
| M8 用户福祉 | 不诊断、不鼓励自毁 | 健康/心理类 |
| M9 工具使用 | 多工具编排 | 工具集成类 |

---

## 🧩 技术栈

- **Reasonix** — AI Agent 框架
- **Obsidian** — 知识库存储
- **enquire-mcp** — Obsidian MCP Server (45 工具, 混合检索 BM25+ML+BGE)
- **Fable5** — Anthropic Claude 系统提示词工程模板

---

## ⚠️ 注意事项

- `setup.sh` 仅支持 macOS (x64/arm64)。Linux 需修改 Node.js 下载 URL
- Node.js 安装到 `nodejs/` (~690MB)，已在 `.gitignore` 排除，不会提交到 Git
- Vault 路径可在 `setup.sh --vault` 或 `reasonix.toml` 中自定义

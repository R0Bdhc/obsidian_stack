# Conversation to Knowledge Skill

将 Claude Code 的对话记录自动转化为结构化的 Obsidian 知识库。

## 触发条件

- 用户说"整理对话记录"、"生成知识库"、"把对话转成笔记"
- 用户需要项目文档化（技术栈、架构、时间线）
- 用户需要按学科归纳知识

## 核心能力

1. **对话解析**：读取 `~/.claude/projects/` 下的 `.jsonl` 对话文件
2. **项目笔记生成**：
   - 📋 项目总览（exec summary + stats）
   - 📈 更新进度（timeline of changes）
   - 🎯 改进方向（improvement roadmap）
   - 🔧 技术栈（tech stack analysis）
   - 🔄 能力流程（capability workflows）
   - 🏗️ 架构设计（architecture）
   - ⚙️ 配置管理（config management）
3. **知识域文章**：按五大领域（计算力学/软件工程/AI/工程自动化/知识管理）生成深度文章

## 用法

```bash
# 通过统一入口执行（推荐）
python pipeline/unified_entry.py --stage refinery

# 或执行 legacy 脚本
python pipeline/knowledge_refinery.py

# 预览模式
python pipeline/knowledge_refinery.py --dry-run
```

## 输出结构

```
D:\knowledgement/
├── 🏠 知识总览.md
├── Projects/
│   └── <project>/
│       ├── 📋 项目总览.md
│       ├── 📈 更新进度.md
│       ├── 🎯 改进方向.md
│       ├── 🔧 技术栈.md
│       ├── 🔄 能力流程.md
│       ├── 🏗️ 架构设计.md
│       ├── ⚙️ 配置管理.md
│       └── conversations/
├── Knowledge/
│   └── <domain>/
│       ├── 📋 索引.md
│       └── <topic>.md
└── Templates/
    ├── tpl-项目总览.md
    └── tpl-知识点.md
```

## 与统一工作流的关系

这是 **Stage 1: Refinery** 的核心 skill。
执行后笔记状态为 `inbox`，需通过 `knowledge-refine` skill 进一步精修。

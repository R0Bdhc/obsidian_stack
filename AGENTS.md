# AGENTS.md — AI Agent 操作指引

## 这是什么

Reasonix Knowledge System — 基于 Fable5 提示词工程的知识库驱动 Skill 生成系统。

## 你有哪些工具

### Obsidian MCP 工具 (mcp__obsidian__*)

连接到用户的 Obsidian Vault，提供 40 个工具：

| 类别 | 常用工具 |
|------|---------|
| 读取 | `obsidian_read_note`, `obsidian_list_notes`, `obsidian_search` |
| 写入 | `obsidian_create_note`, `obsidian_append_to_note`, `obsidian_rename_note` |
| 搜索 | `obsidian_search` (混合检索), `obsidian_search_by_tag` |
| 诊断 | `obsidian_stats`, `obsidian_get_backlinks`, `obsidian_lint_wiki` |

### 知识库内容

| 笔记 | 内容 |
|------|------|
| `提示词知识库/Fable5 系统提示词模块.md` | 10 大行为模块 (M1-M9) |
| `提示词知识库/Fable5 完整提示词参考.md` | 完整系统提示词 |
| `提示词知识库/Skill 构造模板.md` | M1-M9 模板详情 |

### Reasonix Skills

- `skill-generator` — 生成新的专业 Skill
- `meeting-notes-organizer` — 会议笔记结构化

## 何时使用 Obsidian

- 用户提到 "知识库"、"笔记"、"Obsidian"、"Fable5"
- 需要搜索历史记录、会议笔记、专业知识
- 生成 Skill 时需要参考 Fable5 模板
- 用户要求保存内容到 Obsidian

## 何时使用 workspace 文件

- 用户要求修改 Skill 本身 (`.reasonix/skills/`)
- 直接编辑 workspace 内文件时
- 使用 `write_file` 等传统工具

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

### GitHub MCP 工具 (mcp__github__*)

连接到 GitHub API，提供 26 个工具用于仓库操作：

| 类别 | 常用工具 | 用途 |
|------|---------|------|
| 读取 | `get_file_contents`, `list_commits`, `search_code` | 读仓库文件/提交历史/搜索代码 |
| 写入 | `create_or_update_file`, `push_files` | 单文件/批量 push |
| PR | `create_pull_request`, `merge_pull_request`, `get_pull_request_status` | PR 全流程 |
| Issue | `create_issue`, `list_issues`, `update_issue`, `add_issue_comment` | Issue 管理 |
| 分支 | `create_branch`, `update_pull_request_branch` | 分支操作 |
| 仓库 | `create_repository`, `fork_repository`, `search_repositories` | 仓库管理 |

**⚠️ 前提**: 需要设置环境变量 `GITHUB_PERSONAL_ACCESS_TOKEN`（GitHub Personal Access Token，需 `repo` 权限）。

### GitHub Desktop 联动

- 本 workspace 已关联远程仓库 `R0Bdhc/obsidian_stack`
- GitHub Desktop 安装在 `/Applications/GitHub Desktop.app`
- **工作流**: AI 通过 GitHub MCP 推送代码 → GitHub Desktop 可视化查看 diff/提交历史
- 用户提到 "推送"、"提交"、"PR"、"Pull Request" 时优先使用 `mcp__github__*` 工具

## 何时使用 GitHub MCP

- 用户要求 push/pull 代码、提交变更
- 需要创建 PR、Review、Merge
- 搜索 GitHub 上的代码或仓库
- 管理 Issue
- 读取远程仓库文件内容

# 项目颜色注册表

> 知识库内容按项目进行颜色分类，便于视觉区分和快速定位。
> 每个知识库条目应在其元数据中声明所属项目。

---

## 颜色规则

| 项目 | 颜色名 | 色值 | 徽标 | 说明 |
|------|--------|------|------|------|
| `cae-agent` | CAE 蓝 | `#2563EB` | 🔵 | CAE 仿真自动化核心项目 |
| `reasonix` | 知识绿 | `#16A34A` | 🟢 | 知识库驱动 Skill 生成系统 |
| `obsidian-stack` | 上游紫 | `#7C3AED` | 🟣 | obsidian_stack 原始上游项目 |
| `ansys-tools` | 工具橙 | `#EA580C` | 🟠 | ANSYS MAPDL/Mechanical 执行工具 |
| `fable5` | 模板灰 | `#6B7280` | ⚪ | Fable5 提示词工程模板（跨项目通用） |

---

## 项目详情

### 🔵 cae-agent
- **目录**: `.claude/skills/`（CAE 领域 Skills）
- **领域**: 工程仿真、ANSYS 自动化、CAE 辅助
- **MCP 工具**: ansys-local, deepseek, filesystem
- **关联模块**: M10（CAE 分析模块）

### 🟢 reasonix
- **目录**: `.reasonix/skills/`（通用/元 Skills）
- **领域**: 知识管理、Skill 生成、工作流自动化
- **MCP 工具**: deepseek, filesystem
- **关联模块**: M1-M9（Fable5 标准模块）

### 🟣 obsidian-stack
- **upstream**: https://github.com/R0Bdhc/obsidian_stack  <!-- 上游仓库唯一定义处；其他文件通过引用此处获取 URL -->
- **领域**: Obsidian 笔记 + Claude Code 集成
- **关联模块**: M1-M9（原始 Fable5 模块）

### 🟠 ansys-tools
- **目录**: `ansys_runner.py`, `mechanical_runner.py`
- **领域**: PyMAPDL 执行、PyMechanical 批量接触
- **MCP 工具**: ansys-local（MCP Server 本体）

### ⚪ fable5
- **目录**: `knowledge-base/prompts/fable5/`, `knowledge-base/templates/`
- **领域**: 提示词工程、Skill 构造模板
- **关联模块**: M1-M10（全部模块定义）

---

## 使用方式

### 在知识库条目中声明项目

在 Markdown 文件的 frontmatter 或开头添加：

```yaml
---
project: cae-agent
color: "#2563EB"
---
```

### 在 Skill frontmatter 中声明

```yaml
---
name: my-skill
description: 我的技能描述
project: cae-agent
color: "#2563EB"
---
```

### 颜色含义速记

```
🔵 蓝 = CAE 仿真分析
🟢 绿 = 知识/Skill 系统
🟣 紫 = 上游来源
🟠 橙 = ANSYS 执行工具
⚪ 灰 = 通用模板（横跨项目）
```

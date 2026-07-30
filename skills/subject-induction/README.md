# Subject Induction Skill

按学科领域对知识库进行结构化整理和深度归纳。

## 触发条件

- 用户说"按学科整理知识"、"建立学科索引"、"深化某一领域"
- 用户需要对已有知识库进行重新分类或补充新领域
- 用户需要生成学科总览或领域索引

## 核心能力

1. **领域识别**：根据关键词自动将对话和笔记归类到五大领域
2. **索引生成**：为每个领域生成结构化索引（📋 索引.md）
3. **知识文章**：为领域内的每个子主题生成深度文章
4. **交叉链接**：建立知识点与项目对话之间的双向链接

## 五大领域

| 领域 | 关键词示例 |
|------|-----------|
| 计算力学与有限元 | ansys, mapdl, pymapdl, 接触, 收敛, 应力, 模态, .inp |
| 软件工程与架构 | python, fastapi, 架构, 模块, 设计模式, pytest |
| 人工智能与LLM | llm, deepseek, prompt, model, api key, 回退 |
| 工程仿真自动化 | 日志, 报告, 批量, 自动化, 工作流, 解析, 检测 |
| 知识管理与工具链 | obsidian, 知识库, claude code, skill, MCP, git |

## 用法

```bash
# 通过统一入口执行
python pipeline/unified_entry.py --stage deepener

# 或执行 legacy 脚本
python pipeline/knowledge_deepener_v2.py
```

## 输入

- `pipeline/data/deep_data.json` — 五大领域的深度知识内容库
- `~/.claude/projects/` 下的 JSONL 对话文件

## 输出

```
D:\knowledgement/Knowledge/
├── 计算力学与有限元/
│   ├── 📋 索引.md
│   └── <topic>.md
├── 软件工程与架构/
│   ├── 📋 索引.md
│   └── <topic>.md
├── ...
```

## 颜色编码

与 `subject-color-tag` skill 配合使用，为每个领域分配视觉标识：

| 领域 | 颜色 | 图标 |
|------|------|------|
| 计算力学与有限元 | 🔴 红色系 | 🔴 |
| 软件工程与架构 | 🔵 蓝色系 | 🔵 |
| 人工智能与LLM | 🟣 紫色系 | 🟣 |
| 工程仿真自动化 | 🟢 绿色系 | 🟢 |
| 知识管理与工具链 | 🟡 黄色系 | 🟡 |

# Knowledge Publish Skill

知识发布与导出。统一工作流 Stage 3。

## 定位

```
Stage 1 (conversation-to-knowledge)
    ↓
Stage 2 (knowledge-refine)
    ↓
Stage 3 (knowledge-publish) ← 本 Skill
```

## 触发条件

- 用户需要分享项目文档给团队
- 用户需要将知识领域导出为手册/PDF
- 用户需要生成周报/月报
- 用户需要将笔记发布到博客或其他平台

## 核心能力

1. **项目导出**
   - 将 `Projects/<project>/` 下的所有笔记打包导出
   - 自动解析 `[[WikiLinks]]` 为相对路径或标题锚点
   - 包含/排除 conversations/ 原始对话（可选）

2. **领域手册**
   - 将 `Knowledge/<domain>/` 下的知识点合并为连贯手册
   - 自动按主题排序，插入章节导航
   - 输出为 PDF（需 Pandoc）或 HTML

3. **周刊/月报编译**
   - 按时间范围收集 `status: refined` 的笔记
   - 生成摘要和执行摘要
   - 输出为 Markdown 或邮件格式

4. **格式支持**

| 格式 | 用途 | 依赖 |
|------|------|------|
| `markdown-clean` | 通用 Markdown，适合博客/GitHub | 无 |
| `markdown-obsidian` | 保留 Obsidian 语法 | 无 |
| `html` | 静态网页 | 无 |
| `pdf` | 打印/归档 | Pandoc |
| `json` | API/数据交换 | 无 |

## 用法

```bash
cd D:/knowledgement
claude
```

```markdown
# 导出项目文档
请将 Projects/ansysagent/ 导出为 markdown-clean 格式，
保存到 Exports/ansysagent-docs/，
排除 conversations/ 目录。

# 生成领域手册
请将 Knowledge/计算力学与有限元/ 导出为 PDF，
按主题排序，添加页眉页脚，
保存到 Exports/FEA-Handbook.pdf。

# 编译周报
请编译本周（2026-07-15 至 2026-07-22）的所有 refined 笔记，
生成周报摘要，保存到 Exports/Weekly-2026-W29.md。
```

## 输出结构

```
Exports/
├── ansysagent-docs/           # 项目导出
│   ├── README.md
│   ├── 项目总览.md
│   └── ...
├── FEA-Handbook.pdf           # 领域手册
└── Weekly-2026-W29.md         # 周报
```

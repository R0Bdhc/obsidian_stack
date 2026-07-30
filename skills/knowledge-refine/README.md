# Knowledge Refine Skill (Orchestrator)

知识精修编排器。在自动化摄入生成基础笔记后，对 Vault 进行深度精修。

## 定位

**统一工作流 Stage 2**

```
Stage 1 (conversation-to-knowledge) ──→ Stage 2 (knowledge-refine) ──→ Stage 3 (knowledge-publish)
生成 inbox 笔记                          精修为 refined 笔记               导出/分享
```

## 触发条件

- 运行 `pipeline/unified_entry.py` 后自动触发（`--stage sync`）
- 用户在 Claude Code 中说"精修知识库"、"整理链接"、"生成 Canvas"
- 需要更新项目笔记的链接、补充 Canvas 或更新 Bases

## 编排关系

```
knowledge-refine (Orchestrator)
├── calls obsidian-markdown   ← 维基链接优化、Frontmatter 规范
├── calls json-canvas         ← 关系图、项目地图、知识网络
├── calls obsidian-bases      ← 数据库视图、项目追踪
├── calls subject-color-tag   ← 颜色标记（可选）
└── updates status: refined
```

## 核心能力

1. **链接补全**
   - 扫描 `[[...]]` 裸引用，自动创建或链接到已有笔记
   - 建立 Projects/ 与 Knowledge/ 之间的双向链接

2. **Canvas 生成**
   - 当项目对话 ≥5 篇时，生成 `Canvas/项目地图.canvas`
   - 当知识领域笔记 ≥5 篇时，生成 `Canvas/领域网络.canvas`

3. **Bases 更新**
   - 将项目元数据（状态、优先级、进度）同步到 `.base` 视图
   - 生成项目追踪仪表盘

4. **状态流转**
   - 批量更新 frontmatter: `status: inbox → processing → refined`
   - 为 refined 笔记添加 `refined_date` 和 `reviewed: true`

5. **MOC 维护**
   - 为每个领域生成/更新 Map of Content
   - 在 `🏠 知识总览.md` 中更新导航链接

## 用法

### 在 Claude Code 中手动触发

```bash
cd D:/knowledgement
claude
```

```markdown
# 批量精修整个 Vault
请对当前 Vault 执行 knowledge-refine：
1. 检查所有 status: inbox 的笔记
2. 补全缺失的 [[WikiLinks]]
3. 为项目 ansysagent 生成 Canvas 关系图
4. 更新 Knowledge/ 下所有领域的 MOC
5. 将处理过的笔记状态改为 refined

# 精修单个项目
请精修 Projects/ansysagent/：
- 检查 6 篇分析笔记之间的链接完整性
- 在 🔧 技术栈 中补充缺失的模块链接
- 生成项目架构 Canvas

# 精修单个领域
请精修 Knowledge/计算力学与有限元/：
- 更新 📋 索引.md
- 确保所有知识点之间有交叉链接
- 生成领域知识网络 Canvas
```

### 通过统一入口自动触发

```bash
python pipeline/unified_entry.py --stage sync
```

这会打印一组推荐的 Claude Code 精修指令，供用户复制执行。

## 输出示例

精修后的笔记 frontmatter：

```yaml
---
project: "ansysagent"
type: project-overview
status: refined          # ← 从 inbox 更新
refined_date: 2026-07-22
reviewed: true
tags:
  - project
  - moc
  - overview
links_checked: true      # ← 新增
canvas: "Canvas/ansysagent-项目地图.canvas"  # ← 新增
---
```

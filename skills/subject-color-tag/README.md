# Subject Color Tag Skill

为知识库学科分类添加颜色标记，增强可视化导航。

## 触发条件

- 用户说"给知识库分类上色"、"学科颜色分类"
- 用户需要建立 Obsidian 颜色编码体系
- 用户需要美化或重新设计知识库视觉风格

## 设计理念

| 领域 | 建议颜色 | 理由 |
|------|---------|------|
| 计算力学与有限元 | 🔴 红色系 | 工程、强度、热力 |
| 软件工程与架构 | 🔵 蓝色系 | 逻辑、代码、架构图 |
| 人工智能与LLM | 🟣 紫色系 | 智能、未来、创意 |
| 工程仿真自动化 | 🟢 绿色系 | 自动化、运行、通过 |
| 知识管理与工具链 | 🟡 黄色系 | 笔记、高亮、提醒 |

## 实现方式

### Obsidian 标签颜色

在 `.obsidian/snippets/subject-colors.css` 中配置：

```css
/* 计算力学与有限元 */
.tag[href="#计算力学与有限元"],
.tag[href="#FEA"] {
  background-color: #e63946;
  color: white;
}

/* 软件工程与架构 */
.tag[href="#软件工程"],
.tag[href="#架构"] {
  background-color: #457b9d;
  color: white;
}

/* 人工智能与LLM */
.tag[href="#AI"],
.tag[href="#LLM"] {
  background-color: #9b5de5;
  color: white;
}

/* 工程仿真自动化 */
.tag[href="#自动化"],
.tag[href="#仿真"] {
  background-color: #2a9d8f;
  color: white;
}

/* 知识管理与工具链 */
.tag[href="#知识管理"],
.tag[href="#Obsidian"] {
  background-color: #e9c46a;
  color: #1a1a1a;
}
```

### 文件夹颜色（Folder Notes 插件）

为每个 Knowledge/ 子目录添加封面色块：

```markdown
---
color: "#e63946"
---

# 计算力学与有限元
```

## 与 subject-induction 联动

当 `subject-induction` 识别出新领域时，自动调用本 skill 为新领域分配颜色。

## 用法

```bash
# 生成完整颜色主题
# 在 Claude Code 中执行
请为 Knowledge/ 下的五大领域生成颜色主题 CSS，
保存到 .obsidian/snippets/subject-colors.css
```

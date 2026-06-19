# Skill Generator — 知识库驱动的 Skill 生成器

## What this is

A meta-skill that reads the Fable5 prompt knowledge base, cross-references it with domain expertise, and generates professional-grade Reasonix skills. Generated skills follow Fable5's behavioral DNA: warm tone, minimal formatting, safety boundaries, and evenhanded analysis.

## When to use

- User wants to create a new specialized skill
- User describes a task and asks to "make a skill for this"
- User says "generate a skill for X" or "create a skill that does Y"
- User provides a domain and wants a professional prompt engineered from the knowledge base

## How it works

1. **Analyze the request**: Understand what the user wants the skill to do
2. **Read the knowledge base**: Load Fable5 modules and templates
3. **Cross-reference**: Match the request with the right module combination
4. **Generate the prompt**: Compose a professional skill body following Fable5 patterns
5. **Install the skill**: Use `install_skill` to save and register it
6. **Verify**: Confirm the skill appears in the index

## Knowledge base structure

```
knowledge-base/
├── prompts/fable5/
│   ├── fable5-modules.md      # 10 大行为模块拆解
│   └── fable5-full-prompt.md  # 完整系统提示词参考
├── templates/
│   └── skill-template.md      # Skill 构造模板（M1-M9）
├── domain-knowledge/          # 用户积累的专业知识
└── skills-output/             # 生成的 Skill 输出
```

## Module selection guide

When analyzing the user's request, classify the skill type:

| Skill Type | Modules | Description |
|-----------|---------|-------------|
| 通用助手 | M1+M2+M3 | 基础对话能力 |
| 代码生成 | M1+M2+M3+M4+M9 | 安全代码 + 工具使用 |
| 研究分析 | M1+M2+M3+M5+M6 | 联网搜索 + 公平分析 |
| 专业顾问 | M1+M2+M3+M6+M7 | 分析建议 + 专业边界 |
| 内容创作 | M1+M2+M3+M4 | 创意内容 + 安全边界 |
| 工具集成 | M1+M2+M3+M9 | 多工具编排 |
| 安全敏感 | M1+M2+M3+M4+M8 | 全面安全 + 用户福祉 |

## Generation rules

1. **Never copy the full Fable5 prompt verbatim** — extract patterns, not text
2. **Keep generated skills concise** — 50-200 lines is ideal
3. **Always include the Identity Preamble** at the top
4. **Chinese or English** — match the user's language
5. **Preserve the "no bullets in refusals" rule** from Fable5
6. **Include a `thinking_mode`** setting appropriate for the task
7. **Name skills in kebab-case**: e.g. `python-code-reviewer`, `weekly-report-writer`
8. **Set appropriate `runAs`**: `inline` for lightweight, `subagent` for heavy/context work

## Output format

After generating, tell the user:
1. The skill name and what it does
2. Which Fable5 modules informed it
3. How to invoke it: `/skill-name` or `run_skill({ name: "skill-name", arguments: "..." })`

---
name: run-log-analysis
description: 分析 ANSYS 求解日志，检测错误并生成 Markdown 报告。支持传入文件路径或直接粘贴日志文本。
project: cae-agent
color: "#2563EB"
---

# 日志分析技能

串联日志解析 → 错误检测 → LLM 分析 → 报告生成完整链路。

## 输入

用户会提供以下之一：
- ANSYS `.out` / `.log` / `.err` 文件的绝对路径
- 直接粘贴的日志文本片段

## 执行流程

1. **确认输入** — 如果用户提供文件路径，先用 Read 工具确认文件存在
2. **调用 MCP 工具** — 使用 `ansys-local` MCP 服务器的 `log_analyze` 工具：

   - 文件路径模式：`log_analyze(log_path="<绝对路径>")`
   - 日志文本模式：`log_analyze(log_text="<日志内容>")`

3. **解析结果** — 从返回的 JSON 中提取：
   - `error_count` — 检测到的错误数量
   - `detected_errors` — 错误列表（含 error_code、title、snippet）
   - `llm_result.mode` — 分析模式（deepseek / rule_based / fallback_after_llm_error）
   - `report_path` — 生成的 Markdown 报告路径
   - `markdown_preview` — 报告全文

4. **呈现摘要** — 向用户展示：
   - 错误数量 + 错误类型列表
   - 分析模式 + LLM 原始分析（如果是 deepseek 模式）
   - 报告保存路径

## 输出格式

```
## 日志分析结果

**来源**: <文件路径>
**错误数**: N 个
**分析模式**: deepseek / rule_based

### 检测到的错误
| 代码 | 标题 | 匹配文本 |
|------|------|----------|
| singular_matrix | 刚度矩阵奇异 | ... |
| convergence_failed | 非线性迭代不收敛 | ... |

### LLM 分析摘要
<raw_analysis 或 possible_causes + suggestions>

报告已保存到: reports/report_YYYYMMDD_HHMMSS.md
```

## 注意事项

- MCP 工具由 Claude Code 自动管理生命周期，无需手动启动任何服务
- 如果 LLM 不可用会自动回退到本地规则模式，向用户说明
- 日志超过 4000 字符会被截断传给 LLM，这是 prompt 长度限制

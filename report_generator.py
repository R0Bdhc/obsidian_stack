from datetime import datetime
from pathlib import Path


def build_markdown_report(
    source_name: str,
    detected_errors: list[dict],
    llm_result: dict,
    engineering_results: dict | None = None,
) -> str:
    """构造 Markdown 报告内容。"""
    lines: list[str] = []

    lines.append("# CAE 日志分析报告")
    lines.append("")
    lines.append(f"- 日志来源：`{source_name}`")
    lines.append(f"- 生成时间：`{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
    lines.append(f"- 检测到错误数量：`{len(detected_errors)}`")
    lines.append("")

    # ── 求解结果数据（优先展示，因与求解质量直接相关） ──
    if engineering_results:
        lines.append("## 1. 求解结果数据")
        lines.append("")
        _render_engineering_results(lines, engineering_results)

    section = 2
    error_section = section
    section += 1
    llm_section = section

    lines.append(f"## {error_section}. 错误检测结果")
    lines.append("")

    if not detected_errors:
        lines.append("未检测到预设错误关键词。")
        lines.append("")
    else:
        for index, item in enumerate(detected_errors, start=1):
            lines.append(f"### {error_section}.{index} {item['title']}")
            lines.append("")
            lines.append(f"- 错误代码：`{item['error_code']}`")
            lines.append(f"- 匹配文本：`{item['matched_text']}`")
            lines.append(f"- 错误说明：{item['description']}")
            lines.append("")
            lines.append("```text")
            lines.append(item["snippet"])
            lines.append("```")
            lines.append("")

    lines.append(f"## {llm_section}. LLM / 规则分析结果")
    lines.append("")
    lines.append(f"- 分析模式：`{llm_result.get('mode', 'unknown')}`")
    lines.append(f"- 分析摘要：{llm_result.get('summary', '无')}")
    lines.append("")

    raw_analysis = llm_result.get("raw_analysis")
    if raw_analysis:
        lines.append(f"### {llm_section}.1 DeepSeek 原始分析")
        lines.append("")
        lines.append(raw_analysis)
        lines.append("")

    possible_causes = llm_result.get("possible_causes", [])
    if possible_causes:
        lines.append(f"### {llm_section}.2 可能原因")
        lines.append("")
        for item in possible_causes:
            lines.append(f"- {item}")
        lines.append("")

    suggestions = llm_result.get("suggestions", [])
    if suggestions:
        lines.append(f"### {llm_section}.3 修改建议")
        lines.append("")
        for item in suggestions:
            lines.append(f"- {item}")
        lines.append("")

    llm_error = llm_result.get("llm_error")
    if llm_error:
        lines.append(f"### {llm_section}.4 LLM 调用异常")
        lines.append("")
        lines.append(f"`{llm_error}`")
        lines.append("")

    return "\n".join(lines)


def _render_engineering_results(lines: list[str], results: dict) -> None:
    """在 Markdown 行列表中渲染工程结果数据段。"""
    extraction_error = results.get("extraction_error")
    if extraction_error:
        lines.append(f"> 结果提取异常：{extraction_error}")
        lines.append("")
        return

    displacement = results.get("displacement")
    if displacement:
        lines.append("### 1.1 位移")
        lines.append("")
        lines.append("| 指标 | 最大值 |")
        lines.append("|------|--------|")
        for key in ("max_usum", "max_ux", "max_uy", "max_uz"):
            value = displacement.get(key)
            if value is not None:
                label = displacement.get(f"label_{key[4:]}", key)
                lines.append(f"| {label} | {value:.6e} |")
        lines.append("")

    stress = results.get("stress")
    if stress:
        lines.append("### 1.2 应力")
        lines.append("")
        lines.append("| 指标 | 最大值 |")
        lines.append("|------|--------|")
        for key in ("max_von_mises", "max_s1", "max_s3", "max_sx"):
            value = stress.get(key)
            if value is not None:
                label = stress.get(f"label_{key[4:]}", key)
                lines.append(f"| {label} | {value:.6e} |")
        lines.append("")

    reaction = results.get("reaction_forces")
    if reaction:
        lines.append("### 1.3 支反力合力")
        lines.append("")
        lines.append("| 方向 | 合力 |")
        lines.append("|------|------|")
        for axis in ("fx", "fy", "fz"):
            value = reaction.get(axis)
            if value is not None:
                lines.append(f"| {axis.upper()} | {value:.6e} |")
        lines.append("")

    frequency = results.get("frequency")
    if frequency:
        modes = frequency.get("modes", [])
        if modes:
            lines.append("### 1.4 模态频率")
            lines.append("")
            lines.append("| 阶数 | 频率 (Hz) |")
            lines.append("|------|-----------|")
            for mode in modes:
                lines.append(f"| {mode['order']} | {mode['frequency_hz']:.4f} |")
            lines.append("")


def save_markdown_report(markdown_content: str, output_dir: str | Path = "reports") -> Path:
    """把 Markdown 报告保存到本地文件。"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file = output_path / filename
    report_file.write_text(markdown_content, encoding="utf-8")

    return report_file

"""ANSYS MCP Server — 封装 PyMAPDL 和 PyMechanical 为 MCP 工具。

启动方式:
  python server.py

或在 .mcp.json 中由 Claude Code 自动启动。

依赖:
  pip install mcp ansys-mapdl-core
"""

import json
import os
import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv()

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from log_parser import detect_errors, load_log_text
from llm_analyzer import LLMAnalyzer
from report_generator import build_markdown_report, save_markdown_report

_llm_analyzer: LLMAnalyzer | None = None


def _get_llm_analyzer() -> LLMAnalyzer:
    global _llm_analyzer
    if _llm_analyzer is None:
        _llm_analyzer = LLMAnalyzer()
    return _llm_analyzer


server = Server("ansys-mcp")


def _get_ansys_runner():
    """延迟导入，避免启动时因缺失 ANSYS 而崩溃。"""
    from ansys_runner import AnsysRunner
    return AnsysRunner()


def _get_mechanical_runner():
    from mechanical_runner import MechanicalRunner
    return MechanicalRunner()


@server.tool()
async def mapdl_status() -> str:
    """查询 PyMAPDL 环境状态：是否可导入、MAPDL.exe 位置、支持的文件格式。"""
    try:
        runner = _get_ansys_runner()
        status = runner.get_environment_status()
        return json.dumps(status, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({
            "error": str(exc),
            "message": "PyMAPDL 环境查询失败，可能未安装 ansys-mapdl-core 或 ANSYS 未安装。"
        }, ensure_ascii=False, indent=2)


@server.tool()
async def mapdl_execute(input_file_path: str, working_directory: str = "") -> str:
    """执行 MAPDL 输入文件（.inp / .dat / .mac）。

    Args:
        input_file_path: 输入文件的绝对路径
        working_directory: MAPDL 工作目录，为空则使用默认 ansys_workspace
    """
    try:
        runner = _get_ansys_runner()
        result = runner.run_input_file(
            input_file_path=input_file_path,
            working_directory=working_directory or None,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({
            "success": False,
            "message": f"MAPDL 执行失败: {exc}",
            "input_file_path": input_file_path,
        }, ensure_ascii=False, indent=2)


@server.tool()
async def mapdl_demo(launch: bool = False) -> str:
    """返回或执行最小 ANSYS 示例（LINK180 拉杆静力分析）。

    Args:
        launch: 是否真实启动 MAPDL。False 时仅返回 APDL 命令。
    """
    try:
        runner = _get_ansys_runner()
        if launch:
            result = runner.run_demo(launch_mapdl=True)
        else:
            result = runner.get_demo_definition()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({
            "success": False,
            "message": f"MAPDL 示例执行失败: {exc}",
        }, ensure_ascii=False, indent=2)


@server.tool()
async def mechanical_status() -> str:
    """查询 PyMechanical 环境状态：可导入性、Mechanical 版本、支持的批量接触能力。"""
    try:
        runner = _get_mechanical_runner()
        status = runner.get_environment_status()
        return json.dumps(status, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({
            "error": str(exc),
            "message": "PyMechanical 环境查询失败，可能未安装 ansys-mechanical-core。"
        }, ensure_ascii=False, indent=2)


@server.tool()
async def mechanical_batch_contact(
    source_prefix: str,
    target_prefix: str,
    contact_type: str = "Frictionless",
    contact_name_prefix: str = "AUTO_CONTACT_",
    launch: bool = False,
) -> str:
    """按 Named Selection 前缀批量创建接触对（需 242+ Mechanical）。

    Args:
        source_prefix: 源面 Named Selection 前缀，如 NS_SRC_
        target_prefix: 目标面 Named Selection 前缀，如 NS_TGT_
        contact_type: 接触类型 (Bonded/Frictional/Frictionless/NoSeparation/Rough)
        contact_name_prefix: 生成的接触名称前缀
        launch: 是否真实启动 Mechanical 执行
    """
    try:
        runner = _get_mechanical_runner()
        if launch:
            result = runner.execute_batch_contacts_by_named_selection(
                source_named_selection_prefix=source_prefix,
                target_named_selection_prefix=target_prefix,
                contact_type=contact_type,
                contact_name_prefix=contact_name_prefix,
                launch_mechanical=True,
            )
        else:
            result = runner.preview_batch_contact_plan(
                source_named_selection_prefix=source_prefix,
                target_named_selection_prefix=target_prefix,
                contact_type=contact_type,
                contact_name_prefix=contact_name_prefix,
            )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({
            "success": False,
            "message": f"批量接触执行失败: {exc}",
        }, ensure_ascii=False, indent=2)


@server.tool()
async def log_analyze(log_path: str = "", log_text: str = "") -> str:
    """分析 ANSYS 求解日志，检测错误并生成 Markdown 报告。log_path 和 log_text 至少提供一个。

    Args:
        log_path: 日志文件绝对路径（.out / .log / .err）
        log_text: 直接传入的日志文本内容
    """
    try:
        if log_path:
            log_file = Path(log_path)
            if not log_file.exists():
                return json.dumps({
                    "success": False,
                    "message": f"日志文件不存在：{log_path}",
                }, ensure_ascii=False, indent=2)
            content = load_log_text(log_file)
            source_name = str(log_file)
        elif log_text:
            content = log_text
            source_name = "direct_input.log"
        else:
            return json.dumps({
                "success": False,
                "message": "请提供 log_path 或 log_text。",
            }, ensure_ascii=False, indent=2)

        detected_errors = detect_errors(content)
        analyzer = _get_llm_analyzer()
        llm_result = analyzer.analyze(
            source_name=source_name,
            log_text=content,
            detected_errors=detected_errors,
        )
        markdown_content = build_markdown_report(
            source_name=source_name,
            detected_errors=detected_errors,
            llm_result=llm_result,
        )
        report_path = save_markdown_report(markdown_content)

        return json.dumps({
            "success": True,
            "source_name": source_name,
            "error_count": len(detected_errors),
            "detected_errors": detected_errors,
            "llm_result": llm_result,
            "report_path": str(report_path),
            "markdown_preview": markdown_content,
        }, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({
            "success": False,
            "message": f"日志分析失败: {exc}",
        }, ensure_ascii=False, indent=2)


@server.tool()
async def health_check() -> str:
    """检查 LLM 连通性和整体服务状态。"""
    try:
        analyzer = _get_llm_analyzer()
        status = analyzer.get_status()
        return json.dumps({
            "status": "ok",
            "llm": status,
        }, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({
            "status": "error",
            "message": f"健康检查失败: {exc}",
        }, ensure_ascii=False, indent=2)


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="mapdl_status",
            description="查询 PyMAPDL 环境状态：是否可导入、MAPDL.exe 位置、支持的输入格式",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="mapdl_execute",
            description="执行 MAPDL 输入文件（.inp/.dat/.mac）并返回求解结果和日志路径",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file_path": {"type": "string", "description": "输入文件绝对路径"},
                    "working_directory": {"type": "string", "description": "工作目录，默认为 ansys_workspace"},
                },
                "required": ["input_file_path"],
            },
        ),
        Tool(
            name="mapdl_demo",
            description="返回或执行最小 ANSYS 示例（LINK180 拉杆静力分析）",
            inputSchema={
                "type": "object",
                "properties": {
                    "launch": {"type": "boolean", "description": "是否真实启动 MAPDL", "default": False},
                },
            },
        ),
        Tool(
            name="mechanical_status",
            description="查询 PyMechanical 环境状态：可导入性和版本检测",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="mechanical_batch_contact",
            description="按 Named Selection 前缀批量创建 Mechanical 接触对",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_prefix": {"type": "string", "description": "源面前缀，如 NS_SRC_"},
                    "target_prefix": {"type": "string", "description": "目标面前缀，如 NS_TGT_"},
                    "contact_type": {"type": "string", "description": "接触类型", "default": "Frictionless"},
                    "contact_name_prefix": {"type": "string", "description": "接触名称前缀", "default": "AUTO_CONTACT_"},
                    "launch": {"type": "boolean", "description": "是否真实启动 Mechanical", "default": False},
                },
                "required": ["source_prefix", "target_prefix"],
            },
        ),
        Tool(
            name="log_analyze",
            description="分析 ANSYS 求解日志，检测错误并调用 LLM 诊断，生成 Markdown 报告",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_path": {"type": "string", "description": "日志文件绝对路径", "default": ""},
                    "log_text": {"type": "string", "description": "直接传入的日志文本", "default": ""},
                },
            },
        ),
        Tool(
            name="health_check",
            description="检查 LLM 连通性和 DeepSeek API 可用性",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

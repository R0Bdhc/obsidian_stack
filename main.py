from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ansys_runner import AnsysRunner
from llm_analyzer import LLMAnalyzer
from log_parser import detect_errors, load_log_text
from mechanical_runner import MechanicalRunner
from report_generator import build_markdown_report, save_markdown_report


load_dotenv()

app = FastAPI(
    title="cae-agent",
    description="基于 ANSYS 与 LLM 的最小可运行 CAE 辅助系统。",
    version="0.1.0",
)


class AnalyzeLogRequest(BaseModel):
    log_path: Optional[str] = Field(default=None, description="日志文件绝对路径。")
    log_text: Optional[str] = Field(default=None, description="直接传入的日志文本。")


class AnsysDemoRequest(BaseModel):
    launch_mapdl: bool = Field(
        default=False,
        description="是否真实启动 MAPDL。False 时仅返回演示命令。",
    )
    working_directory: Optional[str] = Field(
        default=None,
        description="MAPDL 工作目录。为空时默认使用项目内的 ansys_workspace。",
    )


class MapdlInputRequest(BaseModel):
    input_file_path: str = Field(description="MAPDL 输入文件绝对路径，例如 .inp、.dat、.mac。")
    working_directory: Optional[str] = Field(
        default=None,
        description="MAPDL 工作目录。为空时默认使用项目内的 ansys_workspace。",
    )
    analyze_after_run: bool = Field(
        default=True,
        description="执行完成后是否自动分析主日志文件。",
    )


class MechanicalBatchContactRequest(BaseModel):
    source_named_selection_prefix: str = Field(description="源面命名选择前缀，例如 NS_SRC_")
    target_named_selection_prefix: str = Field(description="目标面命名选择前缀，例如 NS_TGT_")
    contact_type: str = Field(default="Frictionless", description="接触类型，例如 Frictionless/Bonded")
    contact_name_prefix: str = Field(default="AUTO_CONTACT_", description="自动创建接触名称前缀")
    launch_mechanical: bool = Field(
        default=False,
        description="是否真实启动 242+ Mechanical 执行。False 时仅返回方案和脚本预览。",
    )
    working_directory: Optional[str] = Field(
        default=None,
        description="Mechanical 工作目录。为空时默认使用项目内的 mechanical_workspace。",
    )


llm_analyzer = LLMAnalyzer()
ansys_runner = AnsysRunner()
mechanical_runner = MechanicalRunner()


@app.get("/")
def root() -> dict:
    return {
        "project": "cae-agent",
        "message": "服务已启动，可访问 /docs 查看接口文档。",
        "stage": "可执行 MVP：MAPDL 执行 + 日志分析 + 报告生成",
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "llm": llm_analyzer.get_status(),
        "notes": {
            "configured": "是否已配置可用的 LLM API Key。",
            "reachable": "是否能从当前环境成功连通外部 LLM 服务。",
            "checked_at": "最近一次连通性检查的 Unix 时间戳；未检查时为 null。",
        },
    }


@app.get("/mapdl-status")
def mapdl_status() -> dict:
    return ansys_runner.get_environment_status()


@app.get("/ansys-demo")
def get_ansys_demo() -> dict:
    return ansys_runner.get_demo_definition()


@app.get("/mechanical-status")
def mechanical_status() -> dict:
    return mechanical_runner.get_environment_status()


@app.get("/mechanical-capabilities")
def mechanical_capabilities() -> dict:
    return mechanical_runner.get_capability_definition()


@app.post("/mechanical-contact-batch-plan")
def mechanical_contact_batch_plan(request: MechanicalBatchContactRequest) -> dict:
    return mechanical_runner.preview_batch_contact_plan(
        source_named_selection_prefix=request.source_named_selection_prefix,
        target_named_selection_prefix=request.target_named_selection_prefix,
        contact_type=request.contact_type,
        contact_name_prefix=request.contact_name_prefix,
    )


@app.post("/mechanical-contact-batch-execute")
def mechanical_contact_batch_execute(request: MechanicalBatchContactRequest) -> dict:
    return mechanical_runner.execute_batch_contacts_by_named_selection(
        source_named_selection_prefix=request.source_named_selection_prefix,
        target_named_selection_prefix=request.target_named_selection_prefix,
        contact_type=request.contact_type,
        contact_name_prefix=request.contact_name_prefix,
        launch_mechanical=request.launch_mechanical,
        working_directory=request.working_directory,
    )


@app.post("/run-ansys-demo")
def run_ansys_demo(request: AnsysDemoRequest) -> dict:
    return ansys_runner.run_demo(
        launch_mapdl=request.launch_mapdl,
        working_directory=request.working_directory,
    )


@app.post("/run-mapdl-input")
def run_mapdl_input(request: MapdlInputRequest) -> dict:
    result = ansys_runner.run_input_file(
        input_file_path=request.input_file_path,
        working_directory=request.working_directory,
    )

    if not result.get("success"):
        return result

    if not request.analyze_after_run:
        return result

    primary_log_path = result.get("primary_log_path")
    if not primary_log_path:
        result["analysis"] = {
            "success": False,
            "message": "执行已完成，但未找到可分析的主日志文件。",
        }
        return result

    log_text = load_log_text(primary_log_path)
    detected_errors = detect_errors(log_text)
    llm_result = llm_analyzer.analyze(
        source_name=primary_log_path,
        log_text=log_text,
        detected_errors=detected_errors,
    )
    markdown_content = build_markdown_report(
        source_name=primary_log_path,
        detected_errors=detected_errors,
        llm_result=llm_result,
        engineering_results=result.get("engineering_results"),
    )
    report_path = save_markdown_report(markdown_content)

    result["analysis"] = {
        "success": True,
        "primary_log_path": primary_log_path,
        "error_count": len(detected_errors),
        "detected_errors": detected_errors,
        "llm_result": llm_result,
        "report_path": str(report_path),
        "markdown_preview": markdown_content,
    }
    return result


@app.post("/analyze-log")
def analyze_log(request: AnalyzeLogRequest) -> dict:
    if not request.log_path and not request.log_text:
        raise HTTPException(status_code=400, detail="请提供 log_path 或 log_text。")

    if request.log_path:
        log_file = Path(request.log_path)
        if not log_file.exists():
            raise HTTPException(status_code=400, detail=f"日志文件不存在：{log_file}")
        log_text = load_log_text(log_file)
        source_name = str(log_file)
    else:
        log_text = request.log_text or ""
        source_name = "direct_input.log"

    detected_errors = detect_errors(log_text)
    llm_result = llm_analyzer.analyze(
        source_name=source_name,
        log_text=log_text,
        detected_errors=detected_errors,
    )
    markdown_content = build_markdown_report(
        source_name=source_name,
        detected_errors=detected_errors,
        llm_result=llm_result,
    )
    report_path = save_markdown_report(markdown_content)

    return {
        "success": True,
        "source_name": source_name,
        "error_count": len(detected_errors),
        "detected_errors": detected_errors,
        "llm_result": llm_result,
        "report_path": str(report_path),
        "markdown_preview": markdown_content,
    }

#!/usr/bin/env python3
"""
Claude Code 知识精炼器 — 将对话记录拆解细化为结构化知识库。

输出结构:
  idea/
  ├── 🏠 知识总览.md
  ├── Projects/<name>/
  │   ├── 📋 项目总览.md      (exec summary + stats)
  │   ├── 📈 更新进度.md       (timeline of changes)
  │   ├── 🎯 改进方向.md       (improvement roadmap)
  │   ├── 🔧 技术栈.md         (tech stack analysis)
  │   ├── 🔄 能力流程.md       (capability workflows)
  │   ├── 🏗️ 架构设计.md        (architecture)
  │   ├── ⚙️ 配置管理.md        (config management)
  │   └── conversations/       (raw conversation notes)
  ├── Knowledge/<domain>/
  │   ├── 📋 索引.md
  │   └── <topic>.md           (knowledge articles)
  └── Templates/
      ├── tpl-项目总览.md
      └── tpl-知识点.md

用法:
    python knowledge_refinery.py           # 精炼所有对话
    python knowledge_refinery.py --dry-run  # 预览模式
"""

import json
import os
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional
import argparse

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

CLAUDE_HOME = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_HOME / "projects"
IDEA_ROOT = Path("D:/knowledgement")

CST = timezone(timedelta(hours=8))

# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class Conversation:
    session_id: str
    project_name: str
    title: str
    timestamp: str
    user_messages: list[str] = field(default_factory=list)
    assistant_texts: list[str] = field(default_factory=list)
    tool_names: set[str] = field(default_factory=set)
    files_touched: set[str] = field(default_factory=set)
    total_events: int = 0

    @property
    def date_str(self) -> str:
        try:
            return datetime.fromisoformat(self.timestamp).strftime("%Y-%m-%d")
        except Exception:
            return self.timestamp[:10]


# ---------------------------------------------------------------------------
# 知识领域定义 (现实世界专业方向)
# ---------------------------------------------------------------------------

DOMAINS = {
    "计算力学与有限元": {
        "desc": "计算力学、有限元分析(FEA)、ANSYS仿真相关的理论、方法和实践经验",
        "keywords": [
            "ansys", "mapdl", "pymapdl", "mechanical", "pymechanical",
            "接触", "contact", "收敛", "convergence", "求解器", "solver",
            "应力", "形变", "频率", "模态", "刚度矩阵", "singular",
            ".inp", ".dat", ".mac", "input file", "边界条件",
            "非线性", "nonlinear", "材料", "material", "网格", "mesh",
        ],
        "topics": {
            "ANSYS-MAPDL-应用": {
                "desc": "ANSYS MAPDL 求解器的使用、配置和最佳实践",
                "content": None,  # generated from transcripts
            },
            "PyMAPDL-集成": {
                "desc": "Python 通过 PyMAPDL 驱动 ANSYS 求解器的集成方案",
                "content": None,
            },
            "接触分析": {
                "desc": "Mechanical 批量接触对的创建、管理和调试",
                "content": None,
            },
            "求解器收敛与诊断": {
                "desc": "求解器不收敛、奇异矩阵等常见问题的诊断和处理",
                "content": None,
            },
        },
    },
    "软件工程与架构": {
        "desc": "软件设计模式、系统架构、Python开发、API设计等工程实践",
        "keywords": [
            "python", "fastapi", "uvicorn", "REST", "API",
            "架构", "architecture", "模块", "module", "职责",
            "pip", "venv", "pytest", "import",
            "设计模式", "解耦", "分层", "layered",
        ],
        "topics": {
            "FastAPI-服务设计": {
                "desc": "基于 FastAPI 的 REST API 服务架构设计",
                "content": None,
            },
            "模块化架构模式": {
                "desc": "模块职责分离、两阶段设计、回退模式等架构决策",
                "content": None,
            },
            "Python-项目配置": {
                "desc": "Python 项目的依赖管理、环境变量、编码处理",
                "content": None,
            },
            "错误处理与回退": {
                "desc": "多层错误检测、LLM回退、正则匹配的工程实践",
                "content": None,
            },
        },
    },
    "人工智能与LLM": {
        "desc": "大语言模型(LLM)的集成、Prompt工程、API调用和模型管理",
        "keywords": [
            "llm", "deepseek", "大模型", "prompt", "analyzer",
            "模型", "model", "api key", "token",
            "回退", "fallback", "规则", "rule",
        ],
        "topics": {
            "LLM-集成模式": {
                "desc": "将 LLM 集成到工程工具中的架构模式：API 封装、回退、缓存",
                "content": None,
            },
            "DeepSeek-API-应用": {
                "desc": "DeepSeek V4 系列模型的 API 调用、配置和最佳实践",
                "content": None,
            },
            "Prompt-工程设计": {
                "desc": "面向 CAE 场景的 Prompt 设计：错误分析、报告生成、日志理解",
                "content": None,
            },
            "模型选择与回退策略": {
                "desc": "多模型分层：主力模型 vs 回退规则，成本与效果的平衡",
                "content": None,
            },
        },
    },
    "工程仿真自动化": {
        "desc": "CAE工作流的自动化：日志分析、报告生成、批量处理和求解器编排",
        "keywords": [
            "日志", "log", "报告", "report", "批量", "batch",
            "自动化", "automation", "工作流", "workflow",
            "解析", "parse", "检测", "detect", "输出", "output",
            "求解", "solve", "运行", "run",
        ],
        "topics": {
            "日志解析与错误检测": {
                "desc": "ANSYS 求解日志的正则解析、错误模式识别和多级检测",
                "content": None,
            },
            "报告生成系统": {
                "desc": "Markdown 报告自动生成：模板设计、数据聚合、格式化",
                "content": None,
            },
            "批量处理工作流": {
                "desc": "批量执行 ANSYS 输入文件的流程设计和状态管理",
                "content": None,
            },
            "ANSYS-求解器集成": {
                "desc": "Python 与 ANSYS 求解器的进程管理、目录重定向、环境隔离",
                "content": None,
            },
        },
    },
    "知识管理与工具链": {
        "desc": "开发工具使用、知识管理方法、效率提升技巧",
        "keywords": [
            "obsidian", "知识库", "knowledge", "笔记", "transcript",
            "memory", "CLAUDE.md", "skill", "MCP", "hook",
            "claude code", "vscode", "git",
        ],
        "topics": {
            "Claude-Code-使用技巧": {
                "desc": "Claude Code 的配置、Skills、Hooks、MCP 等高级功能",
                "content": None,
            },
            "Obsidian-知识库设计": {
                "desc": "从对话记录到结构化知识库的设计思路和实现",
                "content": None,
            },
            "MCP-与-Skills-设计": {
                "desc": "MCP (Model Context Protocol) 和 Skills 的设计模式",
                "content": None,
            },
            "开发环境配置": {
                "desc": "Windows + ANSYS + Python 环境的配置管理和常见问题",
                "content": None,
            },
        },
    },
}

# ---------------------------------------------------------------------------
# 项目静态分析数据 (从代码库中提取)
# ---------------------------------------------------------------------------

PROJECT_ANALYSIS = {
    "ansysagent": {
        "name": "cae-agent",
        "full_name": "CAE 智能辅助系统",
        "description": "面向 ANSYS 场景的最小可运行 CAE 智能辅助系统，提供日志分析、LLM 增强诊断、求解器执行和报告生成能力。",
        "tech_stack": {
            "核心语言": "Python 3.11+",
            "Web框架": "FastAPI + Uvicorn",
            "LLM服务": "DeepSeek V4 (Pro/Flash)，兼容 Anthropic SDK",
            "仿真引擎": "ANSYS 241+ (PyMAPDL), ANSYS 242+ (PyMechanical)",
            "数据格式": "Markdown (报告), JSON (API), .inp/.dat/.mac (输入)",
            "配置管理": "python-dotenv (.env), CLAUDE.md",
            "依赖管理": "requirements.txt (核心), requirements-mechanical.txt (可选)",
        },
        "modules": [
            {
                "name": "main.py",
                "role": "FastAPI 入口，9 个 REST 端点，组装层",
                "responsibility": "路由、请求校验、模块串联",
                "forbidden": "不写业务逻辑",
            },
            {
                "name": "log_parser.py",
                "role": "日志解析 + 正则错误检测",
                "responsibility": "正则匹配 + 日志截取",
                "forbidden": "不调用外部服务",
                "details": "4 类关键词：singular_matrix, convergence_failed, contact_penetration, unknown_error",
            },
            {
                "name": "llm_analyzer.py",
                "role": "DeepSeek LLM 分析 + 本地规则回退",
                "responsibility": "LLM 调用 + 回退规则",
                "forbidden": "不读写文件",
                "details": "无 API Key 时自动降级到本地规则分析",
            },
            {
                "name": "report_generator.py",
                "role": "Markdown 报告生成",
                "responsibility": "Markdown 拼装 + 落盘",
                "forbidden": "不分析、不调用 API",
            },
            {
                "name": "ansys_runner.py",
                "role": "PyMAPDL 封装",
                "responsibility": "MAPDL 生命周期管理",
                "forbidden": "不分析日志",
                "details": ".inp/.dat/.mac 执行, LOCALAPPDATA 重定向",
            },
            {
                "name": "mechanical_runner.py",
                "role": "PyMechanical 批量接触",
                "responsibility": "Mechanical 批量接触",
                "forbidden": "不处理 MAPDL",
                "details": "ANSYS 242+ 批量接触对创建",
            },
        ],
        "skills": [
            {
                "name": "batch-contact",
                "desc": "基于 Named Selection 前缀批量创建 Mechanical 接触对（242+）",
            },
            {
                "name": "check-ansys-env",
                "desc": "检查 CAE Agent 完整环境状态，包括 LLM 连通性、PyMAPDL 可用性和 PyMechanical 版本检测",
            },
            {
                "name": "run-log-analysis",
                "desc": "分析 ANSYS 求解日志，检测错误并生成 Markdown 报告",
            },
            {
                "name": "run-mapdl-input",
                "desc": "执行 MAPDL 输入文件（.inp/.dat/.mac）并可选自动分析结果日志",
            },
        ],
        "conventions": [
            "两阶段设计：所有执行端点默认 preview 模式，需显式传 launch_*=true 才真实启动求解器",
            "运行时目录重定向：PyMAPDL/PyMechanical 的 LOCALAPPDATA 被重定向到 runtime_data/，避免 C 盘权限问题",
            "LLM 回退：无 API Key 时自动降级到本地规则分析（覆盖奇异矩阵、不收敛、接触穿透三类）",
            "环境变量统一由 .env 管理，通过 python-dotenv 加载",
            "日志文件优先级：.out > .log > .err，过滤隐藏文件和临时文件",
            "Windows 路径：默认 ANSYS 安装路径在 D:\\ANSYS Inc\\v241\\",
        ],
    },
}

# ---------------------------------------------------------------------------
# Timeline events reconstructed from conversations
# ---------------------------------------------------------------------------

PROJECT_TIMELINE = {
    "ansysagent": [
        {
            "date": "2026-05-17",
            "title": "代码配置检查",
            "type": "质量检查",
            "changes": [
                "首次全面审查 ansys_runner.py 的配置问题",
                "确认 LOCALAPPDATA 重定向到 runtime_data/ 的机制",
                "确认两阶段设计模式（preview → launch）",
            ],
        },
        {
            "date": "2026-05-17",
            "title": "模型配置更新",
            "type": "配置变更",
            "changes": [
                "确认当前使用模型为 deepseek-v4-pro",
                "将 LLM 分析模型切换为 DeepSeek V4 接口（兼容 Anthropic SDK）",
            ],
        },
        {
            "date": "2026-05-18",
            "title": "端到端测试验证",
            "type": "测试",
            "changes": [
                "使用 simple 配置文件对完整链路进行测试",
                "运行日志分析服务，确认 0 错误检测通过",
                "验证 rule_based 分析模式正常运行",
            ],
        },
        {
            "date": "2026-05-18",
            "title": "文档与项目规范化",
            "type": "文档",
            "changes": [
                "生成 README 文档，描述功能、架构和使用方式",
                "清理和规范化项目结构",
            ],
        },
        {
            "date": "2026-05-27",
            "title": "架构分析与技能提炼",
            "type": "架构设计",
            "changes": [
                "全面分析文件夹架构和模块职责边界",
                "提炼出 4 个 Skills：batch-contact, check-ansys-env, run-log-analysis, run-mapdl-input",
                "创建 CLAUDE.md 项目文档",
                "配置 MCP (Model Context Protocol) 集成 DeepSeek",
                "与 LangChain 架构进行对比分析，确认本项目的精简路线",
            ],
        },
        {
            "date": "2026-05-27",
            "title": "能力扩展需求",
            "type": "需求",
            "changes": [
                "提出报告增强需求：除错误信息外，还需包含应力、形变、频率等物理性质数据指标",
            ],
        },
        {
            "date": "2026-06-05",
            "title": "安全与编码规范化",
            "type": "质量改进",
            "changes": [
                "将 .env 加入 .gitignore，避免 API Key 泄露",
                "修复/统一中文编码为 UTF-8，覆盖 README、接口返回、报告",
                "确立三层能力架构：FastAPI(主应用) + MCP(工具能力) + Skills(流程编排)",
            ],
        },
        {
            "date": "2026-06-06",
            "title": "知识管理系统建设",
            "type": "工具建设",
            "changes": [
                "集成 Obsidian 为知识管理前端",
                "构建 Claude Code → Obsidian 自动导入管道",
                "配置 Stop Hook 实现对话结束后自动更新知识库",
                "构建知识精炼器，将对话拆解为项目和专业领域结构化笔记",
            ],
        },
    ],
}

# 改进路线图
ROADMAP = {
    "ansysagent": [
        {
            "priority": "P0 - 紧急",
            "items": [
                {
                    "title": "物理结果数据提取",
                    "desc": "在求解完成后自动提取应力、形变、频率、模态等物理性质数据，丰富报告内容",
                    "status": "已识别需求，待实现",
                },
            ],
        },
        {
            "priority": "P1 - 重要",
            "items": [
                {
                    "title": "MCP 工具完备化",
                    "desc": "将核心功能（日志分析、求解器执行、环境检查）封装为标准化 MCP 工具，供其他 Agent 调用",
                    "status": "已完成 Skills 封装，MCP 通道已配置",
                },
                {
                    "title": "报告模板系统",
                    "desc": "支持自定义报告模板，满足不同场景（调试、归档、汇报）的差异化需求",
                    "status": "待设计",
                },
                {
                    "title": "错误检测扩展",
                    "desc": "在 ERROR_PATTERNS 中增加更多 ANSYS 常见错误模式（如接触刚化、单元畸变等）",
                    "status": "框架已就绪，可随时扩展",
                },
            ],
        },
        {
            "priority": "P2 - 优化",
            "items": [
                {
                    "title": "多求解器支持",
                    "desc": "扩展支持 Fluent、LS-DYNA 等其他 ANSYS 求解器的日志格式",
                    "status": "远期规划",
                },
                {
                    "title": "Web Dashboard",
                    "desc": "为 FastAPI 服务添加 Web 前端，提供可视化的环境检查、任务提交和结果查看",
                    "status": "远期规划",
                },
                {
                    "title": "CI/CD 集成",
                    "desc": "将日志分析能力集成到 CI/CD 管道中，实现仿真结果的自动化质量门禁",
                    "status": "远期规划",
                },
            ],
        },
    ],
}


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def resolve_project_name(dirname: str) -> str:
    if dirname.startswith("d--"):
        return dirname[3:]
    if dirname.startswith(("C--", "c--")):
        return "default"
    return dirname


def slugify(text: str) -> str:
    text = re.sub(r'[\\/*?:"<>|\n\r]', "", text)
    text = re.sub(r'\s+', " ", text).strip()
    return text[:80].replace(" ", "-")


def safe_title(text: str) -> str:
    text = re.sub(r'[\\/*?:"<>|\n\r]', "", text)
    return re.sub(r'\s+', " ", text).strip()


# ---------------------------------------------------------------------------
# JSONL 解析 (与旧版相同)
# ---------------------------------------------------------------------------

def parse_transcript(filepath: Path, project_name: str) -> Optional[Conversation]:
    conv = Conversation(
        session_id="", project_name=project_name,
        title="未命名对话", timestamp="",
    )
    all_user_text = []
    all_assistant_text = []
    titles_seen = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                conv.total_events += 1
                etype = event.get("type", "")

                if not conv.session_id:
                    conv.session_id = event.get("sessionId", "")
                if not conv.timestamp and "timestamp" in event:
                    conv.timestamp = event["timestamp"]

                if etype == "ai-title":
                    title = event.get("aiTitle", "")
                    if title:
                        titles_seen.append(title)

                elif etype == "user":
                    msg = event.get("message", {})
                    content = msg.get("content", "")
                    if isinstance(content, list):
                        texts = []
                        for c in content:
                            if isinstance(c, dict) and c.get("type") == "text":
                                texts.append(c.get("text", ""))
                            elif isinstance(c, str):
                                texts.append(c)
                        text = " ".join(texts)
                    elif isinstance(content, str):
                        text = content
                    else:
                        text = str(content)

                    if event.get("isMeta"):
                        continue

                    cleaned = re.sub(r"<[^>]+>", "", text).strip()
                    cleaned = re.sub(
                        r'The user opened the file [^\s]+ in the IDE\..*?\.\s*',
                        '', cleaned, flags=re.IGNORECASE
                    ).strip()
                    cleaned = re.sub(
                        r'\b[/]?\s*(init|help|clear|compact)\b',
                        '', cleaned, flags=re.IGNORECASE
                    ).strip()
                    cleaned = re.sub(r'\n\s*\n', '\n', cleaned).strip()
                    # 跳过内部噪音
                    cleaned = re.sub(r'^call_\w+\s*$', '', cleaned, flags=re.MULTILINE).strip()
                    cleaned = re.sub(r'^(C:\\|/c/)[^\n]*\.output\s*$', '', cleaned, flags=re.MULTILINE).strip()
                    cleaned = re.sub(r'^Background command[^\n]*completed[^\n]*\s*$', '', cleaned, flags=re.MULTILINE | re.IGNORECASE).strip()
                    if cleaned and len(cleaned) > 3:
                        all_user_text.append(cleaned)

                elif etype == "assistant":
                    msg = event.get("message", {})
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for c in content:
                            if isinstance(c, dict):
                                ct = c.get("type", "")
                                if ct == "text":
                                    all_assistant_text.append(c.get("text", "")[:300])
                                elif ct == "tool_use":
                                    conv.tool_names.add(c.get("name", "unknown"))
                            elif isinstance(c, str):
                                all_assistant_text.append(c[:300])

                tur = event.get("toolUseResult")
                if isinstance(tur, dict):
                    fp = tur.get("filePath", "")
                    if fp:
                        fname = Path(fp).name
                        if fname:
                            conv.files_touched.add(fname)

    except Exception as e:
        print(f"  [WARN] {filepath.name}: {e}", file=sys.stderr)
        return None

    conv.user_messages = all_user_text
    conv.assistant_texts = all_assistant_text

    if titles_seen:
        unique_titles = list(dict.fromkeys(titles_seen))
        conv.title = unique_titles[-1]
    elif all_user_text:
        first = all_user_text[0].strip()
        if not first:
            first = all_user_text[1] if len(all_user_text) > 1 else "未命名对话"
        conv.title = first[:50] + ("..." if len(first) > 50 else "")

    conv.title = safe_title(conv.title)
    if not conv.title.strip():
        conv.title = "未命名对话"
    return conv


# ---------------------------------------------------------------------------
# 文件操作
# ---------------------------------------------------------------------------

def write_note(path: Path, content: str, dry_run: bool = False):
    if dry_run:
        print(f"  [DRY] → {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# 生成器: 项目笔记
# ---------------------------------------------------------------------------

def generate_project_overview(project_name: str, conversations: list[Conversation]) -> str:
    info = PROJECT_ANALYSIS.get(project_name, {})
    timeline = PROJECT_TIMELINE.get(project_name, [])

    # 统计
    total_events = sum(c.total_events for c in conversations)
    all_tools = set()
    all_files = set()
    for c in conversations:
        all_tools.update(c.tool_names)
        all_files.update(c.files_touched)

    # 时间线
    timeline_md = ""
    for event in sorted(timeline, key=lambda e: e["date"]):
        changes = "\n".join(f"     - {c}" for c in event["changes"])
        timeline_md += f"""
> **{event['date']}** — {event['title']} `[{event['type']}]`
{changes}
"""

    note = f"""---
project: "{project_name}"
type: project-overview
conversation_count: {len(conversations)}
total_events: {total_events}
tools_used: [{", ".join(sorted(all_tools))}]
tags:
  - project
  - moc
  - overview
created: {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}
---

# 📋 {info.get('full_name', project_name)}

> {info.get('description', '项目概述')}

---

## 📊 项目概况

| 指标 | 数值 |
|------|------|
| 对话数 | {len(conversations)} |
| 总事件数 | {total_events} |
| 使用工具种类 | {len(all_tools)} |
| 涉及文件数 | {len(all_files)} |
| 模块数 | {len(info.get('modules', []))} |
| Skills | {len(info.get('skills', []))} |

## 🔄 相关笔记

- [[../📈 更新进度|📈 更新进度]] — 开发时间线
- [[../🎯 改进方向|🎯 改进方向]] — 待办路线图
- [[../🔧 技术栈|🔧 技术栈]] — 技术选型分析
- [[../🔄 能力流程|🔄 能力流程]] — 能力与工作流
- [[../🏗️ 架构设计|🏗️ 架构设计]] — 架构设计细节
- [[../⚙️ 配置管理|⚙️ 配置管理]] — 配置与环境

## 📈 开发时间线

{timeline_md}

## 📂 对话记录

"""
    for i, conv in enumerate(sorted(conversations, key=lambda c: c.timestamp, reverse=True), 1):
        note += f"{i}. [[conversations/{conv.date_str} {slugify(conv.title)}|{conv.title}]] — {conv.date_str} ({len(conv.user_messages)} 条提问)\n"

    note += """
---
*由 Claude Code 知识精炼器自动生成*
"""
    return note


def generate_project_timeline(project_name: str) -> str:
    timeline = PROJECT_TIMELINE.get(project_name, [])
    note = f"""---
project: "{project_name}"
type: timeline
tags:
  - project
  - timeline
created: {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}
---

# 📈 更新进度

> {project_name} 项目的开发时间线和变更记录

## 时间线

| 日期 | 事件 | 类型 | 关键变更 |
|------|------|------|---------|
"""
    for event in sorted(timeline, key=lambda e: e["date"]):
        changes = "<br>".join(event["changes"])
        note += f"| {event['date']} | {event['title']} | {event['type']} | {changes} |\n"

    note += f"""

## 📊 统计

- **总事件数**: {len(timeline)}
- **时间跨度**: {timeline[0]['date'] if timeline else 'N/A'} → {timeline[-1]['date'] if timeline else 'N/A'}

## 🔄 类型分布

"""
    type_counts = defaultdict(int)
    for e in timeline:
        type_counts[e["type"]] += 1
    for t, n in sorted(type_counts.items()):
        note += f"- {t}: {n} 次\n"

    note += """
---
*由 Claude Code 知识精炼器自动生成*
"""
    return note


def generate_roadmap(project_name: str) -> str:
    roadmap = ROADMAP.get(project_name, [])
    note = f"""---
project: "{project_name}"
type: roadmap
tags:
  - project
  - roadmap
  - planning
created: {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}
---

# 🎯 改进方向

> {project_name} 项目的改进路线图和待办事项

"""

    for section in roadmap:
        note += f"""
## {section['priority']}

"""
        for item in section["items"]:
            note += f"""
### {item['title']}

- **状态**: {item['status']}
- **描述**: {item['desc']}

"""

    note += """

---

## 🗺️ 路线图可视化

```
已完成 ✅                    进行中 🔄                   远期规划 📅

Skills 封装 ✅              物理数据提取 🔄            多求解器 📅
MCP 通道 ✅                 报告模板 🔄                Web Dashboard 📅
Obsidian 集成 ✅             错误检测扩展 🔄            CI/CD 📅
编码规范化 ✅
自动 Hook ✅
```

---
*由 Claude Code 知识精炼器自动生成*
"""
    return note


def generate_tech_stack(project_name: str) -> str:
    info = PROJECT_ANALYSIS.get(project_name, {})
    tech = info.get("tech_stack", {})

    note = f"""---
project: "{project_name}"
type: tech-stack
tags:
  - project
  - tech-stack
  - architecture
created: {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}
---

# 🔧 技术栈

> {project_name} 项目的技术选型分析

## 技术栈概览

| 层级 | 技术 | 说明 |
|------|------|------|
"""
    for key, val in tech.items():
        note += f"| {key} | {val} | |\n"

    note += """
## 技术选型理由

### 为什么选择 FastAPI？

- **异步支持**: 原生 async/await，适合 I/O 密集的 LLM API 调用和求解器进程管理
- **自动文档**: OpenAPI / Swagger 自动生成，降低理解成本
- **类型安全**: Pydantic 模型校验，减少运行时错误
- **生态成熟**: 与 Uvicorn 配合，生产级 ASGI 服务器

### 为什么选择 DeepSeek V4？

- **兼容 Anthropic SDK**: 可直接使用 `ANTHROPIC_BASE_URL` 切换端点
- **成本优势**: 相比 Claude Opus，提供更有竞争力的定价
- **双语能力**: 中英文工程场景均表现良好
- **V4 Pro vs Flash**: 复杂分析用 Pro，简单任务可降级到 Flash

### 为什么采用两阶段设计 (preview → launch)？

- **安全第一**: 避免误操作直接启动大型求解器任务
- **可审核**: 用户可预览将在 ANSYS 中执行的完整参数
- **批量友好**: 批量处理时允许用户确认所有配置后再执行

### 为什么 LOCALAPPDATA 重定向？

- **Windows 权限**: C 盘通常受 UAC 保护，ANSYS 的运行时文件需要写入权限
- **隔离性**: 每个项目的运行时数据独立存放，便于清理和调试

## 依赖关系

```mermaid
graph TD
    A[FastAPI 服务层] --> B[log_parser.py]
    A --> C[llm_analyzer.py]
    A --> D[report_generator.py]
    A --> E[ansys_runner.py]
    A --> F[mechanical_runner.py]
    C --> G[DeepSeek API]
    E --> H[ANSYS MAPDL]
    F --> I[ANSYS Mechanical]
    D --> J[Markdown 报告]
```

---
*由 Claude Code 知识精炼器自动生成*
"""
    return note


def generate_capability_workflow(project_name: str) -> str:
    info = PROJECT_ANALYSIS.get(project_name, {})
    skills = info.get("skills", [])

    skills_md = ""
    for s in skills:
        skills_md += f"\n### {s['name']}\n\n{s['desc']}\n"

    note = f"""---
project: "{project_name}"
type: capability-workflow
tags:
  - project
  - capability
  - workflow
created: {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}
---

# 🔄 能力流程

> {project_name} 的核心能力和工作流程

## 🎯 核心链路

```
日志文件 → 错误检测 → LLM分析 → Markdown报告
```

## ⚡ 能力矩阵

| 能力 | 端点/入口 | 输入 | 输出 |
|------|----------|------|------|
| 日志分析 | POST /analyze-log | .out/.log/.err 文件或文本 | JSON + Markdown 报告 |
| MAPDL 执行 | POST /run-mapdl | .inp/.dat/.mac 文件 | 求解日志 + 可选自动分析 |
| 环境检查 | GET /health, /mapdl-status, /mechanical-status | 无 | JSON 状态信息 |
| 批量接触 | batch-contact Skill | Named Selection 前缀 | 接触对配置 |

## 🛠️ Skills

{skills_md}

## 🔗 端到端工作流

### 1. 标准日志分析流程

```mermaid
sequenceDiagram
    participant User
    participant FastAPI
    participant LogParser
    participant LLMAnalyzer
    participant ReportGen

    User->>FastAPI: POST /analyze-log
    FastAPI->>LogParser: 读取/解析日志
    LogParser->>LogParser: 正则匹配 4 类错误
    LogParser-->>FastAPI: 错误列表
    FastAPI->>LLMAnalyzer: 发送错误摘要
    alt DeepSeek 可用
        LLMAnalyzer->>DeepSeek API: 分析请求
        DeepSeek API-->>LLMAnalyzer: 分析结果
    else DeepSeek 不可用
        LLMAnalyzer->>LLMAnalyzer: 本地规则回退
    end
    LLMAnalyzer-->>FastAPI: 分析结果
    FastAPI->>ReportGen: 生成 Markdown
    ReportGen-->>FastAPI: 报告路径
    FastAPI-->>User: JSON 响应 + 报告
```

### 2. MAPDL 执行流程

```
用户提交 .inp 文件
  → FastAPI 校验参数 (preview 模式)
    → 用户确认 launch_mapdl=true
      → LOCALAPPDATA 重定向到 runtime_data/
        → PyMAPDL 启动 ANSYS 求解器
          → 等待求解完成
            → 收集输出日志
              → (可选) 自动调用日志分析
                → 返回结果 + 报告路径
```

### 3. 两阶段设计模式

所有执行端点都遵循此模式：

```
第一阶段 (preview=True):
  → 返回将执行的参数和预估影响
  → 不实际启动求解器

第二阶段 (launch_*=true):
  → 确认后真正执行
  → 返回执行结果
```

---
*由 Claude Code 知识精炼器自动生成*
"""
    return note


def generate_architecture(project_name: str) -> str:
    info = PROJECT_ANALYSIS.get(project_name, {})
    modules = info.get("modules", [])
    conventions = info.get("conventions", [])

    modules_md = ""
    for m in modules:
        details = m.get("details", "")
        details_line = f"\n  - **核心细节**: {details}" if details else ""
        modules_md += f"""
### {m['name']}

- **角色**: {m['role']}
- **职责**: {m['responsibility']}
- **禁止**: {m['forbidden']}{details_line}
"""

    conventions_md = "\n".join(f"- {c}" for c in conventions)

    note = f"""---
project: "{project_name}"
type: architecture
tags:
  - project
  - architecture
  - design
created: {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}
---

# 🏗️ 架构设计

> {info.get('full_name', project_name)} 的架构设计详解

## 架构图

```
main.py          FastAPI 入口，9 个 REST 端点，组装层
├─ log_parser.py       日志解析 + 正则错误检测（4 类关键词）
├─ llm_analyzer.py     DeepSeek LLM 分析 + 本地规则回退
├─ report_generator.py  Markdown 报告生成
├─ ansys_runner.py     PyMAPDL 封装（.inp/.dat/.mac 执行）
└─ mechanical_runner.py PyMechanical 242+ 批量接触
```

## 设计原则

### 1. 三层能力分层

```
┌─────────────────────────────────┐
│  Skills (流程编排层)             │
│  定义端到端工作流，串联底层能力  │
├─────────────────────────────────┤
│  MCP (工具能力层)                │
│  标准化工具接口，供外部 Agent 调用│
├─────────────────────────────────┤
│  FastAPI (主应用层)              │
│  REST API，请求校验，模块组装    │
└─────────────────────────────────┘
```

### 2. 模块职责边界

| 模块 | 职责 | 禁止 |
|------|------|------|
"""
    for m in modules:
        note += f"| `{m['name']}` | {m['responsibility']} | {m['forbidden']} |\n"

    note += f"""
## 模块详解
{modules_md}

## 关键约定

{conventions_md}

## 与 LangChain 的区别

| 维度 | 本项目 (cae-agent) | LangChain |
|------|-------------------|-----------|
| 定位 | CAE 专用工具 | 通用 LLM 应用框架 |
| 架构 | 简单分层，模块直连 | 复杂链式抽象 (Chain/Agent/Tool) |
| 求解器集成 | 直接封装 PyMAPDL/PyMechanical | 无内置求解器支持 |
| LLM 抽象 | 直接调用 Anthropic SDK | 多层 Provider 抽象 |
| 学习成本 | 低（5 个模块，职责明确） | 高（大量抽象概念） |
| 适用场景 | ANSYS 仿真自动化 | 通用 LLM 应用开发 |

**设计选择**: 本项目选择了精简路线，避免 LangChain 的过度抽象。对 CAE 场景而言，模块职责分离 + LLM 回退机制已经足够。

---
*由 Claude Code 知识精炼器自动生成*
"""
    return note


def generate_config_management(project_name: str) -> str:
    note = f"""---
project: "{project_name}"
type: config-management
tags:
  - project
  - config
  - devops
created: {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}
---

# ⚙️ 配置管理

> {project_name} 的环境配置、密钥管理和安全策略

## 环境变量 (.env)

| 变量 | 用途 | 必需 |
|------|------|------|
| `ANTHROPIC_AUTH_TOKEN` | DeepSeek API Key | 否 (无 Key 时回退本地规则) |
| `ANTHROPIC_BASE_URL` | API 端点 (默认为 Anthropic，可切换) | 否 |
| `ANTHROPIC_MODEL` | 默认模型 ID | 否 |
| `ANSYS241_DIR` | ANSYS 安装路径 | 是 (PyMAPDL 真实执行) |

## 安全策略

### API Key 保护

- `.env` 已加入 `.gitignore`，防止密钥泄露
- API Key 通过 `python-dotenv` 在运行时加载
- 代码中不硬编码任何密钥

### 编码规范化

- 统一 UTF-8 编码
- 覆盖范围：README.md、API 接口返回、Markdown 报告、日志输出
- Windows GBK → UTF-8 迁移已完成

## 运行时配置

```python
# LOCALAPPDATA 重定向机制
# 默认 ANSYS 会将临时文件写入 %LOCALAPPDATA%
# 这在 Windows C 盘可能导致权限问题
# 解决：运行时将 LOCALAPPDATA 重定向到 runtime_data/
os.environ["LOCALAPPDATA"] = str(Path.cwd() / "runtime_data")
```

## 文件优先级

| 类型 | 优先级 | 说明 |
|------|--------|------|
| 求解日志 | `.out` > `.log` > `.err` | ANSYS 输出文件的读取顺序 |
| 隐藏文件 | 过滤 | 跳过 `.` 开头的隐藏文件 |
| 临时文件 | 过滤 | 跳过 tmp 目录和临时文件 |

## 依赖管理

```bash
# 核心依赖 (所有场景必需)
pip install -r requirements.txt

# Mechanical 可选依赖 (仅批量接触功能需要)
pip install -r requirements-mechanical.txt
```

---
*由 Claude Code 知识精炼器自动生成*
"""
    return note


# ---------------------------------------------------------------------------
# 生成器: 对话笔记 (精简版)
# ---------------------------------------------------------------------------

def generate_conversation_note(conv: Conversation, project_name: str) -> str:
    topics = []
    all_text = " ".join(conv.user_messages + conv.assistant_texts).lower()
    for domain_name, domain_info in DOMAINS.items():
        for kw in domain_info["keywords"]:
            if kw.lower() in all_text:
                topics.append(domain_name)
                break

    fm_tags = "\n  - ".join(sorted(set(
        t.replace(" ", "-") for t in topics
    ))) if topics else ""
    fm_topics = "\n".join(f'  - "[[../../Knowledge/{t}/📋 索引|{t}]]"' for t in sorted(set(topics)))

    note = f"""---
date: {conv.date_str}
project: "{project_name}"
session: "{conv.session_id}"
title: "{conv.title}"
tags:
  - conversation
  - {fm_tags}
tools_used: [{", ".join(sorted(conv.tool_names))}]
message_count: {len(conv.user_messages)}
event_count: {conv.total_events}
knowledge_domains:
{fm_topics}
---

# {conv.title}

> 📅 {conv.date_str} | 🔗 `{conv.session_id[:8]}...` | 🛠️ {", ".join(sorted(conv.tool_names)) if conv.tool_names else "无"}

## 💬 对话内容

"""
    for i, msg in enumerate(conv.user_messages, 1):
        display = msg[:500] + ("..." if len(msg) > 500 else "")
        note += f"### {i}. {display}\n\n"

    if conv.files_touched:
        note += "## 📁 涉及文件\n\n"
        for fname in sorted(conv.files_touched):
            note += f"- {fname}\n"

    note += f"""
---
*会话 ID: {conv.session_id} | 事件数: {conv.total_events}*
"""
    return note


# ---------------------------------------------------------------------------
# 生成器: 知识域笔记
# ---------------------------------------------------------------------------

def generate_domain_index(domain_name: str, domain_info: dict) -> str:
    note = f"""---
domain: "{domain_name}"
type: knowledge-index
tags:
  - knowledge
  - moc
  - domain
created: {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}
---

# 📋 {domain_name} — 知识索引

> {domain_info['desc']}

## 📂 知识点

"""

    for topic_name, topic_info in domain_info["topics"].items():
        note += f"- [[{topic_name}|{topic_name}]] — {topic_info['desc']}\n"

    note += """

---
*由 Claude Code 知识精炼器自动生成*
"""
    return note


def generate_knowledge_topic(
    domain_name: str, topic_name: str, topic_info: dict,
    domain_info: dict, conversations: list[Conversation]
) -> str:
    """为单个知识点生成详细笔记。"""
    # 找到相关对话
    related_convos = []
    for conv in conversations:
        all_text = " ".join(conv.user_messages + conv.assistant_texts).lower()
        for kw in DOMAINS.get(domain_name, {}).get("keywords", []):
            if kw.lower() in all_text:
                if conv.session_id not in {c.session_id for c in related_convos}:
                    related_convos.append(conv)
                break

    related_md = ""
    for conv in related_convos[:5]:
        related_md += f"- [[../../Projects/{conv.project_name}/conversations/{conv.date_str} {slugify(conv.title)}|{conv.title}]] ({conv.date_str})\n"

    # 从对话中提取相关片段
    snippets = []
    for conv in related_convos[:3]:
        for msg in conv.user_messages + conv.assistant_texts:
            for kw in DOMAINS.get(domain_name, {}).get("keywords", [])[:5]:
                if kw.lower() in msg.lower() and len(msg) > 50:
                    snippets.append(msg[:300] + "...")
                    break
            if len(snippets) >= 3:
                break
        if len(snippets) >= 3:
            break

    snippets_md = ""
    for s in snippets[:3]:
        snippets_md += f"> {s}\n\n"

    note = f"""---
domain: "{domain_name}"
topic: "{topic_name}"
type: knowledge-article
tags:
  - knowledge
  - {domain_name.replace(" ", "-")}
created: {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}
---

# 📝 {topic_name}

> 🏷️ **领域**: [[📋 索引|{domain_name}]]
> {topic_info['desc']}

---

## 🔍 上下文

本知识点由 Claude Code 与 ansysagent 项目的对话记录提炼而成。

### 相关对话

{related_md if related_md else "暂无直接相关对话。"}

### 关键片段

{snippets_md if snippets_md else "暂无相关代码/对话片段。"}

---

## 💡 知识要点

> *此知识点由对话上下文自动提取。在 Obsidian 中打开后可进一步补充：*
> - 理论背景
> - 实践指南
> - 常见问题与解决方案
> - 相关资源链接

## 🔗 关联主题

"""
    # 列出同域其他主题
    for other_topic in domain_info.get("topics", {}):
        if other_topic != topic_name:
            note += f"- [[{other_topic}]]\n"

    note += """
---
*由 Claude Code 知识精炼器自动生成 — 请在 Obsidian 中补充和细化*
"""
    return note


def generate_knowledge_master_index() -> str:
    note = f"""---
type: master-index
tags:
  - knowledge
  - moc
  - master-index
created: {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}
---

# 📚 知识索引

> 按现实世界专业方向组织的经验知识库

## 🗂️ 知识领域

"""

    for domain_name, domain_info in DOMAINS.items():
        topic_count = len(domain_info["topics"])
        note += f"""
### [[{domain_name}/📋 索引|{domain_name}]]

{domain_info['desc']}

包含 {topic_count} 个知识点：
"""
        for topic_name in domain_info["topics"]:
            note += f"- [[{domain_name}/{topic_name}|{topic_name}]]\n"

    note += """
---

## 🔍 使用指南

- 每个领域文件夹包含该方向的结构化知识点
- 知识点之间通过 `[[]]` 双向链接互联
- 对话记录位于 `Projects/<项目名>/conversations/`
- 从知识点可以反向链接到相关的对话记录

---
*由 Claude Code 知识精炼器自动生成*
"""
    return note


def generate_main_dashboard(project_names: list[str]) -> str:
    projects_md = ""
    for pn in sorted(project_names):
        info = PROJECT_ANALYSIS.get(pn, {})
        projects_md += f"""
### [[Projects/{pn}/📋 项目总览|{info.get('full_name', pn)}]]

{info.get('description', '')}

- [[Projects/{pn}/📈 更新进度|📈 更新进度]]
- [[Projects/{pn}/🎯 改进方向|🎯 改进方向]]
- [[Projects/{pn}/🔧 技术栈|🔧 技术栈]]
- [[Projects/{pn}/🔄 能力流程|🔄 能力流程]]
- [[Projects/{pn}/🏗️ 架构设计|🏗️ 架构设计]]
- [[Projects/{pn}/⚙️ 配置管理|⚙️ 配置管理]]
"""

    domain_md = ""
    for domain_name, domain_info in DOMAINS.items():
        domain_md += f"- [[Knowledge/{domain_name}/📋 索引|{domain_name}]] — {domain_info['desc']}\n"

    note = f"""---
type: dashboard
tags:
  - dashboard
  - moc
pinned: true
created: {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}
updated: {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}
---

# 🏠 知识总览

> 🤖 Claude Code 知识精炼器 — 结构化项目知识 + 专业领域经验库

---

## 🗂️ 项目

{projects_md}

## 📚 知识领域

{domain_md}

## 🧭 快速导航

| 目标 | 路径 |
|------|------|
| 查看项目进度 | `Projects/<项目>/📈 更新进度` |
| 了解技术选型 | `Projects/<项目>/🔧 技术栈` |
| 查找专业知识 | `Knowledge/<领域>/📋 索引` |
| 回顾对话记录 | `Projects/<项目>/conversations/` |
| 创建笔记模板 | `Templates/` |

---
*由 Claude Code 知识精炼器自动生成*
"""
    return note


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def discover_transcripts() -> dict[str, list[Path]]:
    project_files = defaultdict(list)
    if not PROJECTS_DIR.exists():
        print(f"[ERROR] 目录不存在: {PROJECTS_DIR}", file=sys.stderr)
        sys.exit(1)
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        jsonl_files = sorted(project_dir.glob("*.jsonl"))
        if jsonl_files:
            project_files[project_dir.name] = jsonl_files
    return dict(project_files)


def refine_all(dry_run: bool = False):
    print("=" * 60)
    print("Claude Code 知识精炼器")
    print(f"输出: {IDEA_ROOT}")
    print("=" * 60)

    # 1. 清理旧输出
    if not dry_run and IDEA_ROOT.exists():
        # 保留 .obsidian
        for item in IDEA_ROOT.iterdir():
            if item.name not in (".obsidian",):
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink()
        print(f"  🧹 已清理旧输出")

    # 2. 初始化 vault
    if not dry_run:
        obsidian_dir = IDEA_ROOT / ".obsidian"
        obsidian_dir.mkdir(parents=True, exist_ok=True)
        (IDEA_ROOT / "Templates").mkdir(parents=True, exist_ok=True)

    # 3. 解析对话
    print("\n📖 解析对话内容...")
    project_files = discover_transcripts()
    all_conversations = []
    project_conversations = defaultdict(list)

    for dirname, files in sorted(project_files.items()):
        project_name = resolve_project_name(dirname)
        if project_name not in PROJECT_ANALYSIS:
            continue  # 只处理有分析数据的项目

        print(f"\n  项目: {project_name} ({len(files)} 个对话)")
        for fpath in files:
            conv = parse_transcript(fpath, project_name)
            if conv and conv.user_messages:
                all_conversations.append(conv)
                project_conversations[project_name].append(conv)
                print(f"    ✓ {conv.date_str} — {conv.title[:50]}")

    print(f"\n  共解析 {len(all_conversations)} 个有效对话")

    # 4. 生成主仪表盘
    print("\n✍️ 生成知识精炼笔记...")
    project_names = sorted(project_conversations.keys())
    dashboard = generate_main_dashboard(project_names)
    write_note(IDEA_ROOT / "🏠 知识总览.md", dashboard, dry_run)
    print("  ✓ 知识总览")

    # 5. 生成项目笔记
    for project_name, convs in sorted(project_conversations.items()):
        proj_dir = IDEA_ROOT / "Projects" / project_name
        conv_dir = proj_dir / "conversations"
        print(f"\n  --- {project_name} ---")

        proj_note = generate_project_overview(project_name, convs)
        write_note(proj_dir / "📋 项目总览.md", proj_note, dry_run)

        timeline_note = generate_project_timeline(project_name)
        write_note(proj_dir / "📈 更新进度.md", timeline_note, dry_run)

        roadmap_note = generate_roadmap(project_name)
        write_note(proj_dir / "🎯 改进方向.md", roadmap_note, dry_run)

        tech_note = generate_tech_stack(project_name)
        write_note(proj_dir / "🔧 技术栈.md", tech_note, dry_run)

        cap_note = generate_capability_workflow(project_name)
        write_note(proj_dir / "🔄 能力流程.md", cap_note, dry_run)

        arch_note = generate_architecture(project_name)
        write_note(proj_dir / "🏗️ 架构设计.md", arch_note, dry_run)

        config_note = generate_config_management(project_name)
        write_note(proj_dir / "⚙️ 配置管理.md", config_note, dry_run)

        for conv in convs:
            conv_note = generate_conversation_note(conv, project_name)
            fname = f"{conv.date_str} {slugify(conv.title)}.md"
            write_note(conv_dir / fname, conv_note, dry_run)

        print(f"    ✓ {len(convs)} 篇对话 + 6 篇分析笔记")

    # 6. 生成知识域笔记
    print(f"\n  --- Knowledge ---")
    master_index = generate_knowledge_master_index()
    write_note(IDEA_ROOT / "Knowledge" / "📚 知识索引.md", master_index, dry_run)

    for domain_name, domain_info in DOMAINS.items():
        domain_dir = IDEA_ROOT / "Knowledge" / domain_name
        domain_index = generate_domain_index(domain_name, domain_info)
        write_note(domain_dir / "📋 索引.md", domain_index, dry_run)

        for topic_name, topic_info in domain_info["topics"].items():
            topic_note = generate_knowledge_topic(
                domain_name, topic_name, topic_info, domain_info, all_conversations
            )
            write_note(domain_dir / f"{topic_name}.md", topic_note, dry_run)

        topic_count = len(domain_info["topics"])
        print(f"    ✓ {domain_name}: {topic_count} 个知识点")

    # 7. 报告
    total_domain_topics = sum(len(d["topics"]) for d in DOMAINS.values())
    print("\n" + "=" * 60)
    print("📊 精炼完成！")
    print(f"  输出路径:  {IDEA_ROOT}")
    print(f"  项目数:    {len(project_conversations)}")
    print(f"  对话数:    {len(all_conversations)}")
    print(f"  知识领域:  {len(DOMAINS)}")
    print(f"  知识点:    {total_domain_topics}")
    print(f"  分析笔记:  {len(project_conversations) * 6} 篇/项目")
    print()
    print("👉 在 Obsidian 中打开:")
    print(f"   选择 vault: {IDEA_ROOT}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Claude Code 知识精炼器")
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    args = parser.parse_args()
    refine_all(dry_run=args.dry_run)


if __name__ == "__main__":
    main()

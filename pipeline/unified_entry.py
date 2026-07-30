#!/usr/bin/env python3
"""
Unified Knowledge Pipeline Entry
================================
将本地 knowledge-pipeline 与 obsidian-skills 整合为统一入口。

功能：
1. 读取 pipeline_config.yaml 统一管理路径和规则
2. 设置环境变量供 legacy 脚本读取
3. 依次执行：refinery → deepener → obsidian-sync
4. 可选触发 obsidian-skills 进行 Canvas/Bases 精修

用法：
    python unified_entry.py           # 执行完整管线
    python unified_entry.py --stage refinery   # 仅执行精炼
    python unified_entry.py --dry-run          # 预览模式
    python unified_entry.py --config custom.yaml
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    print("❌ 需要 PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# ── 路径 ───────────────────────────────────
BASE = Path(__file__).resolve().parent
CONFIG_PATH = BASE / "config" / "pipeline_config.yaml"
REFINERY_SCRIPT = BASE / "knowledge_refinery.py"
DEEPENER_SCRIPT = BASE / "knowledge_deepener_v2.py"


def load_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_env(config: dict):
    """将配置注入环境变量，供 legacy 脚本读取。"""
    vault = config.get("vault_output", "D:/knowledgement")
    claude_projects = config.get("sources", {}).get("claude_projects", {}).get("path", "~/.claude/projects")

    os.environ["UNIFIED_VAULT_OUTPUT"] = os.path.expandvars(os.path.expanduser(vault))
    os.environ["UNIFIED_CLAUDE_PROJECTS"] = os.path.expandvars(os.path.expanduser(claude_projects))
    os.environ["UNIFIED_CONFIG_PATH"] = str(CONFIG_PATH)

    # 如果 legacy 脚本被 patch 过，会优先读取这些环境变量
    print(f"📁 Vault 输出: {os.environ['UNIFIED_VAULT_OUTPUT']}")
    print(f"📁 对话源: {os.environ['UNIFIED_CLAUDE_PROJECTS']}")


def patch_legacy_refinery():
    """
    动态 patch knowledge_refinery.py 的硬编码路径。
    通过创建临时副本实现，不修改原文件。
    """
    if not REFINERY_SCRIPT.exists():
        print(f"❌ 找不到 {REFINERY_SCRIPT}", file=sys.stderr)
        sys.exit(1)

    original = REFINERY_SCRIPT.read_text(encoding="utf-8")

    # Patch 1: IDEA_ROOT
    vault = os.environ.get("UNIFIED_VAULT_OUTPUT", "D:/knowledgement")
    patched = original.replace(
        'IDEA_ROOT = Path("D:/knowledgement")',
        f'IDEA_ROOT = Path(r"{vault}")'
    )

    # Patch 2: PROJECTS_DIR (如果配置中指定了)
    claude_projects = os.environ.get("UNIFIED_CLAUDE_PROJECTS", "")
    if claude_projects:
        patched = patched.replace(
            'PROJECTS_DIR = CLAUDE_HOME / "projects"',
            f'PROJECTS_DIR = Path(r"{claude_projects}")'
        )

    # 写入临时文件
    temp_script = BASE / ".knowledge_refinery_patched.py"
    temp_script.write_text(patched, encoding="utf-8")
    return temp_script


def patch_legacy_deepener(vault: str):
    """动态 patch knowledge_deepener_v2.py 的输出路径。"""
    if not DEEPENER_SCRIPT.exists():
        return None

    original = DEEPENER_SCRIPT.read_text(encoding="utf-8")
    # 原脚本写死到 BASE / "idea" / "Knowledge"
    # 改为写到 vault / "Knowledge"
    patched = original.replace(
        'KNOWLEDGE_DIR = BASE / "idea" / "Knowledge"',
        f'KNOWLEDGE_DIR = Path(r"{vault}") / "Knowledge"'
    )
    # 同时修改 DATA_FILE 路径查找
    patched = patched.replace(
        'DATA_FILE = BASE / "deep_data.json"',
        f'DATA_FILE = Path(r"{BASE / "data" / "deep_data.json"}")'
    )

    temp_script = BASE / ".knowledge_deepener_patched.py"
    temp_script.write_text(patched, encoding="utf-8")
    return temp_script


def run_stage(script: Path, label: str, timeout: int = 300):
    print(f"\n{'='*60}")
    print(f"▶️  {label}")
    print(f"{'='*60}")
    result = subprocess.run(
        [sys.executable, str(script)],
        check=False,
        timeout=timeout
    )
    if result.returncode != 0:
        print(f"⚠️  {label} 退出码: {result.returncode}", file=sys.stderr)
    return result.returncode == 0


def run_obsidian_sync(vault: str, config: dict):
    """调用 obsidian-skills 进行后处理。"""
    if not config.get("obsidian", {}).get("enabled", True):
        return True

    print(f"\n{'='*60}")
    print("▶️  Obsidian 同步 / 精修")
    print(f"{'='*60}")

    # 检查 Claude Code 是否可用
    claude = subprocess.run(["claude", "--version"], capture_output=True)
    if claude.returncode != 0:
        print("⚠️  Claude Code 未安装，跳过 obsidian-skills 精修")
        print("   提示: 手动运行 `claude` 进入 Vault 后执行精修指令")
        return True

    # 生成一个非交互式的精修指令脚本
    refine_commands = """# 这是 unified-obsidian-knowledge 自动生成的精修指令
# 请在 Claude Code 中粘贴执行：

请对 Vault 中的知识库进行批量精修：

1. 检查 Knowledge/ 下所有状态为 inbox 的笔记
2. 为每个领域（计算力学与有限元/软件工程与架构/人工智能与LLM/工程仿真自动化/知识管理与工具链）
   生成或更新 MOC (Map of Content)
3. 检查 Projects/ 下的项目笔记，补充缺失的链接
4. 如果某个项目下对话记录超过 5 篇，建议生成 Canvas 关系图
5. 更新所有笔记的 frontmatter status 从 inbox → refined

完成后报告处理了多少篇笔记。
"""
    print(refine_commands)
    return True


def main():
    parser = argparse.ArgumentParser(description="Unified Knowledge Pipeline")
    parser.add_argument("--config", "-c", default=str(CONFIG_PATH), help="配置文件路径")
    parser.add_argument("--stage", "-s", choices=["refinery", "deepener", "sync", "all"], default="all", help="执行阶段")
    parser.add_argument("--dry-run", "-n", action="store_true", help="预览模式")
    parser.add_argument("--no-patch", action="store_true", help="不 patch legacy 脚本")
    args = parser.parse_args()

    # 1. 加载配置
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}", file=sys.stderr)
        sys.exit(1)

    config = load_config(config_path)
    print(f"✅ 配置加载: {config_path}")

    # 2. 设置环境
    setup_env(config)
    vault = os.environ["UNIFIED_VAULT_OUTPUT"]

    # 3. 准备 legacy 脚本
    if args.no_patch:
        refinery_script = REFINERY_SCRIPT
        deepener_script = DEEPENER_SCRIPT
    else:
        refinery_script = patch_legacy_refinery()
        deepener_script = patch_legacy_deepener(vault)

    # 4. 执行阶段
    success = True
    stages = config.get("stages", {})

    if args.stage in ("refinery", "all") and stages.get("refinery", True):
        if args.dry_run:
            # 给 legacy 脚本传 --dry-run
            # 注意：legacy 脚本本身支持 --dry-run
            result = subprocess.run(
                [sys.executable, str(refinery_script), "--dry-run"],
                check=False, timeout=300
            )
            success = success and (result.returncode == 0)
        else:
            success = success and run_stage(refinery_script, "Knowledge Refinery (对话精炼)")

    if args.stage in ("deepener", "all") and stages.get("deepener", True):
        if deepener_script and deepener_script.exists():
            success = success and run_stage(deepener_script, "Knowledge Deepener (知识深化)")
        else:
            print("⚠️  knowledge_deepener_v2.py 不存在，跳过深化阶段")

    if args.stage in ("sync", "all") and stages.get("obsidian_sync", True):
        success = success and run_obsidian_sync(vault, config)

    # 5. 清理临时文件
    if not args.no_patch:
        for temp in [BASE / ".knowledge_refinery_patched.py", BASE / ".knowledge_deepener_patched.py"]:
            if temp.exists():
                temp.unlink()

    # 6. 总结
    print(f"\n{'='*60}")
    print("📊 管线执行完成")
    print(f"{'='*60}")
    print(f"Vault: {vault}")
    print(f"状态: {'✅ 成功' if success else '⚠️ 部分失败'}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

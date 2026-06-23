import re
from pathlib import Path


# 中文说明：
# 这里维护一个最小错误模式表。
# 后续你可以持续扩展，比如增加：
# element distortion、time step too small、license error 等。
ERROR_PATTERNS = {
    "singular_matrix": {
        "pattern": r"singular\s+matrix",
        "title": "刚度矩阵奇异",
        "description": "通常表示模型存在刚体位移、约束不足、单元失效或连接异常。",
    },
    "convergence_failed": {
        "pattern": r"convergence\s+failed",
        "title": "非线性迭代不收敛",
        "description": "通常与接触、材料非线性、加载步长过大或初始状态不合理有关。",
    },
    "contact_penetration": {
        "pattern": r"contact\s+penetration",
        "title": "接触穿透",
        "description": "通常与接触刚度、初始间隙、网格质量或接触定义设置有关。",
    },
    "license_error": {
        "pattern": r"license manager error|ansysli exited|checkout failed",
        "title": "许可证错误",
        "description": "通常表示许可证服务不可达、许可证不足，或许可证端口文件/环境配置异常。",
    },
}


def load_log_text(log_path: str | Path) -> str:
    """读取日志文件内容。"""
    path = Path(log_path)
    return path.read_text(encoding="utf-8", errors="replace")


def _build_snippet(log_text: str, start_index: int, window: int = 120) -> str:
    """截取错误附近的日志片段，方便后续分析。"""
    snippet_start = max(0, start_index - window)
    snippet_end = min(len(log_text), start_index + window)
    return log_text[snippet_start:snippet_end].strip()


def detect_errors(log_text: str) -> list[dict]:
    """检测日志中的已知错误。"""
    detected: list[dict] = []

    # 中文说明：
    # 使用忽略大小写的正则匹配，尽量兼容不同软件输出格式。
    for error_code, config in ERROR_PATTERNS.items():
        matches = list(re.finditer(config["pattern"], log_text, flags=re.IGNORECASE))

        for match in matches:
            detected.append(
                {
                    "error_code": error_code,
                    "title": config["title"],
                    "description": config["description"],
                    "matched_text": match.group(0),
                    "snippet": _build_snippet(log_text, match.start()),
                }
            )

    return detected

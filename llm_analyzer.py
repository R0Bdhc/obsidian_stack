import os
import time
from typing import Any

from openai import OpenAI


class LLMAnalyzer:
    """负责 LLM 分析，并在失败时回退到本地规则分析。"""

    def __init__(self) -> None:
        self.provider = "deepseek" if os.getenv("DEEPSEEK_API_KEY") else "openai"
        self.api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url) if self.api_key else None
        self._health_cache_ttl_seconds = 300
        self._last_health_check_at = 0.0
        self._last_health_status: dict[str, Any] | None = None

    def is_available(self) -> bool:
        return self.client is not None

    def get_status(self, force_refresh: bool = False) -> dict[str, Any]:
        """返回 LLM 当前是否已配置以及是否可连通。"""
        if self.client is None:
            return {
                "configured": False,
                "provider": self.provider,
                "model": self.model,
                "base_url": self.base_url,
                "reachable": False,
                "checked_at": None,
                "message": "未配置 LLM API Key，系统将使用本地规则分析。",
            }

        now = time.time()
        if (
            not force_refresh
            and self._last_health_status is not None
            and now - self._last_health_check_at < self._health_cache_ttl_seconds
        ):
            return self._last_health_status

        status: dict[str, Any] = {
            "configured": True,
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "reachable": False,
            "checked_at": int(now),
        }

        try:
            self.client.models.list()
            status["reachable"] = True
            status["message"] = "LLM 已配置，且当前可正常连通。"
        except Exception as exc:
            status["error"] = str(exc)
            status["message"] = "LLM 已配置，但当前不可连通，系统将回退到本地规则分析。"

        self._last_health_check_at = now
        self._last_health_status = status
        return status

    def analyze(self, source_name: str, log_text: str, detected_errors: list[dict]) -> dict:
        if not detected_errors:
            return {
                "mode": "rule_based",
                "summary": "日志中未检测到预设错误关键词。",
                "possible_causes": ["当前规则库中未发现明显异常。"],
                "suggestions": ["建议继续扩展错误规则，或人工检查完整日志上下文。"],
            }

        if self.client is None:
            return self._fallback_analysis(detected_errors)

        try:
            result = self._analyze_with_llm(source_name, log_text, detected_errors)
            now = time.time()
            self._last_health_check_at = now
            self._last_health_status = {
                "configured": True,
                "provider": self.provider,
                "model": self.model,
                "base_url": self.base_url,
                "reachable": True,
                "checked_at": int(now),
                "message": "最近一次 LLM 调用成功。",
            }
            return result
        except Exception as exc:
            fallback_result = self._fallback_analysis(detected_errors)
            fallback_result["mode"] = "fallback_after_llm_error"
            fallback_result["llm_error"] = str(exc)

            now = time.time()
            self._last_health_check_at = now
            self._last_health_status = {
                "configured": True,
                "provider": self.provider,
                "model": self.model,
                "base_url": self.base_url,
                "reachable": False,
                "checked_at": int(now),
                "message": "最近一次 LLM 调用失败，系统已回退到本地规则分析。",
                "error": str(exc),
            }
            return fallback_result

    def _analyze_with_llm(self, source_name: str, log_text: str, detected_errors: list[dict]) -> dict:
        prompt = self._build_prompt(source_name, log_text, detected_errors)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        text_result = (response.choices[0].message.content or "").strip()

        return {
            "mode": self.provider,
            "model": self.model,
            "summary": f"已使用 {self.provider} 生成错误分析。",
            "raw_analysis": text_result,
            "possible_causes": [],
            "suggestions": [],
        }

    def _build_prompt(self, source_name: str, log_text: str, detected_errors: list[dict]) -> str:
        error_lines = []
        for item in detected_errors:
            error_lines.append(
                f"- 错误代码：{item['error_code']}\n"
                f"  标题：{item['title']}\n"
                f"  描述：{item['description']}\n"
                f"  日志片段：{item['snippet']}"
            )

        joined_errors = "\n".join(error_lines)
        truncated_log_text = log_text[:4000]

        return f"""
你是一名 ANSYS 结构与非线性分析专家，请根据日志帮助工程师定位问题。
请使用中文输出，并严格按下面格式回答：
1. 问题概述
2. 可能原因
3. 修改建议
4. 建议优先排查顺序

日志来源：{source_name}

已检测错误：
{joined_errors}

日志全文片段：
{truncated_log_text}
""".strip()

    def _fallback_analysis(self, detected_errors: list[dict]) -> dict:
        possible_causes: list[str] = []
        suggestions: list[str] = []

        error_codes = {item["error_code"] for item in detected_errors}

        if "singular_matrix" in error_codes:
            possible_causes.append("模型约束不足，存在刚体位移自由度。")
            possible_causes.append("单元连接不连续，或关键部位出现悬空节点。")
            suggestions.append("优先检查边界条件、耦合关系和接触连接是否完整。")
            suggestions.append("检查模型是否存在未约束的部件或失效单元。")

        if "convergence_failed" in error_codes:
            possible_causes.append("非线性过强，当前载荷步或子步设置过大。")
            possible_causes.append("材料参数、接触参数或初始状态设置不合理。")
            suggestions.append("减小载荷步长，增加子步数，必要时启用自动时间步。")
            suggestions.append("检查接触刚度、摩擦参数和材料本构输入是否稳定。")

        if "contact_penetration" in error_codes:
            possible_causes.append("接触初始闭合状态不合理，或接触刚度设置偏弱。")
            possible_causes.append("接触面网格过粗，导致接触搜索与法向响应不稳定。")
            suggestions.append("检查初始接触状态、法向刚度和接触算法设置。")
            suggestions.append("局部加密接触区网格，并检查接触/目标面方向。")

        return {
            "mode": "rule_based",
            "summary": "未启用 LLM，已使用本地规则生成基础分析。",
            "possible_causes": self._deduplicate(possible_causes),
            "suggestions": self._deduplicate(suggestions),
        }

    @staticmethod
    def _deduplicate(items: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []

        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)

        return result

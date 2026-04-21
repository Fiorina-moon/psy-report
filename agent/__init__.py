"""报告生成：loaders（配置 / 计分结果 / JSON 工具）+ report（提示词与 LLM）。"""

from agent.loaders import AppConfig, LLMConfig, load_config, load_scored_cohort
from agent.report import ChatResult, build_system_prompt, build_user_prompt, chat_completion

__all__ = [
    "AppConfig",
    "LLMConfig",
    "ChatResult",
    "load_config",
    "load_scored_cohort",
    "build_system_prompt",
    "build_user_prompt",
    "chat_completion",
]

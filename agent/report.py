from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI

from agent.loaders import LLMConfig

USER_MARKERS = {
    "REPORT_TEMPLATE": "<<<REPORT_TEMPLATE>>>",
    "SCORE_PAYLOAD": "<<<SCORE_PAYLOAD>>>",
}

def build_system_prompt(system_prompt_path: Path) -> str:
    return system_prompt_path.read_text(encoding="utf-8").strip()


def build_user_prompt(
    user_prompt_path: Path,
    report_template: str,
    score_payload_json: str,
) -> str:
    text = user_prompt_path.read_text(encoding="utf-8")
    if USER_MARKERS["REPORT_TEMPLATE"] not in text:
        raise ValueError(f"user 提示词中缺少占位符 {USER_MARKERS['REPORT_TEMPLATE']}")
    if USER_MARKERS["SCORE_PAYLOAD"] not in text:
        raise ValueError(f"user 提示词中缺少占位符 {USER_MARKERS['SCORE_PAYLOAD']}")
    text = text.replace(USER_MARKERS["REPORT_TEMPLATE"], report_template, 1)
    text = text.replace(USER_MARKERS["SCORE_PAYLOAD"], score_payload_json, 1)
    return text


@dataclass
class ChatResult:
    content: str
    model: str


def chat_completion(
    llm: LLMConfig,
    system_prompt: str,
    user_prompt: str,
) -> ChatResult:
    if not llm.api_key:
        raise RuntimeError(
            "未设置环境变量 PARATERA_API_KEY（或值为空），无法调用模型。"
            "可先使用 main.py --dry-run 查看拼装后的提示词。"
        )
    if not llm.model:
        raise RuntimeError(
            "未设置环境变量 PARATERA_MODEL。"
            "可先使用 main.py --dry-run 查看拼装后的提示词。"
        )

    client = OpenAI(api_key=llm.api_key, base_url=llm.base_url)
    kwargs: dict = dict(
        model=llm.model,
        temperature=llm.temperature,
        max_tokens=llm.max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    if llm.response_format_json:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    choice = resp.choices[0].message
    content = choice.content or ""
    return ChatResult(content=content, model=resp.model or llm.model)

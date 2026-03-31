"""Inquiry extraction via OpenAI-compatible API (Ollama / cloud) + Pydantic validation."""

from __future__ import annotations

import logging

from openai import APIError, OpenAI
from openai.types.chat import ChatCompletion
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.schemas.inquiry import InquiryExtraction

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You extract structured data from customer inquiry messages.
The message may be messy, informal, or in any language—use only what appears in the text.
Reply with a single JSON object. No markdown fences, no extra commentary.
Required keys (snake_case), each string or null:
- customer_name: how the customer identifies themselves; null if unknown
- contact: phone, email, LINE, WeChat, etc.—one string; null if none
- estimated_budget: any budget/price/quote-related phrase; copy or paraphrase from the text; null only if there is no price/budget hint at all

Example shape (format only):
{"customer_name":"Jane Doe","contact":"jane@example.com","estimated_budget":"under $2k"}
"""
USER_SUFFIX = """
---
Extract from the message above. Include all three keys. Prefer filling estimated_budget when any budget/price wording exists.
"""


def _strip_json_fences(raw: str) -> str:
    s = raw.strip()
    if not s.startswith("```"):
        return s
    lines = s.splitlines()
    if not lines:
        return s
    lines = lines[1:]
    while lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _parse_inquiry_json(text: str) -> InquiryExtraction:
    cleaned = _strip_json_fences(text)
    try:
        return InquiryExtraction.model_validate_json(cleaned)
    except ValidationError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end > start:
            snippet = cleaned[start : end + 1]
            return InquiryExtraction.model_validate_json(snippet)
        raise


class InquiryExtractService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._openai: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._openai is None:
            key = self._settings.openai_api_key or "ollama"
            self._openai = OpenAI(
                base_url=self._settings.llm_base_url.rstrip("/"),
                api_key=key,
                timeout=120.0,
            )
        return self._openai

    def extract_from_text(self, raw_inquiry: str) -> InquiryExtraction:
        """Extract fields from raw inquiry text; validate with Pydantic."""
        text = raw_inquiry.strip()
        if not text:
            return InquiryExtraction()

        user_content = (
            "Customer inquiry text (extract fields, JSON only):\n\n" + text + USER_SUFFIX
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

        completion = self._chat_create(messages, use_json_mode=True)
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("Empty model response (choices[0].message.content)")

        try:
            return _parse_inquiry_json(content)
        except ValidationError as e:
            logger.warning("JSON parse failed, retrying without JSON mode: %s", e)
            completion2 = self._chat_create(messages, use_json_mode=False)
            content2 = completion2.choices[0].message.content
            if not content2:
                raise ValueError("Empty model response on retry") from e
            return _parse_inquiry_json(content2)

    def _chat_create(
        self,
        messages: list[dict[str, str]],
        *,
        use_json_mode: bool,
    ) -> ChatCompletion:
        kwargs: dict = {
            "model": self._settings.llm_model,
            "messages": messages,
            "temperature": 0.2,
        }
        if use_json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            return self.client.chat.completions.create(**kwargs)
        except APIError as err:
            if use_json_mode:
                logger.info("JSON mode unsupported or failed, retrying without: %s", err)
                kwargs.pop("response_format", None)
                return self.client.chat.completions.create(**kwargs)
            raise

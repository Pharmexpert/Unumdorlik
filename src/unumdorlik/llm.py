"""LLM backends. Stack A/B: `claude_cli` (Claude Code subscription, `claude -p`) or `gemini` (free tier).
`anthropic` (API) is kept for Stack C / later."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass

JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


class LLMError(RuntimeError):
    pass


@dataclass
class LLMResult:
    text: str
    provider: str
    model: str

    def json(self) -> dict:
        txt = self.text.strip()
        txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt, flags=re.DOTALL)
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            m = JSON_BLOCK.search(txt)
            if not m:
                raise LLMError("Javobda JSON topilmadi") from None
            return json.loads(m.group(0))


def _claude_cli(system: str, user: str, model: str, timeout: int) -> LLMResult:
    exe = shutil.which("claude")
    if not exe:
        raise LLMError("`claude` CLI topilmadi (Claude Code o'rnatilmagan yoki PATH da yo'q)")
    cmd = [exe, "-p", "--output-format", "text", "--model", model]
    if system:
        cmd += ["--append-system-prompt", system]
    proc = subprocess.run(cmd, input=user, text=True, capture_output=True, timeout=timeout, check=False)
    if proc.returncode != 0:
        raise LLMError(f"claude -p xato ({proc.returncode}): {proc.stderr.strip()[:500]}")
    return LLMResult(text=proc.stdout, provider="claude_cli", model=model)


def _gemini(system: str, user: str, model: str, timeout: int) -> LLMResult:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise LLMError("GEMINI_API_KEY o'rnatilmagan")
    try:
        from google import genai
        from google.genai import types
    except ImportError as e:
        raise LLMError("google-genai o'rnatilmagan: uv sync --extra llm") from e
    client = genai.Client(api_key=key)
    resp = client.models.generate_content(
        model=model,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system or None,
            response_mime_type="application/json",
            temperature=0.7,
        ),
    )
    return LLMResult(text=resp.text or "", provider="gemini", model=model)


def _anthropic(system: str, user: str, model: str, timeout: int) -> LLMResult:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise LLMError("ANTHROPIC_API_KEY o'rnatilmagan")
    try:
        import anthropic
    except ImportError as e:
        raise LLMError("anthropic o'rnatilmagan: uv sync --extra llm") from e
    client = anthropic.Anthropic(api_key=key, timeout=timeout)
    msg = client.messages.create(
        model=model,
        max_tokens=16000,
        system=system or anthropic.NOT_GIVEN,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    return LLMResult(text=text, provider="anthropic", model=model)


BACKENDS = {"claude_cli": _claude_cli, "gemini": _gemini, "anthropic": _anthropic}
DEFAULT_MODELS = {
    "claude_cli": "claude-opus-5-5",
    "gemini": "gemini-2.5-flash",
    "anthropic": "claude-sonnet-5-5",
}


def complete(provider: str, system: str, user: str, model: str | None = None, timeout: int = 900) -> LLMResult:
    if provider not in BACKENDS:
        raise LLMError(f"Noma'lum provider: {provider}")
    model = model or DEFAULT_MODELS[provider]
    return BACKENDS[provider](system, user, model, timeout)


def complete_json(provider: str, system: str, user: str, model: str | None = None, retries: int = 1) -> dict:
    last: Exception | None = None
    for _ in range(retries + 1):
        try:
            return complete(provider, system, user, model).json()
        except (LLMError, json.JSONDecodeError) as e:
            last = e
            user = user + "\n\nIMPORTANT: Return ONLY valid JSON. No prose, no code fences."
    raise LLMError(f"JSON olinmadi ({retries + 1} urinish): {last}")

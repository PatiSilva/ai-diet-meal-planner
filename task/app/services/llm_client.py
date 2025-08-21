# app/services/llm_client.py
import os
import json
import re
from typing import Any, Dict, Optional

from dotenv import load_dotenv
load_dotenv()

try:
    # pip install groq
    from groq import Groq
except Exception:
    Groq = None


class LLMClient:
    """
    Wrapper for Groq chat API that extracts a JSON object even if the model
    adds prose or code fences. Never raises on parse failure; returns {} so
    callers can fallback.
    """

    def __init__(self, model: Optional[str] = None):
        # Accept either GROQ_API_KEY or LLM_API_KEY (from your .env)
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY")
        if not api_key:
            raise RuntimeError("No API key found. Set GROQ_API_KEY or LLM_API_KEY.")
        if Groq is None:
            raise RuntimeError("Groq SDK is not installed. Run: pip install groq")

        self.client = Groq(api_key=api_key)
        self.model = model or os.getenv("GROQ_MODEL", "llama3-8b-8192")
        self.debug = os.getenv("LLM_DEBUG", "0") == "1"

    def call_model_json(self, prompt: str) -> Dict[str, Any]:
        """
        Returns a parsed JSON dict from the model output:
          1) try json.loads on full text
          2) try fenced ```json { ... } ```
          3) brace-match the first { ... }
          4) return {} if all fail
        """
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                # response_format={"type": "json_object"},  # enable if supported in your SDK
            )
        except Exception as e:
            print(f"🚨 Unexpected error during Groq API call: {e}")
            return {}

        try:
            content = resp.choices[0].message.content
        except Exception as e:
            print(f"🚨 Could not read model content: {e}")
            return {}

        if self.debug:
            preview = content[:300].replace("\n", " ")
            print(f"📦 RAW (preview): {preview}...")

        # 1) direct parse
        obj = self._try_json(content)
        if obj is not None:
            return obj

        # 2) fenced ```json ... ```
        fenced = self._extract_fenced_json(content)
        obj = self._try_json(fenced) if fenced else None
        if obj is not None:
            return obj

        # 3) brace-matched first object
        brace_block = self._extract_json_block(content)
        obj = self._try_json(brace_block) if brace_block else None
        if obj is not None:
            return obj

        if self.debug:
            print("⚠️ call_model_json: returning empty dict after parse attempts.")
        return {}

    # ---------- helpers ----------

    def _try_json(self, text: Optional[str]) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        try:
            val = json.loads(text)
            return val if isinstance(val, dict) else None
        except Exception:
            return None

    def _extract_fenced_json(self, text: str) -> Optional[str]:
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
        return m.group(1) if m else None

    def _extract_json_block(self, text: str) -> Optional[str]:
        start = text.find("{")
        if start == -1:
            return None
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
        return None


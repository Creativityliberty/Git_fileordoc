from __future__ import annotations
from typing import Optional, List
import os, json, time, hashlib
import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

class LLMClient:
    def __init__(self, cache_dir: str = ".fuzzsuite_cache"):
        self.cache_dir = cache_dir

    def _headers(self) -> dict:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("Missing OPENROUTER_API_KEY")
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("OPENROUTER_REFERER", "http://localhost"),
            "X-Title": os.getenv("OPENROUTER_TITLE", "FuzzSuite"),
        }

    def _cache_key(self, model: str, prompt: str) -> str:
        h = hashlib.sha256()
        h.update(model.encode("utf-8"))
        h.update(prompt.encode("utf-8"))
        return h.hexdigest()

    def _cache_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, key + ".txt")

    def _load_cache(self, key: str) -> Optional[str]:
        p = self._cache_path(key)
        if os.path.exists(p):
            try:
                return open(p, "r", encoding="utf-8").read()
            except Exception:
                return None
        return None

    def _save_cache(self, key: str, value: str) -> None:
        os.makedirs(self.cache_dir, exist_ok=True)
        with open(self._cache_path(key), "w", encoding="utf-8") as f:
            f.write(value)

    def chat_once(self, prompt: str, model: str, timeout_s: int = 60) -> str:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "stream": False,
        }
        r = requests.post(
            OPENROUTER_URL,
            headers=self._headers(),
            data=json.dumps(payload),
            timeout=timeout_s,
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

    def summarize(
        self,
        text: str,
        models: List[str],
        retry_max: int = 3,
        retry_backoff_s: float = 1.5,
        timeout_s: int = 60,
        max_chars: int = 600,
    ) -> Optional[str]:
        if not models:
            return None
        prompt = ("Résume ce contenu pour documentation technique (1–3 phrases).\n\n" + text).strip()
        for model in models:
            key = self._cache_key(model, prompt)
            cached = self._load_cache(key)
            if cached:
                return cached
            last = None
            for attempt in range(retry_max):
                try:
                    out = self.chat_once(prompt, model=model, timeout_s=timeout_s)
                    out = " ".join(out.split())
                    if len(out) > max_chars:
                        out = out[:max_chars].rstrip() + "…"
                    self._save_cache(key, out)
                    return out
                except Exception as e:
                    last = e
                    time.sleep(retry_backoff_s * (2 ** attempt))
            # try next model
            _ = last
        return None

import os, json, re


def call_ai(prompt: str, max_tokens: int = 3000) -> str:
    """Universal AI caller — Anthropic first, Gemini fallback."""
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            resp = client.messages.create(
                model="claude-sonnet-4-6", max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return resp.content[0].text.strip()
        except Exception as e:
            if "credit" not in str(e).lower() and "balance" not in str(e).lower():
                raise

    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        import requests
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}",
            json={"contents": [{"parts": [{"text": prompt}]}],
                  "generationConfig": {"maxOutputTokens": max_tokens}},
            timeout=60
        )
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    raise Exception("No AI API key available")

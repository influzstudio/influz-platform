import os


def call_ai(prompt: str, max_tokens: int = 3000) -> str:
    ak = os.getenv("ANTHROPIC_API_KEY")
    if ak:
        try:
            import anthropic
            c = anthropic.Anthropic(api_key=ak)
            r = c.messages.create(model="claude-sonnet-4-6", max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}])
            return r.content[0].text.strip()
        except Exception as e:
            if "credit" not in str(e).lower(): raise

    if os.getenv("GEMINI_API_KEY"):
        import google.genai as genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        return client.models.generate_content(model="gemini-2.0-flash", contents=prompt).text.strip()

    raise Exception("No AI API key available")

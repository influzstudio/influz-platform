import os, json, re
from datetime import date, timedelta


def _call_ai(prompt: str, max_tokens: int = 8000) -> str:
    """Call AI — tries Anthropic first, falls back to Gemini."""
    # Try Anthropic
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
            if "credit" in str(e).lower() or "balance" in str(e).lower():
                pass  # Fall through to Gemini
            else:
                raise

    # Try Gemini (free)
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            import requests
            resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}",
                json={"contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"maxOutputTokens": max_tokens}},
                timeout=60
            )
            resp.raise_for_status()
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            raise Exception(f"Gemini error: {e}")

    raise Exception("No AI API key configured")


def generate_social_calendar(business_name, niche, brand_voice, goals, city, start_date, num_posts=16):
    try:
        prompt = f"""Generate a {num_posts}-post social media content calendar for:
Business: {business_name}
Industry/Niche: {niche}
Brand Voice: {brand_voice}
Goals: {goals}
City: {city}
Start date: {start_date}
Period: 60 days

Return ONLY a valid JSON array with exactly {num_posts} objects. Each object must have:
- post_date: YYYY-MM-DD (spread across 60 days)
- post_type: one of Static, Reel, Carousel, Story, UGC
- platforms: list like ["instagram"] or ["instagram","facebook"]
- topic: specific creative angle (max 10 words)
- cover_text: bold headline for image (max 8 words)
- image_text: supporting visual copy (max 12 words)
- caption: full ready-to-post caption with emojis, CTA, 8-10 hashtags
- reference_note: visual direction for designer
- content_angle: the specific hook

Make all content specific to {business_name} and {niche}. No generic placeholders."""

        raw = _call_ai(prompt)
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
        items = json.loads(raw)
        if isinstance(items, list) and len(items) > 0:
            return items[:num_posts]
    except Exception as e:
        print(f"AI generation error: {e}")
    return _fallback(start_date, num_posts, business_name)


def _fallback(start_date, num, name):
    types = ["Static","Reel","Carousel","Story","UGC"]
    return [{"post_date": (start_date+timedelta(days=i*2)).isoformat(),
             "post_type": types[i%5], "platforms": ["instagram"],
             "topic": f"Content idea {i+1}", "cover_text": f"Post {i+1}",
             "image_text": "", "caption": f"Sample caption for {name}. #socialmedia",
             "reference_note": "", "content_angle": ""} for i in range(num)]

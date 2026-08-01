import os, json, re
from datetime import date, timedelta


def _call_gemini(prompt, max_tokens=8000):
    """Call Gemini using the official google-genai SDK which handles AQ. keys."""
    import google.genai as genai
    key = os.getenv("GEMINI_API_KEY", "")
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text.strip()


def generate_social_calendar(business_name, niche, brand_voice, goals, city, start_date, num_posts=16):
    prompt = f"""Generate a {num_posts}-post social media content calendar for:
Business: {business_name} | Niche: {niche} | Voice: {brand_voice} | Goals: {goals} | City: {city}
Start: {start_date} | Period: 60 days

Return ONLY a JSON array with {num_posts} objects, each having:
post_date (YYYY-MM-DD), post_type (Static/Reel/Carousel/Story/UGC), platforms (list),
topic (specific, max 10 words), cover_text (headline, max 8 words),
image_text (supporting copy, max 12 words), caption (full with emojis+hashtags),
reference_note (visual direction), content_angle (hook)

All content must be specific to {business_name} and {niche}. No placeholders."""

    # Try Anthropic first
    ak = os.getenv("ANTHROPIC_API_KEY")
    if ak:
        try:
            import anthropic
            c = anthropic.Anthropic(api_key=ak)
            r = c.messages.create(model="claude-sonnet-4-6", max_tokens=12000,
                messages=[{"role": "user", "content": prompt}])
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", r.content[0].text.strip())
            items = json.loads(raw)
            if isinstance(items, list) and items: return items[:num_posts]
        except Exception as e:
            if "credit" not in str(e).lower(): print(f"Anthropic error: {e}")

    # Try Gemini
    if os.getenv("GEMINI_API_KEY"):
        try:
            raw = _call_gemini(prompt)
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
            items = json.loads(raw)
            if isinstance(items, list) and items: return items[:num_posts]
        except Exception as e:
            print(f"Gemini error: {e}")

    return _fallback(start_date, num_posts, business_name)


def _fallback(start_date, num, name):
    types = ["Static","Reel","Carousel","Story","UGC"]
    return [{"post_date": (start_date+timedelta(days=i*2)).isoformat(),
             "post_type": types[i%5], "platforms": ["instagram"],
             "topic": f"Content idea {i+1}", "cover_text": f"Post {i+1}",
             "image_text": "", "caption": f"Sample caption for {name}. #socialmedia",
             "reference_note": "", "content_angle": ""} for i in range(num)]

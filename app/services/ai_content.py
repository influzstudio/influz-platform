import os, json, re
from datetime import date, timedelta


def generate_social_calendar(business_name, niche, brand_voice, goals, city, start_date, num_posts=16):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback(start_date, num_posts, business_name)
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=12000,
            messages=[{"role": "user", "content": f"""Generate a {num_posts}-post social media content calendar for:
Business: {business_name}
Industry/Niche: {niche}
Brand Voice: {brand_voice}
Goals: {goals}
City: {city}
Start date: {start_date}
Period: 60 days

Return ONLY a valid JSON array with exactly {num_posts} objects. Each object must have:
- post_date: YYYY-MM-DD (spread across 60 days, realistic posting schedule)
- post_type: one of Static, Reel, Carousel, Story, UGC
- platforms: list like ["instagram"] or ["instagram","facebook"] or ["linkedin"]
- topic: specific creative angle (max 10 words, NOT generic)
- cover_text: bold headline text for the image (max 8 words)
- image_text: supporting visual copy (max 12 words)
- caption: full ready-to-post caption with emojis, CTA, and 8-10 hashtags
- reference_note: visual direction note for the designer
- content_angle: the specific hook/angle

Make content specific to the business niche. No generic placeholder text."""}]
        )
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", resp.content[0].text.strip())
        items = json.loads(raw)
        if isinstance(items, list) and len(items) > 0:
            return items[:num_posts]
    except Exception as e:
        print(f"AI generation error: {e}")
    return _fallback(start_date, num_posts, business_name)


def _fallback(start_date, num, name):
    types = ["Static","Reel","Carousel","Story","UGC"]
    return [{"post_date": (start_date+timedelta(days=i*2)).isoformat(), "post_type": types[i%5],
             "platforms": ["instagram"], "topic": f"Content idea {i+1}", "cover_text": f"Post {i+1}",
             "image_text": "", "caption": f"Sample caption for {name}. #socialmedia",
             "reference_note": "", "content_angle": ""} for i in range(num)]

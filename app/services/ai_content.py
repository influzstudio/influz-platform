import os, json, re
from datetime import date, timedelta
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_social_calendar(business_name, niche, brand_voice, goals, city, start_date, num_posts=16):
    if not os.getenv("ANTHROPIC_API_KEY"):
        return _fallback(start_date, num_posts, business_name)
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=12000,
            messages=[{"role": "user", "content": f"""Generate a {num_posts}-post social media calendar for:
Business: {business_name} | Industry: {niche} | Voice: {brand_voice} | Goals: {goals} | City: {city}
Start date: {start_date} | Period: 60 days

Return ONLY a JSON array with objects having: post_date (YYYY-MM-DD), post_type (Static/Reel/Carousel/Story/UGC), platforms (list), topic, cover_text, image_text, caption (with hashtags), reference_note, content_angle"""}]
        )
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", resp.content[0].text.strip())
        items = json.loads(raw)
        return items[:num_posts] if isinstance(items, list) else _fallback(start_date, num_posts, business_name)
    except:
        return _fallback(start_date, num_posts, business_name)

def _fallback(start_date, num, name):
    types = ["Static","Reel","Carousel","Story","UGC"]
    return [{"post_date": (start_date+timedelta(days=i*2)).isoformat(), "post_type": types[i%5],
             "platforms": ["instagram"], "topic": f"Content idea {i+1}", "cover_text": f"Post {i+1}",
             "image_text": "", "caption": f"Sample caption for {name}. #socialmedia",
             "reference_note": "", "content_angle": ""} for i in range(num)]

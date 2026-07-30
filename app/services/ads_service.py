from app.services.ai_base import call_ai
import os, json, re



def generate_ad_assets(business_name, industry, campaign_type, platform, objective, brand_voice):
    if not os.getenv("ANTHROPIC_API_KEY"):
        return {"assets": [{"headline": f"Discover {business_name}", "description": f"Your trusted {industry} partner.",
                             "cta": "Learn More", "creative_brief": "Clean brand image with logo"}]}
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = client.messages.create(model="claude-sonnet-4-6", max_tokens=3000,
            messages=[{"role": "user", "content": f"""Generate 3 ad copy variants for:
Business: {business_name} | Industry: {industry} | Platform: {platform}
Campaign type: {campaign_type} | Objective: {objective} | Voice: {brand_voice}

Return JSON: {{"assets": [{{"headline": str, "description": str, "cta": str, "creative_brief": str}}]}}"""}])
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)
        return json.loads(raw)
    except:
        return {"assets": []}

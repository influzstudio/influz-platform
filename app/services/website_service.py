from app.services.ai_base import call_ai
import os, json, re



def audit_page(url, content, business_name, industry):
    if not os.getenv("ANTHROPIC_API_KEY"):
        return {"ux_score": 6.5, "issues": ["Missing clear CTA", "No trust signals"],
                "recommendations": ["Add testimonials", "Improve headline"],
                "detailed_recommendations": [{"category": "ux", "priority": "high",
                "title": "Add clear CTA", "description": "Add a prominent call-to-action button",
                "before": "Contact us", "after": "Book Free Consultation →"}]}
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = client.messages.create(model="claude-sonnet-4-6", max_tokens=3000,
            messages=[{"role": "user", "content": f"""Audit this webpage for UX and conversion:
URL: {url} | Business: {business_name} | Industry: {industry}
Content: {content[:1500]}

Return JSON: {{"ux_score": float 0-10, "issues": [str], "recommendations": [str],
"detailed_recommendations": [{{"category": "ux|content|cro|seo", "priority": "high|medium|low",
"title": str, "description": str, "before": str, "after": str}}]}}"""}])
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)
        return json.loads(raw)
    except:
        return {"ux_score": 0.0, "issues": [], "recommendations": [], "detailed_recommendations": []}

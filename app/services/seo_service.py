import os, json, re
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_keyword_clusters(business_name, industry, city, seed_keywords=""):
    if not os.getenv("ANTHROPIC_API_KEY"):
        return [{"keyword": f"{industry} services", "intent": "transactional", "cluster": "services", "priority": "high"}]
    try:
        resp = client.messages.create(model="claude-sonnet-4-6", max_tokens=4000,
            messages=[{"role": "user", "content": f"""Generate 20 SEO keywords for:
Business: {business_name} | Industry: {industry} | City: {city} | Seeds: {seed_keywords}

Return ONLY JSON array: [{{"keyword": str, "intent": "informational|transactional|navigational", "cluster": str, "priority": "high|medium|low"}}]"""}])
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", resp.content[0].text.strip())
        return json.loads(raw)
    except:
        return []

def audit_page(url, current_title, current_meta, page_content, business_name, industry):
    if not os.getenv("ANTHROPIC_API_KEY"):
        return {"suggested_title": f"{business_name} | {industry}", "suggested_meta": f"Discover {business_name}.",
                "suggested_h1": f"Welcome to {business_name}", "suggested_schema": "", "issues": ["No API key"]}
    try:
        resp = client.messages.create(model="claude-sonnet-4-6", max_tokens=2000,
            messages=[{"role": "user", "content": f"""Audit this page for SEO:
URL: {url} | Business: {business_name} | Industry: {industry}
Current title: {current_title} | Current meta: {current_meta}
Content: {page_content[:1000]}

Return JSON: {{"suggested_title": str, "suggested_meta": str, "suggested_h1": str, "suggested_schema": str, "issues": [str]}}"""}])
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", resp.content[0].text.strip())
        return json.loads(raw)
    except:
        return {"suggested_title": "", "suggested_meta": "", "suggested_h1": "", "suggested_schema": "", "issues": []}

import os, json, re



def generate_monthly_report(business_name, industry, total_posts, total_leads):
    if not os.getenv("ANTHROPIC_API_KEY"):
        return {"social_summary": f"Published {total_posts} posts across platforms.",
                "ads_summary": "Campaigns running.", "seo_summary": "Keywords tracked.",
                "overall_summary": f"Good month for {business_name}.",
                "next_actions": ["Increase posting frequency", "Launch retargeting campaign"]}
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = client.messages.create(model="claude-sonnet-4-6", max_tokens=2000,
            messages=[{"role": "user", "content": f"""Generate a monthly marketing report for:
Business: {business_name} | Industry: {industry}
Stats: {total_posts} social posts, {total_leads} leads this month

Return JSON: {{"social_summary": str, "ads_summary": str, "seo_summary": str,
"overall_summary": str, "next_actions": [str]}}"""}])
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", resp.content[0].text.strip())
        return json.loads(raw)
    except:
        return {"social_summary": "", "ads_summary": "", "seo_summary": "",
                "overall_summary": "", "next_actions": []}

import os
import json
import requests
from datetime import datetime

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# ─────────────────────────────────────────
# GROQ — Clustering & Kategorisasi
# ─────────────────────────────────────────
def groq_cluster_tools(tools: list) -> dict:
    if not GROQ_API_KEY:
        print("[Groq] No API key set")
        return {}

    # Ambil sample 30 tools untuk clustering
    sample = tools[:30]
    tools_text = "\n".join([
        f"- {t.get('name', '')}: {t.get('description', '')[:100]}"
        for t in sample
    ])

    prompt = f"""Analyze these AI tools and cluster them into categories.
Return ONLY valid JSON, no explanation.

Tools:
{tools_text}

Return this exact format:
{{
  "clusters": {{
    "category_name": ["tool1", "tool2"],
    "category_name2": ["tool3", "tool4"]
  }},
  "top_categories": ["cat1", "cat2", "cat3"],
  "emerging_niches": ["niche1", "niche2"]
}}"""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        # Parse JSON dari response
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
    except Exception as e:
        print(f"[Groq] Error: {e}")

    return {}

def groq_categorize_tool(tool: dict) -> str:
    if not GROQ_API_KEY:
        return "uncategorized"

    prompt = f"""Categorize this AI tool into ONE category.
Name: {tool.get('name', '')}
Description: {tool.get('description', '')[:200]}

Pick ONE from: writing, coding, image, video, audio, marketing, productivity, research, customer-service, data-analysis, other

Return ONLY the category word, nothing else."""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 10
        }
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=15)
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip().lower()
    except Exception as e:
        print(f"[Groq] Categorize error: {e}")
        return "uncategorized"

# ─────────────────────────────────────────
# GEMINI — Market Intelligence & Insights
# ─────────────────────────────────────────
def gemini_generate_insight(tools: list, stats: dict) -> dict:
    if not GEMINI_API_KEY:
        print("[Gemini] No API key set")
        return {}

    # Siapkan data ringkas
    top_tools = sorted(tools, key=lambda x: x.get("upvotes", 0), reverse=True)[:20]
    tools_summary = "\n".join([
        f"- {t.get('name','')}: {t.get('description','')[:80]} (upvotes: {t.get('upvotes',0)}, source: {t.get('source','')})"
        for t in top_tools
    ])

    sources_summary = json.dumps(stats.get("by_source", {}))

    prompt = f"""You are an AI market intelligence analyst.

Analyze this data about AI SaaS tools collected today:

STATS:
- Total tools tracked: {stats.get('total_tools', 0)}
- Sources: {sources_summary}

TOP TRENDING TOOLS:
{tools_summary}

Generate a market intelligence report. Return ONLY valid JSON:
{{
  "market_summary": "2-3 sentence overview of AI tool market right now",
  "top_trends": ["trend1", "trend2", "trend3"],
  "hot_categories": ["cat1", "cat2", "cat3"],
  "opportunities": ["opportunity for builders 1", "opportunity 2"],
  "notable_tools": ["tool1", "tool2", "tool3"],
  "insight_for_indonesian_market": "specific insight for Indonesian SME market"
}}"""

    try:
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 1000
            }
        }
        resp = requests.post(url, json=payload, timeout=30)
        data = resp.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]

        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
    except Exception as e:
        print(f"[Gemini] Error: {e}")

    return {}

def gemini_analyze_tool(tool: dict) -> dict:
    if not GEMINI_API_KEY:
        return {}

    prompt = f"""Analyze this AI tool briefly.
Name: {tool.get('name', '')}
Description: {tool.get('description', '')[:300]}
Source: {tool.get('source', '')}

Return ONLY valid JSON:
{{
  "target_user": "who is this for",
  "core_value": "main value proposition in one sentence",
  "market_fit_indonesia": "high/medium/low",
  "similar_tools": ["tool1", "tool2"],
  "monetization": "how it likely makes money"
}}"""

    try:
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 300}
        }
        resp = requests.post(url, json=payload, timeout=20)
        data = resp.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
    except Exception as e:
        print(f"[Gemini] Tool analysis error: {e}")
    return {}

# ─────────────────────────────────────────
# COMBINED — Run full AI analysis
# ─────────────────────────────────────────
def run_ai_analysis(tools: list, stats: dict) -> dict:
    print("\n[AI Engine] Starting analysis...")
    results = {
        "clusters": {},
        "market_insight": {},
        "generated_at": datetime.utcnow().isoformat()
    }

    print("[AI Engine] Running Groq clustering...")
    results["clusters"] = groq_cluster_tools(tools)

    print("[AI Engine] Running Gemini market insight...")
    results["market_insight"] = gemini_generate_insight(tools, stats)

    print("[AI Engine] Analysis complete")
    return results

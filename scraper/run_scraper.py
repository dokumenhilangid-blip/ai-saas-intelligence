import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.aitools_scraper import AitoolsScraper
from scraper.theresanai_scraper import TheresanaiScraper
from scraper.futurepedia_scraper import FuturepediaScraper
from scraper.hackernews_scraper import HackerNewsScraper
from scraper.devto_scraper import DevtoScraper
from scraper.reddit_scraper import RedditScraper
from scraper.producthunt_scraper import ProductHuntScraper

def run_all_scrapers():
    print("=" * 50)
    print("AI SaaS Intelligence - Full Scraper Run")
    print("=" * 50)

    scrapers = [
        ("aitools.fyi",          AitoolsScraper(),          {"max_pages": 2}),
        ("theresanaiforthat.com", TheresanaiScraper(),       {"max_pages": 2}),
        ("futurepedia.io",        FuturepediaScraper(),      {"max_pages": 2}),
        ("hackernews",            HackerNewsScraper(),       {"max_results": 50}),
        ("devto",                 DevtoScraper(),            {"max_results": 50}),
        ("reddit",                RedditScraper(),           {"max_results": 50}),
        ("producthunt",           ProductHuntScraper(),      {"max_results": 50}),
    ]

    all_tools = []
    results_summary = []

    for name, scraper, kwargs in scrapers:
        print(f"\n{'='*30}")
        print(f"Running: {name}")
        print(f"{'='*30}")
        try:
            tools = scraper.scrape_tools(**kwargs)
            all_tools.extend(tools)
            results_summary.append({"source": name, "count": len(tools), "status": "ok"})
        except Exception as e:
            print(f"[ERROR] {name} failed: {e}")
            results_summary.append({"source": name, "count": 0, "status": f"error: {e}"})

    # Simpan hasil
    os.makedirs("data", exist_ok=True)
    output_path = "data/scraped_raw.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_tools, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 50)
    print("SCRAPING SUMMARY")
    print("=" * 50)
    for r in results_summary:
        status_icon = "✅" if r["status"] == "ok" else "❌"
        print(f"{status_icon} {r['source']:<25} {r['count']} tools")
    print(f"\n💾 Total saved: {len(all_tools)} tools → {output_path}")

    return all_tools

if __name__ == "__main__":
    run_all_scrapers()

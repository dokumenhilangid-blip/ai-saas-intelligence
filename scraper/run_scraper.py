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
from backend.database import init_db, bulk_insert_tools, log_scrape, get_stats

def run_all_scrapers():
    print("=" * 50)
    print("AI SaaS Intelligence - Full Scraper Run")
    print("=" * 50)

    # Inisialisasi database
    init_db()

    scrapers = [
        ("aitools.fyi",           AitoolsScraper(),     {"max_pages": 2}),
        ("theresanaiforthat.com", TheresanaiScraper(),  {"max_pages": 2}),
        ("futurepedia.io",        FuturepediaScraper(), {"max_pages": 2}),
        ("hackernews",            HackerNewsScraper(),  {"max_results": 50}),
        ("devto",                 DevtoScraper(),       {"max_results": 50}),
        ("reddit",                RedditScraper(),      {"max_results": 50}),
        ("producthunt",           ProductHuntScraper(), {"max_results": 50}),
    ]

    all_tools = []
    results_summary = []

    for name, scraper, kwargs in scrapers:
        print(f"\n{'='*30}")
        print(f"Running: {name}")
        print(f"{'='*30}")
        try:
            tools = scraper.scrape_tools(**kwargs)
            
            # Simpan ke database
            db_result = bulk_insert_tools(tools)
            log_scrape(name, len(tools), db_result["added"], "success")
            
            all_tools.extend(tools)
            results_summary.append({
                "source": name,
                "found": len(tools),
                "added": db_result["added"],
                "updated": db_result["updated"],
                "status": "ok"
            })
        except Exception as e:
            print(f"[ERROR] {name} failed: {e}")
            log_scrape(name, 0, 0, f"error: {e}")
            results_summary.append({
                "source": name,
                "found": 0,
                "added": 0,
                "updated": 0,
                "status": f"error: {e}"
            })

    # Simpan juga ke JSON backup
    os.makedirs("data", exist_ok=True)
    with open("data/scraped_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_tools, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 50)
    print("SCRAPING SUMMARY")
    print("=" * 50)
    for r in results_summary:
        icon = "✅" if r["status"] == "ok" else "❌"
        print(f"{icon} {r['source']:<25} found={r['found']} added={r['added']} updated={r['updated']}")

    # Database stats
    stats = get_stats()
    print(f"\n📊 DATABASE STATS:")
    print(f"   Total tools in DB : {stats['total_tools']}")
    print(f"   By source         : {stats['by_source']}")
    print(f"   Last updated      : {stats['last_updated']}")
    print(f"\n💾 JSON backup saved to data/scraped_raw.json")

    return all_tools

if __name__ == "__main__":
    run_all_scrapers()

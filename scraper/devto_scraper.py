import requests
from scraper.base_scraper import BaseScraper

class DevtoScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.api_base = "https://dev.to/api"

    def scrape_tools(self, max_results=50):
        print(f"\n[DevTo] Fetching AI tool articles...")
        all_tools = []

        tags = ["aitools", "ai", "machinelearning", "saas"]

        for tag in tags:
            tools = self._fetch_by_tag(tag, per_page=15)
            all_tools.extend(tools)
            self.polite_delay()

        seen = set()
        unique = []
        for t in all_tools:
            if t["url"] not in seen:
                seen.add(t["url"])
                unique.append(t)

        print(f"[DevTo] Total unique: {len(unique)}")
        return unique

    def _fetch_by_tag(self, tag, per_page=15):
        tools = []
        try:
            params = {"tag": tag, "per_page": per_page, "state": "rising"}
            resp = requests.get(f"{self.api_base}/articles", params=params, timeout=10)
            articles = resp.json()

            for article in articles:
                tool = {
                    "name": article.get("title", "")[:100],
                    "description": article.get("description", "")[:300],
                    "url": article.get("url", ""),
                    "category": tag,
                    "upvotes": article.get("positive_reactions_count", 0),
                    "comments": article.get("comments_count", 0),
                    "source": "devto"
                }
                if tool["name"] and tool["url"]:
                    tools.append(tool)
        except Exception as e:
            print(f"[DevTo] Error for tag {tag}: {e}")
        return tools

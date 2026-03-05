import requests
from scraper.base_scraper import BaseScraper

class HackerNewsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.api_base = "https://hacker-news.firebaseio.com/v0"
        self.search_api = "https://hn.algolia.com/api/v1/search"

    def scrape_tools(self, max_results=50):
        print(f"\n[HackerNews] Searching for AI tools...")
        all_tools = []

        queries = ["Show HN: AI tool", "Launch HN: AI SaaS", "Show HN: built with AI"]

        for query in queries:
            tools = self._search(query, max_results // len(queries))
            all_tools.extend(tools)
            self.polite_delay()

        # Deduplicate by URL
        seen = set()
        unique = []
        for t in all_tools:
            if t["url"] not in seen:
                seen.add(t["url"])
                unique.append(t)

        print(f"[HackerNews] Total unique: {len(unique)}")
        return unique

    def _search(self, query, limit=20):
        tools = []
        try:
            params = {
                "query": query,
                "tags": "story",
                "hitsPerPage": limit
            }
            resp = requests.get(self.search_api, params=params, timeout=10)
            data = resp.json()

            for hit in data.get("hits", []):
                tool = {
                    "name": hit.get("title", "")[:100],
                    "description": hit.get("story_text", "")[:300] if hit.get("story_text") else "",
                    "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    "category": "hacker-news",
                    "upvotes": hit.get("points", 0),
                    "comments": hit.get("num_comments", 0),
                    "source": "hackernews"
                }
                if tool["name"]:
                    tools.append(tool)
        except Exception as e:
            print(f"[HackerNews] Error: {e}")
        return tools

import requests
from scraper.base_scraper import BaseScraper

class RedditScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.reddit.com"
        # Pakai JSON API publik Reddit (tanpa auth key)
        self.headers.update({"User-Agent": "ai-saas-intelligence-bot/1.0"})

    def scrape_tools(self, max_results=50):
        print(f"\n[Reddit] Fetching AI tool posts...")
        all_tools = []

        subreddits = [
            "artificial", "MachineLearning",
            "SideProject", "startups", "AITools"
        ]

        for sub in subreddits:
            tools = self._fetch_subreddit(sub, limit=10)
            all_tools.extend(tools)
            self.polite_delay()

        seen = set()
        unique = []
        for t in all_tools:
            if t["url"] not in seen:
                seen.add(t["url"])
                unique.append(t)

        print(f"[Reddit] Total unique: {len(unique)}")
        return unique

    def _fetch_subreddit(self, subreddit, limit=10):
        tools = []
        try:
            url = f"{self.base_url}/r/{subreddit}/search.json"
            params = {
                "q": "AI tool OR SaaS OR launch",
                "sort": "new",
                "limit": limit,
                "restrict_sr": "true",
                "t": "month"
            }
            resp = requests.get(url, headers=self.headers, params=params, timeout=10)
            data = resp.json()

            posts = data.get("data", {}).get("children", [])
            for post in posts:
                p = post.get("data", {})
                tool = {
                    "name": p.get("title", "")[:100],
                    "description": p.get("selftext", "")[:300],
                    "url": p.get("url") or f"https://reddit.com{p.get('permalink','')}",
                    "category": subreddit,
                    "upvotes": p.get("score", 0),
                    "comments": p.get("num_comments", 0),
                    "source": "reddit"
                }
                if tool["name"]:
                    tools.append(tool)
        except Exception as e:
            print(f"[Reddit] Error for r/{subreddit}: {e}")
        return tools

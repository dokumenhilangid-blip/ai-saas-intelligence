import requests
from scraper.base_scraper import BaseScraper

class ProductHuntScraper(BaseScraper):
    def __init__(self, api_key=None):
        super().__init__()
        self.api_url = "https://api.producthunt.com/v2/api/graphql"
        self.api_key = api_key  # Optional untuk sekarang

    def scrape_tools(self, max_results=50):
        print(f"\n[ProductHunt] Fetching AI tools...")

        if not self.api_key:
            print("[ProductHunt] No API key — using public HTML fallback")
            return self._scrape_html(max_results)

        return self._scrape_api(max_results)

    def _scrape_html(self, max_results=50):
        """Fallback: scrape HTML tanpa API key"""
        tools = []
        url = "https://www.producthunt.com/topics/artificial-intelligence"
        soup = self.get_page(url)
        if not soup:
            return tools

        cards = soup.find_all("div", {"data-test": lambda x: x and "post" in str(x).lower()})
        if not cards:
            cards = soup.find_all("li", class_=lambda c: c and "item" in str(c).lower())

        for card in cards[:max_results]:
            try:
                name_el = card.find(["h3", "h2", "strong"])
                desc_el = card.find("p")
                link_el = card.find("a", href=True)

                tool = {
                    "name": name_el.get_text(strip=True) if name_el else None,
                    "description": desc_el.get_text(strip=True)[:300] if desc_el else None,
                    "url": f"https://producthunt.com{link_el['href']}" if link_el else None,
                    "category": "product-hunt",
                    "source": "producthunt"
                }
                if tool["name"]:
                    tools.append(tool)
            except Exception as e:
                print(f"[ProductHunt] Parse error: {e}")

        print(f"[ProductHunt] Found: {len(tools)}")
        return tools

    def _scrape_api(self, max_results=50):
        """GraphQL API — butuh API key dari producthunt.com/v2/oauth/applications"""
        query = """
        {
          posts(first: 50, topic: "artificial-intelligence", order: VOTES) {
            edges {
              node {
                name
                tagline
                url
                votesCount
                website
              }
            }
          }
        }
        """
        try:
            headers = {
                **self.headers,
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            resp = requests.post(
                self.api_url,
                json={"query": query},
                headers=headers,
                timeout=15
            )
            data = resp.json()
            tools = []
            for edge in data.get("data", {}).get("posts", {}).get("edges", []):
                node = edge.get("node", {})
                tool = {
                    "name": node.get("name"),
                    "description": node.get("tagline", "")[:300],
                    "url": node.get("website") or node.get("url"),
                    "category": "product-hunt",
                    "upvotes": node.get("votesCount", 0),
                    "source": "producthunt"
                }
                if tool["name"]:
                    tools.append(tool)
            print(f"[ProductHunt] API found: {len(tools)}")
            return tools
        except Exception as e:
            print(f"[ProductHunt] API error: {e}")
            return []

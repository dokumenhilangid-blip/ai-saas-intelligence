from scraper.base_scraper import BaseScraper

class TheresanaiScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://theresanaiforthat.com"

    def scrape_tools(self, max_pages=3):
        all_tools = []
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/ais/?page={page}"
            print(f"\n[Theresanai] Scraping page {page}...")
            soup = self.get_page(url)
            if not soup:
                break
            tools = self._parse_tools(soup)
            if not tools:
                break
            all_tools.extend(tools)
            print(f"[Theresanai] Found {len(tools)} tools on page {page}")
            if page < max_pages:
                self.polite_delay()
        print(f"[Theresanai] Total: {len(all_tools)}")
        return all_tools

    def _parse_tools(self, soup):
        tools = []
        cards = soup.find_all("div", class_=lambda c: c and "ai_link" in c.lower())
        if not cards:
            cards = soup.find_all("a", class_=lambda c: c and "ai" in str(c).lower())
        for card in cards:
            tool = self._extract(card)
            if tool and tool.get("name"):
                tools.append(tool)
        return tools

    def _extract(self, card):
        try:
            tool = {
                "name": None,
                "description": None,
                "url": None,
                "category": None,
                "source": "theresanaiforthat.com"
            }
            name_el = card.find(["h2", "h3", "h4", "strong"])
            if name_el:
                tool["name"] = name_el.get_text(strip=True)
            desc_el = card.find("p")
            if desc_el:
                tool["description"] = desc_el.get_text(strip=True)[:300]
            link = card.find("a", href=True)
            if link:
                href = link["href"]
                tool["url"] = href if href.startswith("http") else f"{self.base_url}{href}"
            cat = card.find(class_=lambda c: c and "categ" in str(c).lower())
            if cat:
                tool["category"] = cat.get_text(strip=True)
            return tool
        except Exception as e:
            print(f"[Theresanai] Parse error: {e}")
            return None

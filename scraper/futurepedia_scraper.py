from scraper.base_scraper import BaseScraper

class FuturepediaScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.futurepedia.io"

    def scrape_tools(self, max_pages=3):
        all_tools = []
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/ai-tools?page={page}"
            print(f"\n[Futurepedia] Scraping page {page}...")
            soup = self.get_page(url)
            if not soup:
                break
            tools = self._parse_tools(soup)
            if not tools:
                break
            all_tools.extend(tools)
            print(f"[Futurepedia] Found {len(tools)} tools on page {page}")
            if page < max_pages:
                self.polite_delay()
        print(f"[Futurepedia] Total: {len(all_tools)}")
        return all_tools

    def _parse_tools(self, soup):
        tools = []
        cards = soup.find_all("div", class_=lambda c: c and "tool" in str(c).lower())
        if not cards:
            cards = soup.find_all("article")
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
                "pricing": None,
                "source": "futurepedia.io"
            }
            name_el = card.find(["h2", "h3", "h4"])
            if name_el:
                tool["name"] = name_el.get_text(strip=True)
            desc_el = card.find("p")
            if desc_el:
                tool["description"] = desc_el.get_text(strip=True)[:300]
            link = card.find("a", href=True)
            if link:
                href = link["href"]
                tool["url"] = href if href.startswith("http") else f"{self.base_url}{href}"
            pricing_el = card.find(class_=lambda c: c and "pric" in str(c).lower())
            if pricing_el:
                tool["pricing"] = pricing_el.get_text(strip=True)
            cat_el = card.find(class_=lambda c: c and "categ" in str(c).lower())
            if cat_el:
                tool["category"] = cat_el.get_text(strip=True)
            return tool
        except Exception as e:
            print(f"[Futurepedia] Parse error: {e}")
            return None

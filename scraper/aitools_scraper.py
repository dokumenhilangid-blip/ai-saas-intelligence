from scraper.base_scraper import BaseScraper

class AitoolsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://aitools.fyi"

    def scrape_tools(self, max_pages=3):
        all_tools = []
        
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/?page={page}"
            print(f"\n[AitoolsScraper] Scraping page {page}...")
            
            soup = self.get_page(url)
            if not soup:
                print(f"[AitoolsScraper] Failed to get page {page}, stopping.")
                break

            tools = self._parse_tools(soup)
            
            if not tools:
                print(f"[AitoolsScraper] No tools found on page {page}, stopping.")
                break

            all_tools.extend(tools)
            print(f"[AitoolsScraper] Found {len(tools)} tools on page {page}")
            
            if page < max_pages:
                self.polite_delay()

        print(f"\n[AitoolsScraper] Total tools scraped: {len(all_tools)}")
        return all_tools

    def _parse_tools(self, soup):
        tools = []
        
        # Cari semua card/item tool
        tool_cards = soup.find_all("div", class_=lambda c: c and "card" in c.lower())
        
        if not tool_cards:
            # Coba selector alternatif
            tool_cards = soup.find_all("a", href=lambda h: h and "/tool/" in str(h))

        for card in tool_cards:
            tool = self._extract_tool_data(card)
            if tool and tool.get("name"):
                tools.append(tool)

        return tools

    def _extract_tool_data(self, card):
        try:
            tool = {
                "name": None,
                "description": None,
                "url": None,
                "category": None,
                "source": "aitools.fyi"
            }

            # Nama tool
            name_el = card.find(["h2", "h3", "h4"])
            if name_el:
                tool["name"] = name_el.get_text(strip=True)

            # Deskripsi
            desc_el = card.find("p")
            if desc_el:
                tool["description"] = desc_el.get_text(strip=True)[:300]

            # URL
            link_el = card.find("a", href=True)
            if link_el:
                href = link_el["href"]
                if href.startswith("http"):
                    tool["url"] = href
                else:
                    tool["url"] = f"https://aitools.fyi{href}"

            return tool
        except Exception as e:
            print(f"[Parser] Error: {e}")
            return None

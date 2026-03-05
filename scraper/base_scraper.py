import requests
from bs4 import BeautifulSoup
import time
import random

class BaseScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/91.0.4472.120 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_page(self, url):
        try:
            print(f"[Scraper] Fetching: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            print(f"[Scraper] Status: {response.status_code}")
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"[Scraper] Error fetching {url}: {e}")
            return None

    def polite_delay(self):
        delay = random.uniform(2, 5)
        print(f"[Scraper] Waiting {delay:.1f}s...")
        time.sleep(delay)

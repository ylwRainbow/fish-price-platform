import re
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright, Browser, Page

class ShuichanqConnector:
    def __init__(self, params: Dict[str, Any]):
        self.list_url = params.get("list_url", "")
        self.detail_limit = int(params.get("detail_limit", 20))
        self.fish_keywords = params.get("fish_keywords", [])
        self.region_keywords = params.get("region_keywords", [])
        self.price_pattern = re.compile(r'([0-9]+(?:\.[0-9]+)?)\s*元/斤')
        self.date_pattern = re.compile(r'(\d{4}[\-/年]\d{1,2}[\-/月]\d{1,2}[日]?)')
        self.headless = params.get("headless", True)
        self.timeout = params.get("timeout", 30000)
        self.max_pages = params.get("max_pages", 5)

    def _extract_date(self, text: str) -> str:
        match = self.date_pattern.search(text)
        if match:
            try:
                ds = match.group(1).replace('年', '-').replace('月', '-').replace('日', '').replace('/', '-')
                dt = datetime.strptime(ds, '%Y-%m-%d')
                return dt.date().isoformat()
            except:
                pass
        return datetime.now().date().isoformat()

    def fetch(self, fish: Dict[str, Any], market: Dict[str, Any], start: str, end: str) -> List[Dict[str, Any]]:
        from playwright.sync_api import sync_playwright
        all_prices = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                print(f"Navigating to: {self.list_url}")
                page.goto(self.list_url, timeout=self.timeout)
                page.wait_for_timeout(3000)
                all_links = []
                for page_num in range(self.max_pages):
                    print(f"Scanning page {page_num + 1}...")
                    links = page.query_selector_all('a[href*="ac=view&pubid="]')
                    print(f"  Found {len(links)} article links")
                    for link in links:
                        href = link.get_attribute('href')
                        if href:
                            if href.startswith('/'):
                                href = 'https://www.shuichanq.com' + href
                            elif not href.startswith('http'):
                                href = 'https://www.shuichanq.com/' + href
                            if href not in all_links:
                                all_links.append(href)
                    next_btn = page.query_selector('a:has-text("下一页")') or page.query_selector('.next')
                    if not next_btn:
                        pagination = page.query_selector('.pagination')
                        if pagination:
                            next_btn = pagination.query_selector('a:last-child')
                    if not next_btn or page_num >= self.max_pages - 1:
                        break
                    try:
                        next_btn.click()
                        page.wait_for_timeout(2000)
                    except:
                        break
                browser.close()
                all_links = all_links[:self.detail_limit]
                print(f"Total unique links to process: {len(all_links)}")
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                })
                for idx, url in enumerate(all_links):
                    try:
                        print(f"  [{idx+1}/{len(all_links)}] {url[:60]}...")
                        page.goto(url, timeout=15000)
                        page.wait_for_timeout(1000)
                        text = page.content()
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(text, 'lxml')
                        clean_text = soup.get_text(' ')
                        article_date = self._extract_date(clean_text)
                        fish_ok = any(k in clean_text for k in (self.fish_keywords or [fish['name'], fish.get('alias', '')]))
                        region_ok = any(k in clean_text for k in (self.region_keywords or [market['name'][:2]]))
                        if not (fish_ok and region_ok):
                            print(f"    Skipped: fish_ok={fish_ok}, region_ok={region_ok}")
                            continue
                        found_prices = []
                        for m in self.price_pattern.finditer(clean_text):
                            price = float(m.group(1))
                            found_prices.append(price)
                        if found_prices:
                            avg_price = sum(found_prices) / len(found_prices)
                            all_prices.append({
                                "ts": article_date + "T00:00:00+08:00",
                                "price": round(avg_price, 2),
                                "currency": "CNY",
                                "unit": "kg",
                                "source_text": f"Found {len(found_prices)} prices, avg: {round(avg_price, 2)}"
                            })
                            print(f"    Found date={article_date}, prices={found_prices[:5]}...")
                        else:
                            print(f"    No prices found")
                    except Exception as e:
                        print(f"    Error: {e}")
                        continue
                browser.close()
        except Exception as e:
            print(f"Error in fetch: {e}")
        return all_prices


def create_shuichanq_connector(params: Dict[str, Any]) -> ShuichanqConnector:
    return ShuichanqConnector(params)

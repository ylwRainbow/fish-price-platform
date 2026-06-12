import re
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright, Browser, Page

class WeChatMPConnector:
    def __init__(self, params: Dict[str, Any]):
        self.account_name = params.get("account_name", "")
        self.keywords = params.get("keywords", ["鱼价", "塘口价", "行情"])
        self.price_pattern = re.compile(r'([0-9]+(?:\.[0-9]+)?)\s*[元\-～~至]\s*(?:斤|公斤|kg)')
        self.date_pattern = re.compile(r'(\d{4}[\-/年]\d{1,2}[\-/月]\d{1,2}[日]?)')
        self.headless = params.get("headless", True)
        self.timeout = params.get("timeout", 30000)
        self.max_articles = params.get("max_articles", 10)
        self._browser: Optional[Browser] = None

    async def _ensure_browser(self):
        if self._browser is None:
            p = await async_playwright().start()
            self._browser = await p.chromium.launch(headless=self.headless)

    async def _close_browser(self):
        if self._browser:
            await self._browser.close()
            self._browser = None

    async def _search_sogou_articles(self, page: Page) -> List[Dict[str, Any]]:
        import urllib.parse
        encoded_name = urllib.parse.quote(self.account_name)
        search_url = f"https://weixin.sogou.com/weixin?type=2&query={encoded_name}"
        await page.goto(search_url, timeout=self.timeout)
        await page.wait_for_timeout(3000)
        articles = []
        article_elements = await page.query_selector_all('li[data-val]')
        if not article_elements:
            article_elements = await page.query_selector_all('.news-list li')
        for i, elem in enumerate(article_elements[:self.max_articles]):
            try:
                title_elem = await elem.query_selector('h3 a') or await elem.query_selector('.tit a')
                if not title_elem:
                    continue
                title = await title_elem.inner_text()
                link = await title_elem.get_attribute('href')
                if not link:
                    continue
                account_elem = await elem.query_selector('.account') or await elem.query_selector('.s-p .s2')
                account_name = await account_elem.inner_text() if account_elem else ""
                if self.account_name not in account_name:
                    continue
                date_elem = await elem.query_selector('.time') or await elem.query_selector('.s2')
                date_str = await date_elem.inner_text() if date_elem else ""
                articles.append({
                    "title": title.strip(),
                    "url": link,
                    "account": account_name.strip(),
                    "date_str": date_str.strip()
                })
            except Exception as e:
                print(f"Error parsing article {i}: {e}")
                continue
        return articles

    async def _extract_price_from_article(self, page: Page, url: str) -> List[Dict[str, Any]]:
        prices = []
        try:
            await page.goto(url, timeout=self.timeout)
            await page.wait_for_timeout(3000)
            content_elem = await page.query_selector('#js_content') or await page.query_selector('.rich_media_content')
            if not content_elem:
                return prices
            text = await content_elem.inner_text()
            date_match = self.date_pattern.search(text)
            article_date = None
            if date_match:
                try:
                    ds = date_match.group(1).replace('年', '-').replace('月', '-').replace('日', '').replace('/', '-')
                    article_date = datetime.strptime(ds, '%Y-%m-%d').date().isoformat()
                except:
                    pass
            if not article_date:
                article_date = datetime.now().date().isoformat()
            tables = await content_elem.query_selector_all('table')
            for table in tables:
                rows = await table.query_selector_all('tr')
                for row in rows:
                    row_text = await row.inner_text()
                    has_keyword = any(kw in row_text for kw in self.keywords)
                    if not has_keyword:
                        continue
                    cells = await row.query_selector_all('td')
                    if len(cells) >= 2:
                        name_cell = cells[0]
                        name_text = await name_cell.inner_text()
                        for j, cell in enumerate(cells[1:], 1):
                            cell_text = await cell.inner_text()
                            price_match = re.search(r'([0-9]+(?:\.[0-9]+)?)', cell_text)
                            if price_match:
                                try:
                                    price = float(price_match.group(1))
                                    prices.append({
                                        "ts": article_date + "T00:00:00+08:00",
                                        "price": price,
                                        "currency": "CNY",
                                        "unit": "kg",
                                        "source_text": f"{name_text.strip()}: {cell_text.strip()}"
                                    })
                                    break
                                except:
                                    continue
            lines = text.split('\n')
            for line in lines:
                for kw in self.keywords:
                    if kw in line:
                        matches = self.price_pattern.findall(line)
                        for price_str in matches:
                            try:
                                price = float(price_str)
                                prices.append({
                                    "ts": article_date + "T00:00:00+08:00",
                                    "price": price,
                                    "currency": "CNY",
                                    "unit": "kg",
                                    "source_text": line.strip()[:100]
                                })
                            except:
                                continue
                        break
        except Exception as e:
            print(f"Error extracting price from {url}: {e}")
        return prices

    async def fetch_async(self, fish: Dict[str, Any], market: Dict[str, Any], start: str, end: str) -> List[Dict[str, Any]]:
        all_prices = []
        try:
            await self._ensure_browser()
            page = await self._browser.new_page()
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            articles = await self._search_sogou_articles(page)
            print(f"Found {len(articles)} articles from {self.account_name}")
            for article in articles:
                print(f"Processing: {article['title']}")
                prices = await self._extract_price_from_article(page, article["url"])
                all_prices.extend(prices)
                await page.wait_for_timeout(500)
            await page.close()
        except Exception as e:
            print(f"Error in fetch_async: {e}")
        finally:
            await self._close_browser()
        return all_prices

    def fetch(self, fish: Dict[str, Any], market: Dict[str, Any], start: str, end: str) -> List[Dict[str, Any]]:
        return asyncio.run(self.fetch_async(fish, market, start, end))


def parse_sogou_date(date_str: str) -> Optional[datetime]:
    if not date_str:
        return None
    date_str = date_str.strip()
    today = datetime.now()
    if '天前' in date_str:
        match = re.search(r'(\d+)', date_str)
        days = int(match.group(1)) if match else 1
        return today - timedelta(days=days)
    elif '小时前' in date_str or '分钟前' in date_str:
        return today
    elif '昨天' in date_str:
        return today - timedelta(days=1)
    elif '前天' in date_str:
        return today - timedelta(days=2)
    else:
        try:
            if re.match(r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}', date_str):
                ds = date_str.replace('年', '-').replace('月', '-').replace('日', '').replace('/', '-')
                return datetime.strptime(ds.split()[0], '%Y-%m-%d')
            elif re.match(r'\d{1,2}[-/月]\d{1,2}', date_str):
                ds = date_str.replace('月', '-').replace('日', '').replace('/', '-')
                return datetime.strptime(f"{today.year}-{ds}", '%Y-%m-%d')
        except:
            pass
    return None


class WeChatMPConnectorSync:
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        self.account_name = params.get("account_name", "")
        self.keywords = params.get("keywords", ["鱼价", "塘口价", "行情"])
        self.price_pattern = re.compile(r'([0-9]+(?:\.[0-9]+)?)\s*[元\-～~至]\s*(?:斤|公斤|kg)')
        self.date_pattern = re.compile(r'(\d{4}[\-/年]\d{1,2}[\-/月]\d{1,2}[日]?)')
        self.headless = params.get("headless", True)
        self.timeout = params.get("timeout", 30000)
        self.max_articles = params.get("max_articles", 10)
        self.max_pages = params.get("max_pages", 5)

    def _parse_article_element(self, elem, idx: int) -> Optional[Dict[str, Any]]:
        try:
            title_elem = elem.query_selector('h3 a') or elem.query_selector('.tit a')
            if not title_elem:
                return None
            title = title_elem.inner_text()
            link = title_elem.get_attribute('href')
            if not link:
                return None
            if link.startswith('/'):
                link = 'https://weixin.sogou.com' + link
            elif link.startswith('//'):
                link = 'https:' + link
            full_text = elem.inner_text()
            lines = [l.strip() for l in full_text.split('\n') if l.strip()]
            account_name = ""
            date_str = ""
            for line in lines:
                if re.match(r'\d{4}-\d{1,2}-\d{1,2}', line):
                    date_str = line
                elif len(line) < 15 and ('渔业' in line or '发布' in line or '水产' in line):
                    if not re.match(r'\d{4}-\d{1,2}-\d{1,2}', line):
                        account_name = line
            if self.account_name not in account_name:
                return None
            article_date = parse_sogou_date(date_str)
            return {
                "title": title.strip(),
                "url": link,
                "account": account_name.strip(),
                "date": article_date or datetime.now(),
                "date_str": date_str
            }
        except Exception as e:
            print(f"Error parsing article {idx}: {e}")
            return None

    def _extract_prices_from_content(self, content_elem, article_date: str) -> List[Dict[str, Any]]:
        prices = []
        if not content_elem:
            return prices
        text = content_elem.inner_text()
        date_match = self.date_pattern.search(text)
        if date_match:
            try:
                ds = date_match.group(1).replace('年', '-').replace('月', '-').replace('日', '').replace('/', '-')
                article_date = datetime.strptime(ds, '%Y-%m-%d').date().isoformat()
            except:
                pass
        tables = content_elem.query_selector_all('table')
        for table in tables:
            rows = table.query_selector_all('tr')
            for row in rows:
                row_text = row.inner_text()
                has_keyword = any(kw in row_text for kw in self.keywords)
                if not has_keyword:
                    continue
                cells = row.query_selector_all('td')
                if len(cells) >= 2:
                    name_cell = cells[0]
                    name_text = name_cell.inner_text()
                    for j, cell in enumerate(cells[1:], 1):
                        cell_text = cell.inner_text()
                        price_match = re.search(r'([0-9]+(?:\.[0-9]+)?)', cell_text)
                        if price_match:
                            try:
                                price = float(price_match.group(1))
                                prices.append({
                                    "ts": article_date + "T00:00:00+08:00",
                                    "price": price,
                                    "currency": "CNY",
                                    "unit": "kg",
                                    "source_text": f"{name_text.strip()}: {cell_text.strip()}"
                                })
                                break
                            except:
                                continue
        return prices

    def fetch(self, fish: Dict[str, Any], market: Dict[str, Any], start: str, end: str) -> List[Dict[str, Any]]:
        from playwright.sync_api import sync_playwright
        import urllib.parse
        all_prices = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                encoded_name = urllib.parse.quote(self.account_name)
                search_url = f"https://weixin.sogou.com/weixin?type=2&query={encoded_name}"
                print(f"Searching articles from WeChat account: {self.account_name}")
                page.goto(search_url, timeout=self.timeout)
                page.wait_for_timeout(3000)
                all_articles = []
                for page_num in range(self.max_pages):
                    print(f"Scanning page {page_num + 1}...")
                    article_elements = page.query_selector_all('li[data-val]')
                    if not article_elements:
                        article_elements = page.query_selector_all('.news-list li')
                    print(f"  Found {len(article_elements)} article elements on page {page_num + 1}")
                    for i, elem in enumerate(article_elements):
                        article = self._parse_article_element(elem, i)
                        if article:
                            all_articles.append(article)
                    next_btn = page.query_selector('a.np') or page.query_selector('.np')
                    if not next_btn:
                        next_btn = page.query_selector('a:has-text("下一页")')
                    if not next_btn:
                        links = page.query_selector_all('a')
                        for link in links:
                            href = link.get_attribute('href') or ''
                            text = link.inner_text().strip()
                            if '下一页' in text or 'next' in href.lower() or 'page=' in href:
                                next_btn = link
                                break
                    if not next_btn:
                        print("  No more pages available")
                        break
                    try:
                        next_btn.click()
                        page.wait_for_timeout(3000)
                    except Exception as e:
                        print(f"  Failed to navigate to next page: {e}")
                        break
                seen_urls = set()
                unique_articles = []
                for article in all_articles:
                    if article['url'] not in seen_urls:
                        seen_urls.add(article['url'])
                        unique_articles.append(article)
                print(f"Found {len(unique_articles)} unique articles from {self.account_name}")
                articles_to_process = unique_articles[:self.max_articles]
                print(f"Processing {len(articles_to_process)} articles...")
                for idx, article in enumerate(articles_to_process):
                    try:
                        print(f"  [{idx+1}/{len(articles_to_process)}] {article['title'][:40]}... (date: {article['date_str']})")
                        page.goto(article['url'], timeout=self.timeout)
                        page.wait_for_timeout(2000)
                        content_elem = page.query_selector('#js_content') or page.query_selector('.rich_media_content')
                        prices = self._extract_prices_from_content(content_elem, article['date'].date().isoformat() if hasattr(article['date'], 'date') else str(article['date']))
                        if prices:
                            print(f"    Found {len(prices)} price points")
                            all_prices.extend(prices)
                        page.wait_for_timeout(300)
                    except Exception as e:
                        print(f"    Error processing article: {e}")
                        continue
                browser.close()
        except Exception as e:
            print(f"Error in fetch: {e}")
        return all_prices


def create_wechat_connector(params: Dict[str, Any]) -> WeChatMPConnectorSync:
    return WeChatMPConnectorSync(params)

from typing import Dict, Any, List
from datetime import datetime, timedelta
import re
import requests
from bs4 import BeautifulSoup

class BaseConnector:
    def fetch(self, fish:Dict[str,Any], market:Dict[str,Any], start:str, end:str) -> List[Dict[str,Any]]:
        raise NotImplementedError

class MockPondConnector(BaseConnector):
    def __init__(self, base:float):
        self.base = base
    def fetch(self, fish:Dict[str,Any], market:Dict[str,Any], start:str, end:str) -> List[Dict[str,Any]]:
        s = datetime.fromisoformat(start); e = datetime.fromisoformat(end)
        out = []
        cur = s
        i = 0
        while cur <= e:
            v = self.base + (i * 0.02) + (abs((i % 21) - 10) * 0.04)
            out.append({"ts": cur.date().isoformat()+"T00:00:00+08:00", "price": round(v,2), "currency": "CNY", "unit": "kg"})
            cur += timedelta(days=1); i += 1
        return out

def connector_from_source(src:Dict[str,Any]) -> BaseConnector:
    t = src.get("type","mock")
    if t == "mock":
        base = float(src.get("params",{}).get("base", 20.0))
        return MockPondConnector(base)
    if t == "http_html":
        from .shuichanq_connector import create_shuichanq_connector
        return create_shuichanq_connector(src.get("params", {}))
    if t == "wechat_mp":
        from .wechat_connector import create_wechat_connector
        return create_wechat_connector(src.get("params", {}))
    return MockPondConnector(float(src.get("params",{}).get("base", 20.0)))

class HttpHtmlConnector(BaseConnector):
    def __init__(self, params:Dict[str,Any]):
        self.params = params
        self.list_url = params.get("list_url")
        self.detail_limit = int(params.get("detail_limit", 20))
        self.fish_keywords = params.get("fish_keywords", [])
        self.region_keywords = params.get("region_keywords", [])
        self.price_pattern = re.compile(r'([0-9]+(?:\.[0-9]+)?)\s*元/斤')
        self.date_pattern = re.compile(r'(\d{4}[\-/年]\d{1,2}[\-/月]\d{1,2}[日]?)')

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

    def fetch(self, fish:Dict[str,Any], market:Dict[str,Any], start:str, end:str) -> List[Dict[str,Any]]:
        if not self.list_url:
            return []
        try:
            html = requests.get(self.list_url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }).text
        except Exception as e:
            print(f"Error fetching list page: {e}")
            return []
        soup = BeautifulSoup(html, 'lxml')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'plugin.php?id=xigua_hb&ac=view&pubid=' in href:
                full_url = href if href.startswith('http') else requests.compat.urljoin(self.list_url, href)
                if full_url not in links:
                    links.append(full_url)
        links = links[:self.detail_limit]
        print(f"Found {len(links)} article links to process")
        out = []
        for idx, url in enumerate(links):
            try:
                print(f"  Processing article {idx+1}/{len(links)}: {url[:60]}...")
                content = requests.get(url, timeout=15, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }).text
            except Exception as e:
                print(f"    Error fetching article: {e}")
                continue
            soup = BeautifulSoup(content, 'lxml')
            text = soup.get_text(' ')
            article_date = self._extract_date(text)
            fish_ok = any(k in text for k in (self.fish_keywords or [fish['name'], fish.get('alias','')]))
            region_ok = any(k in text for k in (self.region_keywords or [market['name'][:2]]))
            if not (fish_ok and region_ok):
                print(f"    Skipped: fish_ok={fish_ok}, region_ok={region_ok}")
                continue
            found_prices = []
            for m in self.price_pattern.finditer(text):
                price = float(m.group(1))
                found_prices.append(price)
            if found_prices:
                avg_price = sum(found_prices) / len(found_prices)
                out.append({
                    "ts": article_date + "T00:00:00+08:00",
                    "price": round(avg_price, 2),
                    "currency": "CNY",
                    "unit": "kg",
                    "source_text": f"Found {len(found_prices)} prices, avg: {round(avg_price, 2)}"
                })
                print(f"    Found date={article_date}, prices={found_prices}")
            else:
                print(f"    No prices found")
        return out

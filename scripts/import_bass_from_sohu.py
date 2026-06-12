# -*- coding: utf-8 -*-
"""
加州鲈价格数据导入脚本
从搜狐"杰大饲料特约·加州鲈行情周报"获取塘口价数据
"""
import re
from datetime import datetime, timedelta
import pymysql
import requests
from bs4 import BeautifulSoup

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'YOUR_PASSWORD',
    'database': 'fish_prices',
    'charset': 'utf8mb4'
}

MARKET_MAP = {
    '广东佛山': 201,
    '浙江湖州': 202,
    '浙江': 202,
    '江苏吴江': 203,
    '江苏': 203,
    '四川成都': 204,
    '四川': 204,
    '湖南华容': 205,
    '湖南': 205,
    '湖北武汉': 206,
    '湖北': 206,
    '河南郑州': 207,
    '河南': 207
}

FISH_ID = 1

def parse_price(price_str):
    """
    解析价格字符串，返回元/斤的价格
    """
    if not price_str or price_str == '-':
        return None
    price_str = price_str.replace('元/斤', '').strip()
    if '-' in price_str:
        parts = price_str.split('-')
        try:
            low = float(parts[0])
            high = float(parts[1])
            return round((low + high) / 2, 2)
        except:
            return None
    try:
        return float(price_str)
    except:
        return None

def extract_week_number(title):
    """从标题中提取周报期号"""
    match = re.search(r'第(\d+)期', title)
    if match:
        return int(match.group(1))
    return None

def estimate_date_from_week(week_num, year=2026):
    """根据周报期号估算日期"""
    first_week = datetime(year, 1, 1)
    estimated = first_week + timedelta(weeks=week_num - 1)
    return estimated

def fetch_sohu_article(url):
    """获取搜狐文章内容并解析价格数据"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_elem = soup.find('h1')
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        article = soup.find('article') or soup.find('div', class_='article-content')
        if not article:
            article = soup.find('div', class_='text')
        if not article:
            return None
            
        text = article.get_text('\n', strip=True)
        
        week_num = extract_week_number(title)
        
        date_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', text)
        if date_match:
            date_str = date_match.group(1).replace('/', '-')
            try:
                pub_date = datetime.strptime(date_str, '%Y-%m-%d')
            except:
                pub_date = estimate_date_from_week(week_num) if week_num else None
        else:
            pub_date = estimate_date_from_week(week_num) if week_num else None
        
        prices = []
        
        patterns = [
            (r'广东佛山[^\d]*(\d+\.?\d*-?\d*\.?\d*)\s*元/斤', '广东佛山'),
            (r'浙江湖州[^\d]*(\d+\.?\d*-?\d*\.?\d*)\s*元/斤', '浙江湖州'),
            (r'江苏吴江[^\d]*(\d+\.?\d*-?\d*\.?\d*)\s*元/斤', '江苏吴江'),
            (r'四川成都[^\d]*(\d+\.?\d*-?\d*\.?\d*)\s*元/斤', '四川成都'),
            (r'湖南华容[^\d]*(\d+\.?\d*-?\d*\.?\d*)\s*元/斤', '湖南华容'),
            (r'湖北武汉[^\d]*(\d+\.?\d*-?\d*\.?\d*)\s*元/斤', '湖北武汉'),
            (r'河南郑州[^\d]*(\d+\.?\d*-?\d*\.?\d*)\s*元/斤', '河南郑州'),
        ]
        
        for pattern, market_name in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price = parse_price(match.group(1))
                if price and market_name in MARKET_MAP:
                    prices.append({
                        'market': market_name,
                        'market_id': MARKET_MAP[market_name],
                        'price': price,
                        'date': pub_date,
                        'source_url': url
                    })
        
        return {
            'title': title,
            'url': url,
            'date': pub_date,
            'week_num': week_num,
            'prices': prices
        }
        
    except Exception as e:
        print("Error fetching {}: {}".format(url, e))
        return None

def save_to_database(records):
    """保存价格数据到数据库"""
    if not records:
        return 0
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    inserted = 0
    for record in records:
        try:
            sql = """
            INSERT INTO prices (fish_id, market_id, price, ts, price_type, source_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE price = VALUES(price)
            """
            cursor.execute(sql, (
                FISH_ID,
                record['market_id'],
                record['price'],
                record['date'].strftime('%Y-%m-%d') if record['date'] else None,
                'pond',
                record.get('source_url', '')
            ))
            if cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            print("Insert error: {}".format(e))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return inserted

KNOWN_ARTICLE_URLS = [
    "https://m.sohu.com/a/992571562_210667/",
    "https://m.sohu.com/a/989985535_210667/",
    "https://m.sohu.com/a/989622806_210667/",
    "https://www.sohu.com/a/951315758_210667",
    "https://www.sohu.com/a/968994799_210667",
    "https://www.sohu.com/a/946535621_210667",
    "https://www.sohu.com/a/897442360_210667",
    "https://www.sohu.com/a/919232291_210667",
]

def main():
    """主函数"""
    print("=" * 60)
    print("加州鲈价格数据导入脚本")
    print("=" * 60)
    
    all_records = []
    
    print("\n正在获取已知文章...")
    for url in KNOWN_ARTICLE_URLS:
        print("  获取: {}".format(url))
        article = fetch_sohu_article(url)
        if article and article.get('prices'):
            print("    标题: {}...".format(article['title'][:50]))
            print("    日期: {}".format(article['date']))
            print("    价格数: {}".format(len(article['prices'])))
            for p in article['prices']:
                all_records.append(p)
    
    print("\n共获取 {} 条价格记录".format(len(all_records)))
    
    if all_records:
        print("\n正在写入数据库...")
        inserted = save_to_database(all_records)
        print("成功写入 {} 条记录".format(inserted))
    
    print("\n完成！")

if __name__ == '__main__':
    main()

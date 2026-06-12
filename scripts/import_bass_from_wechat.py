# -*- coding: utf-8 -*-
"""
民众渔业微信文章鲈鱼价格数据导入脚本
从微信公众号文章中解析加州鲈价格数据并导入数据库
"""
import re
import pymysql
import requests
from datetime import datetime
from bs4 import BeautifulSoup

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'YOUR_PASSWORD',
    'database': 'fish_prices',
    'charset': 'utf8mb4'
}

MARKET_ID = 104
FISH_ID = 1

def parse_publish_date(soup):
    """
    从文章HTML中解析发布时间
    格式: 2026年1月15日 17:22
    优先使用文章发布时间，因为内容中的日期可能有编辑错误
    """
    publish_time_tag = soup.find('em', id='publish_time')
    if publish_time_tag:
        text = publish_time_tag.get_text()
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            try:
                return datetime(year, month, day)
            except:
                pass
    
    for tag in soup.find_all('em'):
        text = tag.get_text()
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            try:
                return datetime(year, month, day)
            except:
                pass
    
    return None

def parse_content_date(text):
    """
    从文章文本中解析日期（备用方案）
    格式: 2025-1-2更新, 2019-3-29更新, 2020-11-19更新
    注意: 内容中的年份可能有编辑错误，优先使用发布时间
    """
    text_clean = text.replace('\n', '')
    
    match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})更新', text_clean)
    if match:
        year = match.group(1)
        month = match.group(2).zfill(2)
        day = match.group(3).zfill(2)
        date_str = "{}-{}-{}".format(year, month, day)
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return None
    return None

def parse_price(price_str):
    """
    解析价格字符串
    格式: 8.5, 9-9.5, 8.5-9
    """
    if not price_str:
        return None
    
    price_str = price_str.strip()
    
    if price_str == '-' or price_str == '—' or price_str == '':
        return None
    
    price_str = re.sub(r'[^\d.\-]', '', price_str)
    
    if not price_str:
        return None
    
    if '-' in price_str:
        parts = price_str.split('-')
        try:
            low = float(parts[0])
            high = float(parts[1])
            return round((low + high) / 2, 2)
        except:
            try:
                return float(parts[0])
            except:
                return None
    else:
        try:
            return float(price_str)
        except:
            return None

def extract_bass_prices_from_text(text):
    """
    从纯文本中提取加州鲈价格数据
    格式:
    加州鲈
    0.6-1.3
    斤
    13
    12.6
    ↑
    """
    prices = []
    
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if '加州鲈' in line or '海鲈' in line:
            j = i + 1
            while j < len(lines) and j < i + 15:
                spec_line = lines[j].strip()
                
                if re.match(r'^[\d.]+-[\d.]+$', spec_line):
                    if j + 1 < len(lines) and lines[j + 1].strip() == '斤':
                        spec = spec_line + '斤'
                        
                        price_idx = j + 4
                        if price_idx < len(lines):
                            price_str = lines[price_idx].strip()
                            price = parse_price(price_str)
                            
                            if price and price > 0 and price < 100:
                                prices.append({
                                    'spec': spec,
                                    'price': price
                                })
                                j = j + 5
                                continue
                        
                        price_idx = j + 3
                        if price_idx < len(lines):
                            price_str = lines[price_idx].strip()
                            price = parse_price(price_str)
                            
                            if price and price > 0 and price < 100:
                                prices.append({
                                    'spec': spec,
                                    'price': price
                                })
                                j = j + 4
                                continue
                
                elif re.match(r'^[\d.]+(?:两|斤)起抓$', spec_line):
                    spec = spec_line
                    
                    price_idx = j + 3
                    if price_idx < len(lines):
                        price_str = lines[price_idx].strip()
                        price = parse_price(price_str)
                        
                        if price and price > 0 and price < 100:
                            prices.append({
                                'spec': spec,
                                'price': price
                            })
                
                j += 1
                
                if lines[j].strip() and re.search(r'[\u4e00-\u9fa5]{2,}', lines[j].strip()) and '鲈' not in lines[j].strip():
                    break
    
    return prices

def fetch_article(url):
    """
    获取微信文章内容
    优先使用文章发布时间，因为内容中的日期可能有编辑错误
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content_div = soup.find('div', class_='rich_media_content')
        if not content_div:
            content_div = soup.find('div', id='js_content')
        
        if not content_div:
            return None
        
        text = content_div.get_text('\n', strip=True)
        
        publish_date = parse_publish_date(soup)
        
        content_date = parse_content_date(text)
        
        date = publish_date or content_date
        if not date:
            return None
        
        if publish_date and content_date:
            if publish_date.year != content_date.year:
                print("  [注意] 发布时间({}) 与 内容日期({}) 年份不一致，使用发布时间".format(
                    publish_date.strftime('%Y-%m-%d'),
                    content_date.strftime('%Y-%m-%d')
                ))
        
        bass_prices = extract_bass_prices_from_text(text)
        
        if not bass_prices:
            return None
        
        return {
            'date': date,
            'prices': bass_prices,
            'url': url
        }
        
    except Exception as e:
        print("Error fetching {}: {}".format(url, e))
        return None

def save_to_database(records):
    """
    保存价格数据到数据库
    """
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
                MARKET_ID,
                record['price'],
                record['date'].strftime('%Y-%m-%d'),
                'pond',
                record['url']
            ))
            if cursor.rowcount > 0:
                inserted += 1
                print("  插入: {} {} {}元/斤".format(
                    record['date'].strftime('%Y-%m-%d'),
                    record.get('spec', ''),
                    record['price']
                ))
        except Exception as e:
            print("  插入错误: {}".format(e))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return inserted

def main():
    """
    主函数
    """
    print("=" * 60)
    print("民众渔业鲈鱼价格数据导入脚本")
    print("=" * 60)
    
    with open('/Users/zcy/IdeaProjects/fish-price-platform/数据地址', 'r') as f:
        urls = [line.strip() for line in f if line.strip().startswith('http')]
    
    print("\n共 {} 个URL".format(len(urls)))
    
    all_records = []
    success_count = 0
    fail_count = 0
    no_bass_count = 0
    
    for i, url in enumerate(urls):
        if (i + 1) % 20 == 0:
            print("\n处理进度: {}/{}".format(i + 1, len(urls)))
        
        article = fetch_article(url)
        if article and article.get('date') and article.get('prices'):
            for price_info in article['prices']:
                all_records.append({
                    'date': article['date'],
                    'spec': price_info['spec'],
                    'price': price_info['price'],
                    'url': url
                })
            success_count += 1
        elif article and article.get('date'):
            no_bass_count += 1
        else:
            fail_count += 1
        
        if len(all_records) >= 100:
            print("\n正在写入数据库 (当前缓存 {} 条)...".format(len(all_records)))
            inserted = save_to_database(all_records)
            print("成功写入 {} 条记录".format(inserted))
            all_records = []
    
    if all_records:
        print("\n正在写入数据库...")
        inserted = save_to_database(all_records)
        print("成功写入 {} 条记录".format(inserted))
    
    print("\n" + "=" * 60)
    print("处理完成！")
    print("成功解析: {} 个URL".format(success_count))
    print("无鲈鱼数据: {} 个URL".format(no_bass_count))
    print("解析失败: {} 个URL".format(fail_count))
    print("=" * 60)

if __name__ == '__main__':
    main()

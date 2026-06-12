#!/usr/bin/env python3
"""
修复数据库中错误的日期数据
通过访问微信文章获取实际发布时间来修正日期
"""

import pymysql
from playwright.sync_api import sync_playwright
import re
from datetime import datetime
import time
import sys

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_PASSWORD',
    'database': 'fish_prices'
}

def get_article_publish_date(page, url):
    """
    访问微信文章页面，获取文章的实际发布时间
    """
    try:
        page.goto(url, timeout=30000)
        page.wait_for_load_state('networkidle', timeout=10000)
        
        content = page.content()
        
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日\s+\d{1,2}:\d{1,2}', content)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            return datetime(year, month, day)
        
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    auto_fix = '--auto' in sys.argv
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT source_url, ts 
        FROM prices 
        WHERE market_id = 104 
          AND source_url LIKE "%mp.weixin.qq.com%"
          AND ts >= "2025-01-01"
        ORDER BY ts
    ''')
    rows = cursor.fetchall()
    
    print(f"找到 {len(rows)} 条需要检查的微信文章数据")
    
    url_date_map = {}
    for row in rows:
        url = row[0]
        if url not in url_date_map:
            url_date_map[url] = row[1]
    
    print(f"共 {len(url_date_map)} 个不同的URL需要检查")
    
    fixes = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for i, (url, db_date) in enumerate(url_date_map.items()):
            print(f"\n[{i+1}/{len(url_date_map)}] 检查: {url}")
            
            actual_date = get_article_publish_date(page, url)
            
            if actual_date:
                print(f"  数据库日期: {db_date.strftime('%Y-%m-%d')}")
                print(f"  实际发布日期: {actual_date.strftime('%Y-%m-%d')}")
                
                if actual_date.year != db_date.year:
                    print(f"  [需要修复] 年份不一致!")
                    fixes.append({
                        'url': url,
                        'old_date': db_date,
                        'new_date': actual_date
                    })
                else:
                    print(f"  [正确] 日期一致")
            else:
                print(f"  [警告] 无法获取发布时间")
            
            time.sleep(0.5)
        
        browser.close()
    
    print(f"\n\n=== 修复汇总 ===")
    print(f"需要修复的数据: {len(fixes)} 条")
    
    if fixes:
        if auto_fix:
            for fix in fixes:
                cursor.execute('''
                    UPDATE prices 
                    SET ts = %s 
                    WHERE source_url = %s AND ts = %s AND market_id = 104
                ''', (fix['new_date'], fix['url'], fix['old_date']))
                print(f"已更新: {fix['url']} {fix['old_date']} -> {fix['new_date']}")
            
            conn.commit()
            print(f"\n已修复 {len(fixes)} 条数据")
        else:
            print("\n运行 python fix_dates.py --auto 来自动修复")
    
    conn.close()

if __name__ == '__main__':
    main()

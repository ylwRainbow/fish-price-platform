#!/usr/bin/env python3
"""
泥鳅价格抓取脚本

从微信公众号文章中抓取泥鳅（20条）的价格数据并存入数据库
"""

import os
import re
import requests
from datetime import datetime
from typing import Optional, Tuple, List
from bs4 import BeautifulSoup

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from app.db import get_conn


def fetch_page_content(url: str) -> Optional[str]:
    """
    获取微信公众号文章内容
    
    Args:
        url: 微信公众号文章链接
        
    Returns:
        文章文本内容，失败返回None
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def parse_price_data(content: str) -> Optional[Tuple[str, float]]:
    """
    从页面内容中解析泥鳅20条的价格和日期
    
    Args:
        content: 页面文本内容
        
    Returns:
        (日期字符串, 价格) 或 None
    """
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    
    # 先尝试匹配完整日期格式 (YYYY年MM月DD日 或 YYYY-MM-DD)
    # 也处理 "2019-5- 3" 这种有空格的格式
    date_pattern = r'(\d{4})[年\-/]\s*(\d{1,2})[月\-/]\s*(\d{1,2})'
    date_match = re.search(date_pattern, text)
    
    if date_match:
        year = int(date_match.group(1))
        month = int(date_match.group(2))
        day = int(date_match.group(3))
        date_str = f"{year}-{month:02d}-{day:02d}"
    else:
        # 尝试匹配部分日期格式 (MM月DD日)，并从文章开头提取年份
        date_pattern2 = r'(\d{1,2})月(\d{1,2})日'
        date_match2 = re.search(date_pattern2, text)
        if date_match2:
            month = int(date_match2.group(1))
            day = int(date_match2.group(2))
            
            # 从文章开头2000字符内查找年份
            year_match = re.search(r'(20\d{2})', text[:2000])
            if year_match:
                year = int(year_match.group(1))
            else:
                # 如果找不到年份，使用当前年份并判断
                year = datetime.now().year
                if month > datetime.now().month:
                    year -= 1
            
            date_str = f"{year}-{month:02d}-{day:02d}"
        else:
            print("  Warning: Could not find date in content")
            return None
    
    # 尝试多种价格格式
    price = None
    
    # 格式1: 泥鳅 80条 9.7 50条 9.3 20条 9.3 (新格式)
    # 或者: 泥鳅 20条 8.3 7.8 (上周 本周)
    loach_idx = text.find('泥鳅')
    if loach_idx >= 0:
        segment = text[loach_idx:loach_idx+150]
        # 匹配 "20条 9.3" 或 "20条 8.3 7.8" (取最后一个数字作为本周价格)
        match = re.search(r'20\s*条\s+([\d\.]+)(?:-[\d\.]+)?(?:\s+([\d\.]+(?:-[\d\.]+)?))?(?:\s|$)', segment)
        if match:
            if match.group(2):
                # 有两个价格，取第二个（本周）
                price_str = match.group(2)
            else:
                # 只有一个价格
                price_str = match.group(1)
            
            if '-' in price_str:
                parts = price_str.split('-')
                try:
                    price = (float(parts[0]) + float(parts[1])) / 2
                except:
                    pass
            else:
                try:
                    price = float(price_str)
                except:
                    pass
    
    # 格式2: 泥鳅 20条 规格 价格
    if price is None:
        patterns = [
            r'泥鳅\s+.*?20\s*条\s+[\d\.]+(?:-[\d\.]+)?\s+([\d\.]+(?:-[\d\.]+)?)',
            r'泥鳅\s+20\s*条\s+[\d\.]+(?:-[\d\.]+)?\s+([\d\.]+(?:-[\d\.]+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                price_str = match.group(1)
                if '-' in price_str:
                    parts = price_str.split('-')
                    try:
                        price = (float(parts[0]) + float(parts[1])) / 2
                    except:
                        continue
                else:
                    try:
                        price = float(price_str)
                    except:
                        continue
                if price:
                    break
    
    # 格式3: 在泥鳅附近查找
    if price is None and loach_idx >= 0:
        segment = text[loach_idx:loach_idx+200]
        loach_20_match = re.search(r'20\s*条\s+([\d\.]+)(?:-[\d\.]+)?\s+([\d\.]+(?:-[\d\.]+)?)', segment)
        if loach_20_match:
            price_str = loach_20_match.group(2)
            if '-' in price_str:
                parts = price_str.split('-')
                try:
                    price = (float(parts[0]) + float(parts[1])) / 2
                except:
                    pass
            else:
                try:
                    price = float(price_str)
                except:
                    pass
    
    if price is None:
        print(f"  Warning: Could not parse loach 20 price")
        return None
    
    return date_str, price


def save_price(date_str: str, price: float, fish_id: int = 2, market_id: int = 104) -> bool:
    """
    保存价格数据到数据库
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        price: 价格
        fish_id: 鱼种ID，默认为泥鳅
        market_id: 市场ID，默认为民众渔业
        
    Returns:
        是否保存成功
    """
    conn = get_conn()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO prices (fish_id, market_id, price, ts, currency, unit, price_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE price = VALUES(price)
            """, (fish_id, market_id, price, date_str, 'CNY', 'kg', 'pond'))
        conn.commit()
        return True
    except Exception as e:
        print(f"  Error saving price: {e}")
        return False


def main():
    """
    主函数：读取URL列表，抓取数据并存入数据库
    """
    url_file = "/Users/zcy/IdeaProjects/fish-price-platform/数据地址"
    
    with open(url_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"共发现 {len(urls)} 个URL")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 处理: {url}")
        
        content = fetch_page_content(url)
        if not content:
            fail_count += 1
            continue
        
        result = parse_price_data(content)
        if not result:
            fail_count += 1
            continue
        
        date_str, price = result
        print(f"  日期: {date_str}, 泥鳅20条价格: {price} 元/斤")
        
        if save_price(date_str, price):
            print(f"  ✓ 已保存到数据库")
            success_count += 1
            results.append((date_str, price))
        else:
            print(f"  ✗ 保存失败")
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"处理完成: 成功 {success_count}, 失败 {fail_count}")
    
    if results:
        print("\n成功抓取的数据:")
        for date_str, price in sorted(results):
            print(f"  {date_str}: {price} 元/斤")


if __name__ == "__main__":
    main()

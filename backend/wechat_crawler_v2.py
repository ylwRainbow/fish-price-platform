# -*- coding: utf-8 -*-
"""
微信文章爬虫 - 自动抓取鲈鱼价格数据 (改进版)
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
import random


# 多个 User-Agent 轮流使用
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
]


def fetch_article_content(url, max_retries=3):
    """获取微信文章内容，带重试机制"""
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
            
            time.sleep(random.uniform(0.5, 2.0))
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            if '微信安全验证' in response.text or len(response.text) < 1000:
                print(f"  触发反爬机制，重试 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
            
            return response.text
        except Exception as e:
            print(f"获取文章失败 (尝试 {attempt + 1}/{max_retries}): {url} - {e}")
            if attempt < max_retries - 1:
                time.sleep(3 * (attempt + 1))
    
    return None


def extract_date_from_text(text):
    """从正文开头提取日期"""
    # 模式：流通价格信息（2025-1-2 更新）
    match = re.search(r'[\(（](\d{4})[-年](\d{1,2})[-月](\d{1,2})[日号]?更新[\)）]', text[:200])
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    # 模式：2025-1-2 更新
    match = re.search(r'(\d{4})[-年](\d{1,2})[-月](\d{1,2})[日号]?更新', text[:200])
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    return None


def extract_price_data(html, source_url):
    """从 HTML 中提取价格数据（改进版）"""
    soup = BeautifulSoup(html, 'lxml')
    
    # 提取文章标题 - 尝试多种选择器
    title = None
    for selector in ['h1.rich_media_title', 'h2.rich_media_title', 'h1.title', 'div.rich_media_title']:
        title = soup.select_one(selector)
        if title:
            break
    
    title_text = title.get_text(strip=True) if title else "未知标题"
    print(f"  标题：{title_text[:50]}...")
    
    # 提取正文内容
    content = soup.find('div', class_='rich_media_content')
    if not content:
        print(f"  警告：未找到正文内容")
        return []
    
    text = content.get_text()
    
    # 从正文开头提取日期
    article_date = extract_date_from_text(text)
    if article_date:
        print(f"  文章日期：{article_date}")
    else:
        print(f"  未找到文章日期")
        return []
    
    data_list = []
    
    # 模式 1：查找包含"加州鲈"或"海鲈"的段落
    # 数据可能是连续的数字，需要特殊处理
    for keyword in ['加州鲈', '海鲈']:
        if keyword in text:
            idx = text.find(keyword)
            # 提取关键词后面的价格数据（200 字符内）
            segment = text[idx:idx+200]
            print(f"  找到\"{keyword}\": {segment[:100]}...")
            
            # 提取所有数字（可能是价格）
            numbers = re.findall(r'(\d+\.?\d*)', segment)
            for num_str in numbers:
                try:
                    price = float(num_str)
                    # 过滤：价格通常在 5-50 之间
                    if 5 <= price <= 50:
                        data_list.append({
                            'date': article_date,
                            'price': price,
                            'source_url': source_url,
                            'original_text': segment[:100],
                            'title': title_text,
                            'fish_type': keyword
                        })
                        print(f"  -> 找到：{article_date} | {keyword} | {price}元/斤")
                except:
                    pass
    
    return data_list


def standardize_date(date_str):
    """将各种日期格式标准化为 YYYY-MM-DD"""
    if not date_str:
        return None
    
    date_str = date_str.strip()
    current_year = datetime.now().year
    
    # 模式 1: 2020 年 3 月 15 日
    match = re.match(r'(\d{4}) 年 (\d{1,2}) 月 (\d{1,2}) 日', date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    # 模式 2: 2020-03-15
    match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    # 模式 3: 3 月 15 日
    match = re.match(r'(\d{1,2}) 月 (\d{1,2}) 日', date_str)
    if match:
        month, day = match.groups()
        return f"{current_year}-{int(month):02d}-{int(day):02d}"
    
    return None


def crawl_all_articles(url_file):
    """爬取所有文章"""
    with open(url_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and line.startswith('http')]
    
    print(f"找到 {len(urls)} 个链接")
    
    all_data = []
    success_count = 0
    fail_count = 0
    empty_count = 0
    
    for idx, url in enumerate(urls, 1):
        print(f"\n[{idx}/{len(urls)}] 爬取：{url}")
        html = fetch_article_content(url)
        if html:
            data = extract_price_data(html, url)
            if data:
                all_data.extend(data)
                print(f"  提取 {len(data)} 条数据")
                success_count += 1
            else:
                print(f"  未找到价格数据")
                empty_count += 1
        else:
            fail_count += 1
        
        time.sleep(random.uniform(1.0, 2.0))
    
    print(f"\n{'='*60}")
    print(f"爬取完成：成功{success_count}个，失败{fail_count}个，无数据{empty_count}个")
    print(f"共采集到 {len(all_data)} 条数据")
    
    return all_data


if __name__ == '__main__':
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 60)
    print("微信文章爬虫 - 鲈鱼价格数据采集 (改进版)")
    print("=" * 60)
    
    data = crawl_all_articles('../数据地址')
    
    if data:
        print(f"\n数据示例:")
        for i, item in enumerate(data[:5], 1):
            print(f"{i}. {item['date']} | {item['price']}元/斤 | {item['title'][:30]}...")
    else:
        print("\n未采集到任何数据")

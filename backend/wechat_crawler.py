# -*- coding: utf-8 -*-
"""
微信文章爬虫 - 自动抓取鲈鱼价格数据
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
    'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
]


def fetch_article_content(url, max_retries=3):
    """获取微信文章内容，带重试机制"""
    for attempt in range(max_retries):
        try:
            # 随机选择 User-Agent
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # 添加随机延迟
            time.sleep(random.uniform(0.5, 2.0))
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 检查是否被反爬
            if '微信安全验证' in response.text or len(response.text) < 1000:
                print(f"  触发反爬机制，重试 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))  # 递增延迟
                    continue
            
            return response.text
        except Exception as e:
            print(f"获取文章失败 (尝试 {attempt + 1}/{max_retries}): {url} - {e}")
            if attempt < max_retries - 1:
                time.sleep(3 * (attempt + 1))
    
    return None


def standardize_date(date_str):
    """将各种日期格式标准化为 YYYY-MM-DD"""
    if not date_str:
        return None
    
    # 去除空格
    date_str = date_str.strip()
    
    # 当前年份（用于处理没有年份的日期）
    current_year = datetime.now().year
    
    # 模式 1: 2020 年 3 月 15 日 或 2020 年 03 月 15 日
    match = re.match(r'(\d{4}) 年 (\d{1,2}) 月 (\d{1,2}) 日', date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    # 模式 2: 2020-03-15 或 2020-3-15
    match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    # 模式 3: 3 月 15 日 (假设当前年份)
    match = re.match(r'(\d{1,2}) 月 (\d{1,2}) 日', date_str)
    if match:
        month, day = match.groups()
        return f"{current_year}-{int(month):02d}-{int(day):02d}"
    
    # 模式 4: 03-15 或 3-15 (假设当前年份)
    match = re.match(r'(\d{1,2})-(\d{1,2})', date_str)
    if match:
        month, day = match.groups()
        return f"{current_year}-{int(month):02d}-{int(day):02d}"
    
    # 模式 5: 2020.03.15
    match = re.match(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    return None


def extract_price_data(html, source_url):
    """从 HTML 中提取价格数据"""
    soup = BeautifulSoup(html, 'lxml')
    
    # 提取文章标题
    title = soup.find('h2', class_='rich_media_title')
    title_text = title.get_text(strip=True) if title else "未知标题"
    
    # 提取正文内容
    content = soup.find('div', class_='rich_media_content')
    if not content:
        print(f"  警告：未找到正文内容 - {source_url}")
        return []
    
    text = content.get_text()
    
    # 更灵活的正则匹配价格信息
    patterns = [
        # 2020 年 3 月 15 日 鲈鱼价格 12.5 元/斤
        r'(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日号])[^0-9]*(鲈鱼 | 海鲈)[^0-9]*价格 [为是]?(\d+\.?\d*)\s*[元斤]',
        # 3 月 15 日 鲈鱼价格 12.5 元
        r'(\d{1,2}月\d{1,2}日)[^0-9]*(鲈鱼 | 海鲈)[^0-9]*价格 [为是]?(\d+\.?\d*)\s*[元斤]',
        # 鲈鱼 12.5 元/斤 2020 年 3 月 15 日
        r'(鲈鱼 | 海鲈)[^0-9]*(\d+\.?\d*)\s*[元斤][^0-9]*(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日号])',
        # 简单模式：日期 + 数字 + 元
        r'(\d{4}[-年./]\d{1,2}[-月./]\d{1,2}[日号])[^0-9]*(\d+\.?\d*)\s*元',
        # 3 月 15 日，价格 12.5 元
        r'(\d{1,2}月\d{1,2}日)[^0-9]*(\d+\.?\d*)\s*元',
    ]
    
    data_list = []
    seen_dates = set()  # 去重
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # 根据模式调整分组索引
            if pattern.startswith(r'(\d{4}'):
                if '鲈鱼' in pattern or '海鲈' in pattern:
                    date_str = match.group(1)
                    price = float(match.group(3))
                else:
                    date_str = match.group(1)
                    price = float(match.group(2))
            elif pattern.startswith(r'(鲈鱼'):
                date_str = match.group(3)
                price = float(match.group(2))
            elif pattern.startswith(r'(\d{1,2}月'):
                if '鲈鱼' in pattern or '海鲈' in pattern:
                    date_str = match.group(1)
                    price = float(match.group(3))
                else:
                    date_str = match.group(1)
                    price = float(match.group(2))
            else:
                continue
            
            # 标准化日期格式
            date_standardized = standardize_date(date_str)
            
            # 去重：如果已经有这个日期的数据，跳过
            if date_standardized and date_standardized not in seen_dates:
                seen_dates.add(date_standardized)
                data_list.append({
                    'date': date_standardized,
                    'price': price,
                    'source_url': source_url,
                    'original_text': match.group(0),
                    'title': title_text
                })
    
    return data_list


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
        print(f"[{idx}/{len(urls)}] 爬取：{url}")
        html = fetch_article_content(url)
        if html:
            data = extract_price_data(html, url)
            if data:
                all_data.extend(data)
                print(f"  -> 提取 {len(data)} 条数据")
                success_count += 1
            else:
                print(f"  -> 未找到价格数据")
                empty_count += 1
        else:
            fail_count += 1
        
        # 随机延迟，避免被封
        time.sleep(random.uniform(1.0, 3.0))
    
    print(f"\n爬取完成：成功{success_count}个，失败{fail_count}个，无数据{empty_count}个")
    print(f"共采集到 {len(all_data)} 条数据")
    
    return all_data


if __name__ == '__main__':
    import os
    # 切换到 backend 目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 60)
    print("微信文章爬虫 - 鲈鱼价格数据采集")
    print("=" * 60)
    
    # 爬取数据
    data = crawl_all_articles('../数据地址')
    
    # 显示结果
    if data:
        print(f"\n数据示例:")
        for i, item in enumerate(data[:3], 1):
            print(f"{i}. {item['date']} | {item['price']}元/斤 | {item['title']}")
    else:
        print("\n未采集到任何数据")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜狗搜索自动化 - 终极版 - 更多关键词
"""
import asyncio
import re
from playwright.async_api import async_playwright


async def search_and_collect():
    """使用 Playwright 执行搜索并提取链接"""
    
    # 终极搜索关键词列表 - 覆盖更多长尾词
    keywords = [
        # 原有 14 个
        'site:sohu.com 湖州 加州鲈 水产前沿',
        'site:sohu.com 湖州 加州鲈 杰大饲料',
        'site:sohu.com 湖州 鲈鱼价格',
        'site:m.sohu.com 加州鲈 周报',
        'site:sohu.com 浙江 加州鲈 价格',
        'site:sohu.com 湖州 鲈鱼 行情',
        'site:sohu.com 加州鲈 鱼价 周报',
        'site:sohu.com 水产前沿 鲈鱼',
        'site:sohu.com 杰大饲料 鲈鱼',
        'site:sohu.com 湖州 鱼价 上涨',
        'site:sohu.com 湖州 鱼价 下跌',
        'site:sohu.com 加州鲈 养殖',
        'site:sohu.com 鲈鱼 市场 行情',
        'site:sohu.com 淡水鱼 价格 周报',
        
        # 新增 16 个 - 更多长尾词
        'site:sohu.com 湖州 加州鲈 8 两',
        'site:sohu.com 加州鲈 统货 价格',
        'site:sohu.com 鲈鱼 塘口价',
        'site:sohu.com 加州鲈 新鱼',
        'site:sohu.com 湖州 水产品 价格',
        'site:sohu.com 浙江 鲈鱼 周报',
        'site:sohu.com 加州鲈 上市',
        'site:sohu.com 鲈鱼 收购价',
        'site:sohu.com 加州鲈 出鱼',
        'site:sohu.com 鲈鱼 流通',
        'site:sohu.com 加州鲈 投苗',
        'site:sohu.com 鲈鱼 饲料',
        'site:sohu.com 加州鲈 病害',
        'site:sohu.com 鲈鱼 养殖技术',
        'site:sohu.com 加州鲈 利润',
        'site:sohu.com 鲈鱼 市场预测',
    ]
    
    all_urls = set()
    article_ids = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        for i, keyword in enumerate(keywords, 1):
            print(f"\n[{i}/{len(keywords)}] 搜索：{keyword}")
            
            try:
                search_url = f'https://www.sogou.com/web?query={keyword}'
                await page.goto(search_url, timeout=30000)
                await page.wait_for_timeout(5000)
                
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(3000)
                
                content = await page.content()
                matches = re.findall(r'/a/(\d{9,})', content)
                
                found_count = 0
                for article_id in matches:
                    if article_id not in article_ids:
                        article_ids.add(article_id)
                        standard_url = f'https://www.sohu.com/a/{article_id}_210667'
                        all_urls.add(standard_url)
                        found_count += 1
                        print(f"  ✓ 发现文章：{article_id}")
                
                print(f"  找到 {found_count} 篇相关文章")
                
                import random
                wait_time = random.uniform(5, 8)
                print(f"  等待 {wait_time:.1f} 秒...")
                await page.wait_for_timeout(wait_time * 1000)
                
            except Exception as e:
                print(f"  搜索失败：{e}")
                continue
        
        await browser.close()
    
    return list(all_urls)


def merge_to_known(urls, known_file='backend/sohu_known_urls.txt'):
    """合并到已知链接文件"""
    import os
    
    existing = set()
    if os.path.exists(known_file):
        with open(known_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and line.startswith('http'):
                    existing.add(line)
    
    merged = existing.union(set(urls))
    
    with open(known_file, 'w', encoding='utf-8') as f:
        for url in sorted(merged):
            f.write(url + '\n')
    
    new_count = len(merged) - len(existing)
    print(f"\n合并到 {known_file}，共 {len(merged)} 个链接（新增 {new_count} 个）")
    return merged


async def main():
    print("=" * 60)
    print("搜狗搜索自动化 - 终极版（30 个关键词）")
    print("=" * 60)
    
    urls = await search_and_collect()
    
    if urls:
        print(f"\n共收集到 {len(urls)} 个链接")
        merge_to_known(urls)
    else:
        print("\n未收集到链接")
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())

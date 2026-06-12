#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜狗搜索自动化 - 改进版 - 使用 Playwright 批量发现搜狐网文章
"""
import asyncio
import re
from playwright.async_api import async_playwright


async def search_and_collect():
    """使用 Playwright 执行搜索并提取链接"""
    
    # 搜索关键词列表
    keywords = [
        'site:sohu.com 湖州 加州鲈 水产前沿',
        'site:sohu.com 湖州 加州鲈 杰大饲料',
        'site:sohu.com 湖州 鲈鱼价格',
        'site:m.sohu.com 加州鲈 周报',
        'site:sohu.com 浙江 加州鲈 价格',
        'site:sohu.com 湖州 鲈鱼 行情',
    ]
    
    all_urls = set()
    article_ids = set()
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        for i, keyword in enumerate(keywords, 1):
            print(f"\n[{i}/{len(keywords)}] 搜索：{keyword}")
            
            try:
                # 访问搜狗搜索
                search_url = f'https://www.sogou.com/web?query={keyword}'
                await page.goto(search_url, timeout=30000)
                await page.wait_for_timeout(5000)  # 等待页面加载
                
                # 滚动页面加载更多内容
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(3000)
                
                # 获取页面所有文本
                content = await page.content()
                
                # 使用正则表达式提取所有文章 ID
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
                
                # 保守模式：等待 5-10 秒
                import random
                wait_time = random.uniform(5, 10)
                print(f"  等待 {wait_time:.1f} 秒...")
                await page.wait_for_timeout(wait_time * 1000)
                
            except Exception as e:
                print(f"  搜索失败：{e}")
                continue
        
        await browser.close()
    
    return list(all_urls)


def save_urls(urls, output_file='backend/sohu_playwright_urls.txt'):
    """保存 URL 到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in sorted(urls):
            f.write(url + '\n')
    print(f"\n保存 {len(urls)} 个链接到 {output_file}")


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
    
    # 合并
    merged = existing.union(set(urls))
    
    with open(known_file, 'w', encoding='utf-8') as f:
        for url in sorted(merged):
            f.write(url + '\n')
    
    new_count = len(merged) - len(existing)
    print(f"合并到 {known_file}，共 {len(merged)} 个链接（新增 {new_count} 个）")
    return merged


async def main():
    print("=" * 60)
    print("搜狗搜索自动化 - 搜狐网文章收集（改进版）")
    print("=" * 60)
    
    # 执行搜索
    urls = await search_and_collect()
    
    if urls:
        print(f"\n共收集到 {len(urls)} 个链接")
        
        # 保存
        save_urls(urls)
        
        # 合并到已知链接
        merge_to_known(urls)
    else:
        print("\n未收集到链接")
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())

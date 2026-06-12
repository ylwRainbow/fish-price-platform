# -*- coding: utf-8 -*-
"""
调试微信文章 HTML 结构 - 测试多篇文章
"""
import requests
from bs4 import BeautifulSoup
import re

urls = [
    "https://mp.weixin.qq.com/s/ekCDAxg_bOrb29xJUuAKDw",
    "https://mp.weixin.qq.com/s/NPT07xckDfTpDapvCluP3Q",
    "https://mp.weixin.qq.com/s/LaxFqxfE88P9S6VYHrhSXA",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

for idx, url in enumerate(urls, 1):
    print(f"\n{'='*60}")
    print(f"文章 {idx}: {url}")
    print('='*60)
    
    response = requests.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, 'lxml')
    
    # 获取标题
    title = soup.find('h2', class_='rich_media_title')
    title_text = title.get_text(strip=True) if title else "未知标题"
    print(f"标题：{title_text}")
    
    # 获取正文
    content = soup.find('div', class_='rich_media_content')
    if content:
        text = content.get_text()
        
        # 查找所有鱼类名称
        fish_names = ['鲈鱼', '海鲈', '草鱼', '鲤鱼', '鲫鱼', '石斑', '罗非', '黄颡', '鳜鱼', '加州鲈']
        found_fish = []
        for fish in fish_names:
            if fish in text:
                found_fish.append(fish)
        
        print(f"找到的鱼类：{found_fish if found_fish else '无'}")
        
        # 查找所有价格相关的行
        price_lines = []
        for line in text.split('\n'):
            if any(fish in line for fish in fish_names) and ('元' in line or '价' in line):
                price_lines.append(line.strip()[:100])
        
        if price_lines:
            print(f"价格相关行 ({len(price_lines)}条):")
            for line in price_lines[:5]:
                print(f"  - {line}")
        else:
            print("未找到价格相关行")
    else:
        print("未找到正文内容")

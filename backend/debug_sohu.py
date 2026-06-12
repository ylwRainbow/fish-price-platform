# -*- coding: utf-8 -*-
"""
调试搜狐网数据结构
"""
import requests
from bs4 import BeautifulSoup

# 测试两个不同类型的链接
urls = {
    '水产前沿_PC': 'https://www.sohu.com/a/516858961_210667',
    '杰大饲料_移动': 'https://m.sohu.com/a/660709304_210667/',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

for source, url in urls.items():
    print(f"\n{'='*60}")
    print(f"测试：{source}")
    print(f"URL: {url}")
    print('='*60)
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"状态码：{response.status_code}")
        print(f"内容长度：{len(response.text)}")
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 提取标题
        title = soup.find('h1') or soup.find('h2')
        if title:
            print(f"标题：{title.get_text(strip=True)[:100]}")
        
        # 提取正文
        content = soup.find('div', class_='content') or soup.find('article')
        if not content:
            # 尝试其他选择器
            for selector in ['div.article', 'div.main', 'section']:
                content = soup.select_one(selector)
                if content:
                    break
        
        if content:
            text = content.get_text()
            
            # 查找"湖州"相关的内容
            if '湖州' in text:
                print("\n找到'湖州'关键词！")
                # 显示包含湖州的段落
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if '湖州' in line and ('鲈' in line or '鱼' in line):
                        print(f"  相关行：{line.strip()[:200]}")
            
            # 查找价格表格
            tables = soup.find_all('table')
            if tables:
                print(f"\n找到 {len(tables)} 个表格")
                for i, table in enumerate(tables[:2]):
                    print(f"\n表格 {i+1}:")
                    rows = table.find_all('tr')
                    for row in rows[:5]:
                        cells = row.find_all(['td', 'th'])
                        cell_texts = [c.get_text(strip=True) for c in cells]
                        if cell_texts:
                            print(f"  {' | '.join(cell_texts[:5])}")
        else:
            print("未找到正文内容")
            
    except Exception as e:
        print(f"错误：{e}")

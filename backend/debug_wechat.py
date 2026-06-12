# -*- coding: utf-8 -*-
"""
调试微信文章 HTML 结构
"""
import requests
from bs4 import BeautifulSoup

url = "https://mp.weixin.qq.com/s/ekCDAxg_bOrb29xJUuAKDw"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

print(f"获取文章：{url}")
response = requests.get(url, headers=headers, timeout=30)
print(f"状态码：{response.status_code}")
print(f"内容长度：{len(response.text)}")

# 保存 HTML 到文件
with open('/tmp/test_article.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print("\nHTML 已保存到 /tmp/test_article.html")

# 分析 HTML 结构
soup = BeautifulSoup(response.text, 'lxml')

# 查找所有可能的内容容器
print("\n=== 查找内容容器 ===")
for tag in ['h2', 'div']:
    elements = soup.find_all(tag)
    if elements:
        print(f"\n<{tag}> 标签数量：{len(elements)}")
        for i, elem in enumerate(elements[:3]):
            class_name = elem.get('class', [])
            text = elem.get_text(strip=True)[:100]
            print(f"  {i+1}. class={class_name}, 文本：{text}...")

# 查找包含"鲈鱼"或"价格"的文本
print("\n=== 查找关键词 ===")
text = soup.get_text()
if '鲈鱼' in text:
    print("找到'鲈鱼'关键词")
    # 显示包含鲈鱼的段落
    for p in soup.find_all(['p', 'span', 'div']):
        if '鲈鱼' in p.get_text():
            print(f"  - {p.get_text(strip=True)[:200]}")
else:
    print("未找到'鲈鱼'关键词")

if '价格' in text:
    print("找到'价格'关键词")
else:
    print("未找到'价格'关键词")

# 显示前 500 个字符
print("\n=== HTML 开头 500 字符 ===")
print(response.text[:500])

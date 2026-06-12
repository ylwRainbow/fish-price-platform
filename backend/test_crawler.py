# -*- coding: utf-8 -*-
"""
测试爬虫 - 只爬取前 10 个链接
"""
import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')

from wechat_crawler_v2 import crawl_all_articles

# 只读取前 10 个链接
with open('../数据地址', 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip() and line.startswith('http')][:10]

# 保存到临时文件
with open('/tmp/test_urls.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(urls))

print(f"测试前 10 个链接:")
for i, url in enumerate(urls, 1):
    print(f"{i}. {url}")

data = crawl_all_articles('/tmp/test_urls.txt')

if data:
    print(f"\n成功采集到 {len(data)} 条数据:")
    for i, item in enumerate(data, 1):
        print(f"{i}. {item['date']} | {item['price']}元/斤")
else:
    print("\n未采集到任何数据")

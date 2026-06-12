# -*- coding: utf-8 -*-
"""
智能链接收集器 - 自动发现和收集搜狐网历史文章链接
"""
import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime


class SmartLinkCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        self.known_urls = set()
    
    def load_existing_urls(self, url_file='backend/sohu_known_urls.txt'):
        """加载已有的链接"""
        if os.path.exists(url_file):
            with open(url_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        self.known_urls.add(line)
        print(f"已加载 {len(self.known_urls)} 个现有链接")
    
    def extract_from_search_results(self, search_url):
        """从搜索结果页面提取链接（需要手动操作）"""
        print(f"打开搜索链接：{search_url}")
        print("请在浏览器中打开上述链接，复制搜狐网文章 URL 到 clipboard")
        # 这个方法需要用户手动复制链接
        pass
    
    def generate_search_links(self):
        """生成搜索链接列表"""
        keywords = [
            '加州鲈 湖州 水产前沿',
            '加州鲈 湖州 杰大饲料',
            '鲈鱼价格 湖州',
        ]
        years = list(range(2020, 2025))
        
        search_links = []
        for keyword in keywords:
            for year in years:
                query = f'site:sohu.com "{keyword}" after:{year}-01-01 before:{year}-12-31'
                google_url = f'https://www.google.com/search?q={requests.utils.quote(query)}'
                search_links.append({
                    'keyword': keyword,
                    'year': year,
                    'url': google_url
                })
        
        return search_links
    
    def save_urls(self, output_file='backend/sohu_urls_batch.txt'):
        """保存收集到的链接"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for url in sorted(self.known_urls):
                f.write(url + '\n')
        print(f"保存 {len(self.known_urls)} 个链接到 {output_file}")


if __name__ == '__main__':
    # 测试链接收集器
    collector = SmartLinkCollector()
    collector.load_existing_urls()
    
    # 生成搜索链接
    search_links = collector.generate_search_links()
    print(f"\n生成了 {len(search_links)} 个搜索链接:")
    for link in search_links[:5]:  # 只显示前 5 个
        print(f"  {link['keyword']} ({link['year']}年): {link['url']}")
    
    if len(search_links) > 5:
        print(f"  ... 还有 {len(search_links) - 5} 个搜索链接")
    
    # 保存链接
    collector.save_urls()

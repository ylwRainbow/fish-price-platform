#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜狐网 AI 自动化链接收集器
通过 AI 搜索逐个发现历史文章链接
"""
import requests
import re
import os
import json
from datetime import datetime
import time


class AILinkCollector:
    """AI 自动化链接收集器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        self.collected_urls = []
        self.article_ids = set()
    
    def load_seed_urls(self, url_file='backend/sohu_known_urls.txt'):
        """加载种子链接"""
        if os.path.exists(url_file):
            with open(url_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        self.collected_urls.append(line)
                        match = re.search(r'/a/(\d+)', line)
                        if match:
                            self.article_ids.add(match.group(1))
        print(f"已加载 {len(self.collected_urls)} 个种子链接")
    
    def search_articles_by_ai(self, query):
        """
        使用 AI 搜索相关文章
        通过搜索引擎 API 发现相关搜狐网文章
        """
        print(f"\nAI 搜索：{query}")
        
        # 使用 DuckDuckGo 搜索（无需 API key）
        search_url = f'https://html.duckduckgo.com/html/?q=site:sohu.com+{requests.utils.quote(query)}'
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            results = []
            
            # 解析搜索结果
            for match in re.finditer(r'sohu\.com/a/(\d+)', response.text):
                article_id = match.group(1)
                if article_id not in self.article_ids:
                    url = f'https://www.sohu.com/a/{article_id}_210667'
                    results.append(url)
                    self.article_ids.add(article_id)
                    print(f"  ✓ 发现：{url}")
            
            print(f"  找到 {len(results)} 篇新文章")
            return results
            
        except Exception as e:
            print(f"  搜索失败：{e}")
            return []
    
    def generate_search_queries(self):
        """生成 AI 搜索查询列表"""
        queries = []
        
        # 按年份和关键词组合
        keywords = [
            '湖州 加州鲈 价格',
            '湖州 鲈鱼 水产前沿',
            '湖州 加州鲈 杰大饲料',
            '浙江 加州鲈 周报',
            '湖州 鲈鱼 行情',
        ]
        
        years = ['2020', '2021', '2022', '2023', '2024']
        
        for keyword in keywords:
            for year in years:
                queries.append(f'{keyword} {year}年')
        
        return queries
    
    def collect_batch(self, max_queries=20):
        """批量收集链接"""
        queries = self.generate_search_queries()
        
        print(f"\n开始 AI 搜索，共 {len(queries)} 个查询")
        
        all_found = []
        for i, query in enumerate(queries[:max_queries], 1):
            print(f"\n[{i}/{max_queries}] ", end='')
            found = self.search_articles_by_ai(query)
            all_found.extend(found)
            self.collected_urls.extend(found)
            
            # 延迟避免频率限制
            time.sleep(2)
        
        return all_found
    
    def save_urls(self, output_file='backend/sohu_ai_collected_urls.txt'):
        """保存收集到的链接"""
        # 去重
        unique_urls = list(set(self.collected_urls))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for url in sorted(unique_urls):
                f.write(url + '\n')
        
        print(f"\n保存 {len(unique_urls)} 个链接到 {output_file}")
        return unique_urls
    
    def merge_to_known(self, known_file='backend/sohu_known_urls.txt'):
        """合并到已知链接文件"""
        existing = set()
        if os.path.exists(known_file):
            with open(known_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        existing.add(line)
        
        # 合并
        merged = existing.union(set(self.collected_urls))
        
        with open(known_file, 'w', encoding='utf-8') as f:
            for url in sorted(merged):
                f.write(url + '\n')
        
        new_count = len(merged) - len(existing)
        print(f"合并到 {known_file}，共 {len(merged)} 个链接（新增 {new_count} 个）")
        return merged


def main():
    """主函数"""
    print("=" * 60)
    print("搜狐网 AI 自动化链接收集器")
    print("=" * 60)
    
    collector = AILinkCollector()
    
    # 1. 加载种子链接
    print("\n【步骤 1】加载种子链接...")
    collector.load_seed_urls()
    
    # 2. AI 搜索收集
    print("\n【步骤 2】AI 搜索相关文章...")
    collector.collect_batch(max_queries=30)
    print(f"\n当前共收集 {len(collector.collected_urls)} 个链接")
    
    # 3. 保存结果
    print("\n【步骤 3】保存结果...")
    collector.save_urls()
    
    # 4. 合并到已知链接
    print("\n【步骤 4】合并到已知链接文件...")
    collector.merge_to_known()
    
    print("\n" + "=" * 60)
    print(f"AI 收集完成！")
    print("=" * 60)
    print(f"\n统计:")
    print(f"  - 总计：{len(collector.collected_urls)} 个链接")
    print(f"  - 新增：{len(set(collector.collected_urls)) - 2} 个")


if __name__ == '__main__':
    main()

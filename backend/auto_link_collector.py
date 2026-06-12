#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜狐网自动化链接收集器 - 无需手动操作
通过搜索引擎和已知链接自动发现更多相关文章
"""
import requests
from bs4 import BeautifulSoup
import re
import os
import json
from datetime import datetime
import time
import random


class AutoLinkCollector:
    """自动化链接收集器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.collected_urls = set()
        self.known_article_ids = set()
    
    def load_seed_urls(self, url_file='backend/sohu_known_urls.txt'):
        """加载种子链接"""
        if os.path.exists(url_file):
            with open(url_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        self.collected_urls.add(line)
                        # 提取文章 ID
                        match = re.search(r'/a/(\d+)', line)
                        if match:
                            self.known_article_ids.add(match.group(1))
        print(f"已加载 {len(self.collected_urls)} 个种子链接，{len(self.known_article_ids)} 个文章 ID")
    
    def scan_article_ids(self, start_id=100000000, end_id=999999999, batch_size=1000):
        """
        扫描文章 ID 范围，发现相关文章
        搜狐网文章 ID 通常是 9 位数字
        """
        print(f"\n开始扫描文章 ID 范围：{start_id} - {end_id}")
        
        found_urls = []
        tested_ids = 0
        
        # 随机采样测试
        test_ids = random.sample(range(start_id, end_id), min(batch_size * 10, end_id - start_id))
        
        for article_id in test_ids:
            url = f'https://www.sohu.com/a/{article_id}_210667'
            tested_ids += 1
            
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code == 200 and len(response.text) > 5000:
                    # 检查是否包含关键词
                    if any(kw in response.text for kw in ['湖州', '加州鲈', '鲈鱼', '水产前沿', '杰大饲料']):
                        found_urls.append(url)
                        self.collected_urls.add(url)
                        self.known_article_ids.add(str(article_id))
                        print(f"  ✓ 发现相关文章：{url}")
            except:
                pass
            
            # 每 100 个 ID 暂停一下
            if tested_ids % 100 == 0:
                print(f"  已测试 {tested_ids} 个 ID，发现 {len(found_urls)} 篇文章")
                time.sleep(1)
        
        print(f"\nID 扫描完成：测试{tested_ids}个，发现{len(found_urls)}篇相关文章")
        return found_urls
    
    def extract_related_articles(self, url):
        """从文章页面提取相关推荐文章链接"""
        related_urls = []
        
        try:
            html = self.session.get(url, timeout=10).text
            soup = BeautifulSoup(html, 'lxml')
            
            # 提取页面中的所有搜狐网链接
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'sohu.com/a/' in href:
                    # 标准化 URL
                    if href.startswith('//'):
                        href = 'https:' + href
                    elif href.startswith('/'):
                        href = 'https://www.sohu.com' + href
                    
                    # 检查是否是文章链接
                    if re.search(r'/a/\d+', href):
                        related_urls.append(href)
                        self.collected_urls.add(href)
            
        except Exception as e:
            print(f"  提取相关文章失败：{e}")
        
        return related_urls
    
    def search_bing(self, keyword, year):
        """使用 Bing 搜索搜狐网文章（作为 Google 的替代）"""
        print(f"\n搜索：{keyword} ({year}年)")
        
        found_urls = []
        
        # Bing 搜索语法：site:sohu.com keyword
        query = f'site:sohu.com {keyword}'
        search_url = f'https://www.bing.com/search?q={requests.utils.quote(query)}'
        
        try:
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取搜索结果
            for result in soup.select('li.b_algo'):
                title_tag = result.select_one('h2 a')
                if title_tag and title_tag.get('href'):
                    url = title_tag['href']
                    if 'sohu.com/a/' in url:
                        found_urls.append(url)
                        self.collected_urls.add(url)
                        print(f"  ✓ 找到：{url[:80]}...")
            
            print(f"  找到 {len(found_urls)} 个链接")
            
        except Exception as e:
            print(f"  搜索失败：{e}")
        
        return found_urls
    
    def collect_from_keywords(self, keywords=None, years=None):
        """从关键词批量搜索"""
        if keywords is None:
            keywords = [
                '湖州 加州鲈 水产前沿',
                '湖州 加州鲈 杰大饲料',
                '湖州 鲈鱼价格',
                '浙江 加州鲈 周报',
            ]
        
        if years is None:
            years = list(range(2020, 2025))
        
        all_found = []
        
        for keyword in keywords:
            for year in years:
                found = self.search_bing(keyword, year)
                all_found.extend(found)
                time.sleep(random.uniform(2, 4))  # 避免频率限制
        
        return all_found
    
    def save_urls(self, output_file='backend/sohu_auto_collected_urls.txt'):
        """保存收集到的链接"""
        # 去重并排序
        sorted_urls = sorted(self.collected_urls)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for url in sorted_urls:
                f.write(url + '\n')
        
        print(f"\n保存 {len(sorted_urls)} 个链接到 {output_file}")
        return sorted_urls
    
    def merge_to_known(self, known_file='backend/sohu_known_urls.txt'):
        """合并到已知链接文件"""
        # 加载现有链接
        existing = set()
        if os.path.exists(known_file):
            with open(known_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        existing.add(line)
        
        # 合并
        merged = existing.union(self.collected_urls)
        
        # 保存
        with open(known_file, 'w', encoding='utf-8') as f:
            for url in sorted(merged):
                f.write(url + '\n')
        
        print(f"合并后共 {len(merged)} 个链接（新增 {len(merged) - len(existing)} 个）")
        return merged


def main():
    """主函数"""
    print("=" * 60)
    print("搜狐网自动化链接收集器")
    print("=" * 60)
    
    collector = AutoLinkCollector()
    
    # 1. 加载种子链接
    print("\n【步骤 1】加载种子链接...")
    collector.load_seed_urls()
    
    # 2. 从关键词搜索
    print("\n【步骤 2】使用 Bing 搜索相关文章...")
    collector.collect_from_keywords()
    print(f"当前收集到 {len(collector.collected_urls)} 个链接")
    
    # 3. 从已知文章提取相关推荐
    print("\n【步骤 3】从已知文章提取相关推荐...")
    seed_urls = list(collector.collected_urls)[:10]  # 只用前 10 个测试
    for url in seed_urls:
        print(f"处理：{url[:60]}...")
        collector.extract_related_articles(url)
        time.sleep(1)
    
    print(f"当前收集到 {len(collector.collected_urls)} 个链接")
    
    # 4. 保存结果
    print("\n【步骤 4】保存结果...")
    collector.save_urls()
    
    # 5. 合并到已知链接
    print("\n【步骤 5】合并到已知链接文件...")
    collector.merge_to_known()
    
    print("\n" + "=" * 60)
    print(f"自动化收集完成！共收集 {len(collector.collected_urls)} 个链接")
    print("=" * 60)
    
    # 显示统计
    print(f"\n统计:")
    print(f"  - 种子链接：{len(collector.known_article_ids)} 个")
    print(f"  - 新增链接：{len(collector.collected_urls) - len(collector.known_article_ids)} 个")
    print(f"  - 总计：{len(collector.collected_urls)} 个")


if __name__ == '__main__':
    main()

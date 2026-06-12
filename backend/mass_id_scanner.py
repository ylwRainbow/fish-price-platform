#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜狐网大规模 ID 扫描器
通过大范围扫描发现历史文章
"""
import requests
import re
import os
import time
import random
from datetime import datetime


class MassScanner:
    """大规模 ID 扫描器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.found_urls = []
        self.known_ids = set()
        self.load_known_ids()
    
    def load_known_ids(self):
        """加载已知 ID"""
        url_file = 'backend/sohu_known_urls.txt'
        if os.path.exists(url_file):
            with open(url_file, 'r', encoding='utf-8') as f:
                for line in f:
                    match = re.search(r'/a/(\d+)', line)
                    if match:
                        self.known_ids.add(match.group(1))
        print(f"加载 {len(self.known_ids)} 个已知 ID")
    
    def check_article_fast(self, article_id):
        """快速检查文章"""
        url = f'https://www.sohu.com/a/{article_id}_210667'
        
        try:
            response = self.session.get(url, timeout=3)
            
            if response.status_code == 200 and len(response.text) > 8000:
                # 快速关键词检查
                if '湖州' in response.text or '加州鲈' in response.text or '鲈鱼' in response.text:
                    # 提取标题
                    title_match = re.search(r'<title>([^<]+)</title>', response.text)
                    if title_match:
                        title = title_match.group(1)
                        # 二次验证标题
                        if any(kw in title for kw in ['湖州', '加州鲈', '鲈鱼', '水产', '杰大']):
                            print(f"  ✓ {article_id}: {title[:50]}...")
                            self.found_urls.append(url)
                            self.known_ids.add(article_id)
                            return True
        except:
            pass
        
        return False
    
    def scan_sequential(self, start_id, count, step=1):
        """顺序扫描"""
        print(f"\n开始扫描：从 {start_id} 开始，共 {count} 个")
        
        found = 0
        for i in range(count):
            article_id = str(start_id + i * step)
            
            if article_id in self.known_ids:
                continue
            
            if self.check_article_fast(article_id):
                found += 1
            
            # 每 100 个暂停
            if i % 100 == 0 and i > 0:
                print(f"  进度：{i}/{count}, 已发现：{found}")
                time.sleep(1)
            
            # 随机延迟
            time.sleep(random.uniform(0.3, 1.0))
        
        print(f"\n扫描完成：发现 {found} 篇新文章")
        return found
    
    def scan_targeted(self):
        """针对性扫描（基于已知 ID 的模式）"""
        print("\n针对性扫描：分析已知 ID 模式...")
        
        # 已知 ID: 516858961 (2022-01), 660709304 (2023-03)
        # 推测 ID 增长规律，在相似范围搜索
        
        test_ranges = [
            (500000000, 550000000, 10000),  # 2021-2022 年范围
            (600000000, 700000000, 10000),  # 2022-2023 年范围
            (800000000, 950000000, 10000),  # 2023-2024 年范围
        ]
        
        total_found = 0
        
        for start, end, step in test_ranges:
            print(f"\n扫描范围：{start} - {end} (步长{step})")
            
            for test_id in range(start, end, step):
                if self.check_article_fast(str(test_id)):
                    total_found += 1
                
                time.sleep(random.uniform(0.5, 2.0))
        
        return total_found
    
    def save_results(self):
        """保存结果"""
        # 读取现有
        existing = []
        url_file = 'backend/sohu_known_urls.txt'
        if os.path.exists(url_file):
            with open(url_file, 'r', encoding='utf-8') as f:
                existing = [line.strip() for line in f if line.strip().startswith('http')]
        
        # 合并
        all_urls = list(set(existing + self.found_urls))
        all_urls.sort()
        
        # 保存
        with open(url_file, 'w', encoding='utf-8') as f:
            for url in all_urls:
                f.write(url + '\n')
        
        print(f"\n保存到 {url_file}")
        print(f"总计：{len(all_urls)} 个链接")
        
        return all_urls


def main():
    print("=" * 60)
    print("搜狐网大规模 ID 扫描器")
    print("=" * 60)
    
    scanner = MassScanner()
    
    # 1. 针对性扫描
    print("\n【步骤 1】针对性扫描...")
    scanner.scan_targeted()
    
    # 2. 顺序扫描（小范围测试）
    print("\n【步骤 2】顺序扫描测试...")
    scanner.scan_sequential(900000000, 10000, step=1000)
    
    # 3. 保存
    print("\n【步骤 3】保存结果...")
    scanner.save_results()
    
    print("\n" + "=" * 60)
    print("扫描完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()

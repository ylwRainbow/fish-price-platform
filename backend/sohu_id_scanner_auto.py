#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜狐网 ID 扫描器 - 自动发现历史文章
通过扫描文章 ID 范围来发现相关文章
"""
import requests
import re
import os
import time
import random
from datetime import datetime


class IDScanner:
    """搜狐网文章 ID 扫描器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.found_urls = []
        self.known_ids = set()
    
    def load_known_ids(self, url_file='backend/sohu_known_urls.txt'):
        """加载已知文章 ID"""
        if os.path.exists(url_file):
            with open(url_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        match = re.search(r'/a/(\d+)', line)
                        if match:
                            self.known_ids.add(match.group(1))
        print(f"已加载 {len(self.known_ids)} 个已知文章 ID")
    
    def check_article(self, article_id):
        """检查单个文章 ID 是否有效且相关"""
        # 尝试不同的专栏 ID
        column_ids = ['210667']  # 水产前沿专栏
        
        for column_id in column_ids:
            url = f'https://www.sohu.com/a/{article_id}_{column_id}'
            
            try:
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200 and len(response.text) > 5000:
                    # 检查是否包含关键词
                    content = response.text
                    keywords = ['湖州', '加州鲈', '鲈鱼', '水产前沿', '杰大饲料', '周报', '行情']
                    
                    if any(kw in content for kw in keywords):
                        # 提取标题进一步验证
                        title_match = re.search(r'<title>([^<]+)</title>', content)
                        if title_match:
                            title = title_match.group(1)
                            if any(kw in title for kw in keywords):
                                print(f"  ✓ 发现：{url} - {title[:50]}...")
                                self.found_urls.append(url)
                                return True
            except:
                pass
        
        return False
    
    def scan_range(self, start_id, end_id, step=1):
        """扫描 ID 范围"""
        print(f"\n扫描 ID 范围：{start_id} - {end_id}")
        
        found_count = 0
        tested_count = 0
        
        # 生成要测试的 ID 列表
        test_ids = list(range(start_id, end_id, step))
        random.shuffle(test_ids)  # 随机打乱
        
        for article_id in test_ids:
            if str(article_id) in self.known_ids:
                continue
            
            tested_count += 1
            
            if self.check_article(str(article_id)):
                found_count += 1
                self.known_ids.add(str(article_id))
            
            # 每 10 个暂停一下
            if tested_count % 10 == 0:
                print(f"  已测试 {tested_count} 个，发现 {found_count} 篇")
                time.sleep(1)
            
            # 随机延迟
            time.sleep(random.uniform(0.5, 2.0))
        
        print(f"\n扫描完成：测试{tested_count}个，发现{found_count}篇")
        return found_count
    
    def scan_smart(self, base_ids, range_size=1000000):
        """
        智能扫描：在已知 ID 附近搜索
        文章 ID 通常是连续的，在已知 ID 附近更容易找到相关文章
        """
        print(f"\n智能扫描：在 {len(base_ids)} 个已知 ID 附近搜索")
        
        total_found = 0
        
        for base_id in base_ids:
            try:
                base_num = int(base_id)
                
                # 在前后范围内搜索
                start = max(base_num - range_size, 100000000)
                end = base_num + range_size
                
                print(f"\n在 {base_id} 附近搜索 ({start} - {end})...")
                
                # 随机采样测试
                test_count = 0
                for offset in range(-range_size, range_size, 10000):
                    test_id = base_num + offset
                    if test_id > 0 and str(test_id) not in self.known_ids:
                        if self.check_article(str(test_id)):
                            total_found += 1
                            test_count += 1
                        
                        time.sleep(random.uniform(1, 3))
                    
                    if test_count >= 5:  # 每个基地 ID 最多发现 5 个
                        break
                
            except ValueError:
                continue
        
        return total_found
    
    def save_urls(self, output_file='backend/sohu_scanned_urls.txt'):
        """保存发现的 URL"""
        # 合并已知链接
        existing = []
        if os.path.exists('backend/sohu_known_urls.txt'):
            with open('backend/sohu_known_urls.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        existing.append(line)
        
        # 合并所有
        all_urls = list(set(existing + self.found_urls))
        all_urls.sort()
        
        # 保存到已知文件
        with open('backend/sohu_known_urls.txt', 'w', encoding='utf-8') as f:
            for url in all_urls:
                f.write(url + '\n')
        
        print(f"\n保存 {len(all_urls)} 个链接到 sohu_known_urls.txt")
        print(f"其中新增 {len(self.found_urls)} 个")
        
        return all_urls


def main():
    """主函数"""
    print("=" * 60)
    print("搜狐网文章 ID 扫描器")
    print("=" * 60)
    
    scanner = IDScanner()
    
    # 1. 加载已知 ID
    print("\n【步骤 1】加载已知文章 ID...")
    scanner.load_known_ids()
    
    # 2. 智能扫描（在已知 ID 附近搜索）
    print("\n【步骤 2】智能扫描（在已知 ID 附近搜索）...")
    known_list = list(scanner.known_ids)
    scanner.scan_smart(known_list, range_size=500000)
    
    # 3. 大范围扫描（可选）
    print("\n【步骤 3】大范围扫描...")
    print("从 500000000 到 1000000000，步长 100000")
    scanner.scan_range(500000000, 1000000000, step=100000)
    
    # 4. 保存结果
    print("\n【步骤 4】保存结果...")
    scanner.save_urls()
    
    print("\n" + "=" * 60)
    print(f"扫描完成！")
    print("=" * 60)
    print(f"\n统计:")
    print(f"  - 已知 ID: {len(scanner.known_ids)} 个")
    print(f"  - 新增：{len(scanner.found_urls)} 个")
    print(f"  - 总计：{len(scanner.known_ids) + len(scanner.found_urls)} 个")


if __name__ == '__main__':
    main()

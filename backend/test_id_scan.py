#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜狐网 ID 扫描器 - 快速测试版
"""
import requests
import re
import os
import time
import random


def scan_test():
    """快速测试扫描"""
    print("=" * 60)
    print("搜狐网 ID 扫描器 - 快速测试")
    print("=" * 60)
    
    # 已知的文章 ID
    known_ids = ['516858961', '660709304']
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    session = requests.Session()
    session.headers.update(headers)
    
    found_urls = []
    
    # 在已知 ID 附近扫描
    for base_id in known_ids:
        base_num = int(base_id)
        print(f"\n扫描 {base_id} 附近...")
        
        # 测试前后各 100 个 ID
        for offset in range(-100, 100, 10):  # 步长 10
            test_id = base_num + offset
            if test_id <= 0:
                continue
            
            url = f'https://www.sohu.com/a/{test_id}_210667'
            
            try:
                response = session.get(url, timeout=3)
                
                if response.status_code == 200 and len(response.text) > 5000:
                    # 检查关键词
                    if any(kw in response.text for kw in ['湖州', '加州鲈', '鲈鱼']):
                        title_match = re.search(r'<title>([^<]+)</title>', response.text)
                        title = title_match.group(1) if title_match else '无标题'
                        print(f"  ✓ 发现：{url} - {title[:40]}...")
                        found_urls.append(url)
                        time.sleep(2)
            except Exception as e:
                pass
            
            time.sleep(random.uniform(0.5, 1.5))
    
    print(f"\n测试完成！发现 {len(found_urls)} 篇文章")
    
    # 保存到文件
    if found_urls:
        with open('backend/sohu_known_urls.txt', 'a', encoding='utf-8') as f:
            for url in found_urls:
                f.write(url + '\n')
        print(f"已保存到 sohu_known_urls.txt")
    
    return found_urls


if __name__ == '__main__':
    scan_test()

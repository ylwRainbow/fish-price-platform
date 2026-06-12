# -*- coding: utf-8 -*-
"""
搜狐网文章 ID 遍历爬虫
通过分析已知文章的 ID 规律，批量发现历史文章
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
import random
import os


class SohuIdCrawler:
    """搜狐网文章 ID 遍历爬虫"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 已知的文章 ID（从成功采集的文章中提取）
        self.known_ids = [
            516858961,  # 2022-01-14 水产前沿
            660709304,  # 2023-03-29 杰大饲料
        ]
        
        # 已知的作者 ID
        self.author_ids = [
            210667,  # 水产前沿/杰大饲料的作者 ID
        ]
        
        self.valid_articles = []
    
    def check_article(self, article_id, author_id):
        """检查文章 ID 是否有效"""
        url = f'https://www.sohu.com/a/{article_id}_{author_id}'
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200 and len(response.text) > 5000:
                # 解析文章
                soup = BeautifulSoup(response.text, 'lxml')
                
                # 提取标题
                title_tag = soup.find('h1') or soup.find('h2')
                title = title_tag.get_text(strip=True) if title_tag else None
                
                # 检查是否包含关键词
                if title and any(kw in title for kw in ['湖州', '加州鲈', '鲈鱼', '水产前沿', '杰大饲料', '周报']):
                    # 提取日期
                    date = self.extract_date(soup)
                    
                    self.valid_articles.append({
                        'id': article_id,
                        'url': url,
                        'title': title,
                        'date': date,
                        'author_id': author_id
                    })
                    
                    print(f"✓ 找到：{article_id} - {title[:50]}... ({date})")
                    return True
        except:
            pass
        
        return False
    
    def extract_date(self, soup):
        """从文章中提取日期"""
        time_tag = soup.find('time')
        if time_tag:
            date_str = time_tag.get('datetime') or time_tag.get_text()
            return date_str[:10] if date_str else None
        return None
    
    def scan_id_range(self, start_id, end_id, author_id):
        """扫描 ID 范围"""
        print(f"\n扫描 ID 范围：{start_id} - {end_id}")
        
        found_count = 0
        
        for article_id in range(start_id, end_id + 1):
            if self.check_article(article_id, author_id):
                found_count += 1
            
            # 控制频率
            time.sleep(random.uniform(0.5, 2.0))
            
            # 每 100 个 ID 暂停一下
            if (article_id - start_id) % 100 == 0 and article_id > start_id:
                print(f"  已扫描 {article_id - start_id} 个 ID，找到 {found_count} 篇文章")
                time.sleep(5)
        
        print(f"\n扫描完成：共找到 {found_count} 篇文章")
    
    def smart_scan(self):
        """智能扫描 - 基于已知 ID 扩展"""
        print("=" * 60)
        print("搜狐网智能 ID 扫描")
        print("=" * 60)
        
        # 从已知 ID 向前后扩展
        for known_id in self.known_ids:
            print(f"\n从已知 ID {known_id} 开始扫描...")
            
            # 向前扫描 1000 个 ID
            start_id = max(known_id - 1000, 100000000)
            end_id = known_id
            
            self.scan_id_range(start_id, end_id, self.author_ids[0])
            
            # 向后扫描 1000 个 ID
            start_id = known_id
            end_id = known_id + 1000
            
            self.scan_id_range(start_id, end_id, self.author_ids[0])
    
    def save_results(self, output_file):
        """保存结果"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for article in self.valid_articles:
                f.write(f"{article['url']}\n")
        
        print(f"\n保存 {len(self.valid_articles)} 个链接到 {output_file}")
        
        # 生成详细报告
        report_file = output_file.replace('.txt', '_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 搜狐网历史文章扫描报告\n\n")
            f.write(f"扫描时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"共找到 **{len(self.valid_articles)}** 篇文章\n\n")
            
            f.write("## 文章列表\n\n")
            f.write("| ID | 标题 | 日期 | URL |\n")
            f.write("|---|------|------|-----|\n")
            
            for article in sorted(self.valid_articles, key=lambda x: x['date'] or '', reverse=True):
                title = article['title'][:30] + '...' if len(article['title'] or '') > 30 else article['title']
                f.write(f"| {article['id']} | {title} | {article['date']} | [链接]({article['url']}) |\n")
        
        print(f"生成报告：{report_file}")


def main():
    """主函数"""
    crawler = SohuIdCrawler()
    
    # 执行智能扫描
    crawler.smart_scan()
    
    # 保存结果
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, 'sohu_urls_id_scan.txt')
    crawler.save_results(output_file)
    
    return crawler.valid_articles


if __name__ == '__main__':
    main()

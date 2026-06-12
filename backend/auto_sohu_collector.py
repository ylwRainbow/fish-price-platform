# -*- coding: utf-8 -*-
"""
搜狐网专栏自动化爬虫
自动收集历史文章链接
"""
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import time
import random
import os


class SohuColumnCrawler:
    """搜狐专栏爬虫"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 已知的专栏 URL（需要通过搜索找到）
        self.column_urls = [
            # 水产前沿 - 需要找到实际专栏页面
            # 杰大饲料 - 需要找到实际专栏页面
        ]
        
        # 关键词过滤
        self.keywords = ['湖州', '加州鲈', '鲈鱼', '水产前沿', '杰大饲料', '周报', '行情']
    
    def search_sohu(self, keyword, start_year=2020, end_year=2024):
        """
        搜索搜狐网文章
        
        使用 Google 搜索：site:sohu.com keyword
        由于无法直接调用 Google API，这里提供搜索链接生成
        """
        search_urls = []
        
        # 生成 Google 搜索链接
        for year in range(start_year, end_year + 1):
            # Google 搜索语法：site:sohu.com "keyword" after:YEAR-01-01 before:YEAR-12-31
            query = f'site:sohu.com "{keyword}" after:{year}-01-01 before:{year}-12-31'
            encoded_query = requests.utils.quote(query)
            google_search_url = f'https://www.google.com/search?q={encoded_query}'
            search_urls.append({
                'year': year,
                'query': query,
                'search_url': google_search_url
            })
        
        return search_urls
    
    def fetch_with_selenium(self, url):
        """
        使用 Selenium 获取动态内容
        适用于需要 JavaScript 渲染的页面
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            time.sleep(3)  # 等待页面加载
            
            html = driver.page_source
            driver.quit()
            
            return html
        except Exception as e:
            print(f"Selenium 访问失败：{e}")
            return None
    
    def extract_articles_from_search(self, html):
        """从搜索结果页面提取文章链接"""
        articles = []
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Google 搜索结果
        for result in soup.select('div.g, div.tF2Cxc'):
            title_tag = result.select_one('h3')
            link_tag = result.select_one('a')
            
            if title_tag and link_tag:
                title = title_tag.get_text()
                url = link_tag.get('href')
                
                # 只保留搜狐网链接
                if url and 'sohu.com' in url:
                    # 检查是否包含关键词
                    if any(kw in title for kw in self.keywords):
                        articles.append({
                            'title': title,
                            'url': url,
                            'source': 'google_search'
                        })
        
        return articles
    
    def crawl_known_columns(self):
        """
        爬取已知的专栏页面
        
        需要先找到以下专栏的实际 URL：
        1. 水产前沿 - 每周价格周报
        2. 杰大饲料 - 每周行情分析
        """
        all_articles = []
        
        # 示例：假设找到专栏 URL
        column_examples = [
            'https://www.sohu.com/mp/account/123456',  # 水产前沿专栏（示例）
            'https://www.sohu.com/mp/account/789012',  # 杰大饲料专栏（示例）
        ]
        
        for column_url in column_examples:
            print(f"爬取专栏：{column_url}")
            articles = self.crawl_column_page(column_url)
            all_articles.extend(articles)
            time.sleep(2)
        
        return all_articles
    
    def crawl_column_page(self, column_url, max_pages=20):
        """爬取专栏的单页"""
        articles = []
        
        for page in range(1, max_pages + 1):
            # 构建分页 URL（需要根据实际专栏页面结构调整）
            if page == 1:
                url = column_url
            else:
                url = f"{column_url}?page={page}"
            
            try:
                html = self.fetch_article(url)
                if not html:
                    break
                
                # 解析文章列表
                page_articles = self.parse_column_articles(html)
                if not page_articles:
                    break
                
                articles.extend(page_articles)
                print(f"  第{page}页：{len(page_articles)}篇文章")
                
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"爬取第{page}页失败：{e}")
                break
        
        return articles
    
    def parse_column_articles(self, html):
        """解析专栏页面的文章列表"""
        articles = []
        
        soup = BeautifulSoup(html, 'lxml')
        
        # 查找文章列表（选择器需要根据实际页面结构调整）
        article_elements = soup.select('div.article-list div.article-item, article')
        
        for elem in article_elements:
            title_tag = elem.select_one('h3, h4, .article-title')
            link_tag = elem.select_one('a')
            date_tag = elem.select_one('time, .date, .publish-time')
            
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                url = link_tag.get('href')
                
                # 处理相对 URL
                if url and url.startswith('/'):
                    url = f'https://www.sohu.com{url}'
                
                # 提取日期
                date_str = None
                if date_tag:
                    date_str = date_tag.get('datetime') or date_tag.get_text()
                
                # 过滤关键词
                if any(kw in title for kw in self.keywords):
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': date_str,
                        'source': 'column'
                    })
        
        return articles
    
    def extract_from_wechat_articles(self, wechat_data_file):
        """从已采集的微信文章中提取搜狐网链接"""
        sohu_urls = set()
        
        try:
            with open(wechat_data_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 使用正则提取搜狐网链接
                pattern = r'https?://[wm]*\.sohu\.com/a/\d+_\d+/?'
                matches = re.findall(pattern, content)
                
                sohu_urls.update(matches)
                print(f"从微信文章中提取到 {len(sohu_urls)} 个搜狐网链接")
                
        except FileNotFoundError:
            print(f"文件不存在：{wechat_data_file}")
        
        return list(sohu_urls)
    
    def fetch_article(self, url, max_retries=3):
        """获取文章内容（复用已有方法）"""
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                if len(response.text) < 1000:
                    if attempt < max_retries - 1:
                        time.sleep(5 * (attempt + 1))
                        continue
                
                return response.text
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(3 * (attempt + 1))
        
        return None
    
    def save_urls(self, articles, output_file):
        """保存 URL 到文件"""
        # 去重
        unique_urls = {}
        for article in articles:
            url = article['url']
            if url not in unique_urls:
                unique_urls[url] = article
        
        # 排序
        sorted_articles = sorted(unique_urls.values(), 
                                key=lambda x: x.get('date', ''), 
                                reverse=True)
        
        # 保存
        with open(output_file, 'w', encoding='utf-8') as f:
            for article in sorted_articles:
                f.write(f"{article['url']}\n")
        
        print(f"保存 {len(sorted_articles)} 个链接到 {output_file}")
        return sorted_articles


def main():
    """主函数"""
    print("=" * 60)
    print("搜狐网专栏自动化爬虫 - 历史文章收集")
    print("=" * 60)
    
    crawler = SohuColumnCrawler()
    all_articles = []
    
    # 方法 1：从微信文章中提取
    print("\n【方法 1】从微信文章中提取搜狐网链接...")
    wechat_file = '../docs/price_data_to_verify.md'
    wechat_urls = crawler.extract_from_wechat_articles(wechat_file)
    
    for url in wechat_urls:
        all_articles.append({
            'title': '从微信文章提取',
            'url': url,
            'source': 'wechat_reference'
        })
    
    # 方法 2：生成搜索链接（需要手动或通过其他方式获取）
    print("\n【方法 2】生成搜索链接...")
    keywords = ['加州鲈 湖州 水产前沿', '加州鲈 湖州 杰大饲料', '鲈鱼价格 湖州']
    
    search_links = []
    for keyword in keywords:
        search_urls = crawler.search_sohu(keyword, start_year=2020)
        search_links.extend(search_urls)
    
    print(f"生成 {len(search_links)} 个搜索链接")
    print("示例搜索链接:")
    for link in search_links[:3]:
        print(f"  {link['search_url']}")
    
    # 保存搜索结果链接到文件（供后续处理）
    output_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(output_dir, 'sohu_search_links.txt'), 'w', encoding='utf-8') as f:
        for link in search_links:
            f.write(f"{link['search_url']}\n")
    
    print("\n搜索链接已保存到：sohu_search_links.txt")
    
    # 保存所有收集到的 URL
    if all_articles:
        output_file = os.path.join(output_dir, 'sohu_urls_auto.txt')
        crawler.save_urls(all_articles, output_file)
        print(f"\n自动收集完成！共收集 {len(all_articles)} 个链接")
    else:
        print("\n未收集到链接，将使用搜索链接")
    
    return all_articles


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
搜狐网历史文章链接收集器
通过搜索引擎 API 和手动收集获取历史文章链接
"""
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import time


def search_sohu_articles(keywords, start_year=2020, end_year=None):
    """
    搜索搜狐网历史文章
    
    Args:
        keywords: 搜索关键词列表
        start_year: 起始年份
        end_year: 结束年份（默认当前年份）
    
    Returns:
        文章链接列表
    """
    if end_year is None:
        end_year = datetime.now().year
    
    all_urls = set()
    
    # 使用 Google 搜索（site:sohu.com）
    # 注意：这里需要使用搜索引擎 API，或者手动收集
    search_queries = []
    
    for keyword in keywords:
        for year in range(start_year, end_year + 1):
            # 构建搜索查询
            query = f"{keyword} site:sohu.com {year}"
            search_queries.append(query)
    
    print(f"生成 {len(search_queries)} 个搜索查询")
    print("示例查询:")
    for q in search_queries[:5]:
        print(f"  - {q}")
    
    # 由于无法直接调用搜索引擎 API
    # 这里提供手动收集的模板
    print("\n" + "="*60)
    print("请按以下方式手动收集链接：")
    print("="*60)
    print("""
1. 访问 Google 或百度搜索
2. 使用以下搜索语法：
   site:sohu.com "加州鲈" "湖州" "水产前沿"
   site:sohu.com "加州鲈" "湖州" "杰大饲料"
   site:sohu.com "鲈鱼价格" "浙江湖州"
   
3. 添加时间限定：
   - 在搜索工具中选择时间范围（如 2020-2024 年）
   - 或者在查询中直接加年份：2020, 2021, 2022, 2023, 2024

4. 复制搜索结果中的链接到文本文件

推荐关键词组合：
- "加州鲈 湖州 水产前沿"
- "加州鲈 湖州 杰大饲料"
- "鲈鱼 湖州 塘口价"
- "浙江湖州 加州鲈 价格"
- "水产前沿 周报 湖州"
- "杰大饲料 鲈鱼 行情"
    """)
    
    return list(all_urls)


def collect_urls_from_file(file_path):
    """
    从文件中收集 URL 列表
    
    Args:
        file_path: 包含 URL 的文件路径
    
    Returns:
        URL 列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = []
            for line in f:
                line = line.strip()
                if line and line.startswith('http'):
                    # 验证 URL 格式
                    if 'sohu.com' in line:
                        urls.append(line)
            
            print(f"从 {file_path} 读取到 {len(urls)} 个 URL")
            return urls
    except FileNotFoundError:
        print(f"文件不存在：{file_path}")
        return []


def deduplicate_urls(urls):
    """
    去重 URL 列表
    
    Args:
        urls: URL 列表
    
    Returns:
        去重后的 URL 列表
    """
    # 使用集合去重
    unique_urls = list(set(urls))
    
    # 按文章 ID 排序（搜狐网 URL 通常包含 /a/数字）
    def extract_article_id(url):
        match = re.search(r'/a/(\d+)', url)
        return int(match.group(1)) if match else 0
    
    unique_urls.sort(key=extract_article_id, reverse=True)
    
    print(f"去重后剩余 {len(unique_urls)} 个 URL")
    return unique_urls


def save_urls(urls, output_file):
    """
    保存 URL 到文件
    
    Args:
        urls: URL 列表
        output_file: 输出文件路径
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')
    
    print(f"已保存 {len(urls)} 个 URL 到 {output_file}")


def main():
    """主函数"""
    print("=" * 60)
    print("搜狐网历史文章链接收集器")
    print("=" * 60)
    
    # 定义搜索关键词
    keywords = [
        "加州鲈 湖州 水产前沿",
        "加州鲈 湖州 杰大饲料",
        "鲈鱼 湖州 塘口价",
        "浙江湖州 加州鲈 价格",
        "水产前沿 周报 湖州",
        "杰大饲料 鲈鱼 行情",
    ]
    
    # 搜索文章（生成搜索建议）
    print("\n【步骤 1】生成搜索查询...")
    search_sohu_articles(keywords, start_year=2020)
    
    # 从文件读取 URL
    print("\n【步骤 2】从文件读取 URL...")
    url_file = 'sohu_historical_urls.txt'
    urls = collect_urls_from_file(url_file)
    
    # 如果没有文件，使用示例 URL
    if not urls:
        print("未找到 URL 文件，使用示例 URL...")
        urls = [
            'https://www.sohu.com/a/516858961_210667',
            'https://m.sohu.com/a/660709304_210667/',
            # 添加更多已知的历史文章 URL
        ]
    
    # 去重
    print("\n【步骤 3】URL 去重...")
    urls = deduplicate_urls(urls)
    
    # 保存
    print("\n【步骤 4】保存 URL...")
    output_file = 'sohu_urls_final.txt'
    save_urls(urls, output_file)
    
    print("\n" + "="*60)
    print("收集完成！")
    print(f"共收集 {len(urls)} 个 URL")
    print("="*60)
    
    return urls


if __name__ == '__main__':
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()

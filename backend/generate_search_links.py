# -*- coding: utf-8 -*-
"""
搜狐网历史文章链接收集器 - 实用版
通过预定义的搜索策略收集链接
"""
import os

# 生成搜索链接列表
search_queries = []

keywords = [
    '加州鲈 湖州 水产前沿',
    '加州鲈 湖州 杰大饲料',
    '鲈鱼价格 湖州',
    '浙江湖州 加州鲈',
    '水产前沿 周报 湖州',
]

years = list(range(2020, 2025))

print("=" * 60)
print("搜狐网历史文章搜索链接生成器")
print("=" * 60)

for keyword in keywords:
    for year in years:
        # Google 搜索语法
        query = f'site:sohu.com "{keyword}" after:{year}-01-01 before:{year}-12-31'
        encoded = requests.utils.quote(query) if 'requests' in globals() else query.replace(' ', '+')
        
        google_url = f'https://www.google.com/search?q={encoded}'
        
        search_queries.append({
            'keyword': keyword,
            'year': year,
            'url': google_url
        })

print(f"\n生成了 {len(search_queries)} 个搜索链接\n")

# 显示示例
print("示例搜索链接：")
for i, item in enumerate(search_queries[:5], 1):
    print(f"{i}. {item['keyword']} ({item['year']})")
    print(f"   {item['url'][:100]}...\n")

# 保存搜索链接
output_file = 'backend/sohu_search_urls.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# 搜狐网历史文章搜索链接\n")
    f.write("# 使用方法：逐个点击链接，在 Google 搜索结果中复制搜狐网文章 URL\n")
    f.write("# 将复制的 URL 保存到 sohu_known_urls.txt\n\n")
    
    for item in search_queries:
        f.write(f"# {item['keyword']} ({item['year']})\n")
        f.write(f"{item['url']}\n\n")

print(f"搜索链接已保存到：{output_file}")
print(f"\n下一步操作：")
print("1. 打开生成的搜索链接")
print("2. 在 Google 搜索结果中复制搜狐网文章 URL")
print("3. 添加到 backend/sohu_known_urls.txt")
print("4. 运行采集脚本")

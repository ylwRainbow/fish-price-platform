# 搜狐网历史数据批量采集实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 自动化收集 200+ 篇搜狐网历史文章，采集 400+ 条湖州鲈鱼价格数据并导入数据库

**Architecture:** 使用已有的爬虫系统，通过自动化搜索链接生成、批量爬取、AI 验证、数据库导入的完整流程

**Tech Stack:** Python 3, requests, BeautifulSoup4, MySQL, 已有爬虫模块

---

## 阶段 1：链接收集自动化

### Task 1: 创建智能链接收集器

**Files:**
- Create: `backend/smart_link_collector.py`
- Modify: `backend/sohu_known_urls.txt`

**Step 1: 创建智能链接收集器**

```python
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
        
    def load_existing_urls(self):
        """加载已有的链接"""
        url_file = 'backend/sohu_known_urls.txt'
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
```

**Step 2: 测试链接收集器**

```bash
cd /Users/zcy/IdeaProjects/fish-price-platform
python backend/smart_link_collector.py
```

Expected: 成功加载现有链接，生成搜索链接列表

**Step 3: 添加 20 个测试链接**

手动添加以下格式的链接到 `backend/sohu_known_urls.txt`：
```
https://www.sohu.com/a/516858961_210667
https://m.sohu.com/a/660709304_210667/
# 添加更多从搜索结果中复制的链接
```

**Step 4: 验证链接收集**

```bash
python -c "
from backend.smart_link_collector import SmartLinkCollector
collector = SmartLinkCollector()
collector.load_existing_urls()
print(f'收集到 {len(collector.known_urls)} 个链接')
"
```

Expected: 显示收集到的链接数量

**Step 5: Commit**

```bash
cd /Users/zcy/IdeaProjects/fish-price-platform
git add backend/smart_link_collector.py backend/sohu_known_urls.txt
git commit -m "feat: 创建智能链接收集器"
```

---

## 阶段 2：批量爬取优化

### Task 2: 优化爬虫性能

**Files:**
- Modify: `backend/sohu_crawler.py:1-50`

**Step 1: 添加并发控制**

```python
# 在 SohuCrawler 类中添加并发控制
def crawl_urls_batch(self, urls, batch_size=10, delay=2.0):
    """批量爬取，控制并发和延迟"""
    all_data = []
    
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        print(f"\n爬取批次 {i//batch_size + 1}/{(len(urls)-1)//batch_size + 1}")
        
        for url in batch:
            html = self.fetch_article(url)
            if html:
                data = self.parse_article(html, url)
                all_data.extend(data)
            
            time.sleep(delay)  # 控制频率
        
        # 每批次后暂停
        if i + batch_size < len(urls):
            print(f"批次完成，暂停 5 秒...")
            time.sleep(5)
    
    return all_data
```

**Step 2: 添加进度保存**

```python
def crawl_with_checkpoint(self, urls, checkpoint_file='backend/crawl_progress.json'):
    """带进度保存的爬取"""
    import json
    
    # 加载进度
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            progress = json.load(f)
        start_index = progress.get('last_index', 0)
        collected_data = progress.get('data', [])
    else:
        start_index = 0
        collected_data = []
    
    # 继续爬取
    for i in range(start_index, len(urls)):
        url = urls[i]
        print(f"[{i+1}/{len(urls)}] 爬取：{url}")
        
        html = self.fetch_article(url)
        if html:
            data = self.parse_article(html, url)
            collected_data.extend(data)
            print(f"  -> 提取 {len(data)} 条数据")
        
        # 每 10 个保存一次进度
        if (i + 1) % 10 == 0:
            with open(checkpoint_file, 'w') as f:
                json.dump({
                    'last_index': i + 1,
                    'data': collected_data,
                    'total_urls': len(urls)
                }, f, ensure_ascii=False, indent=2)
            print(f"  进度已保存")
        
        time.sleep(2.0)
    
    return collected_data
```

**Step 3: 测试批量爬取**

```bash
python -c "
from backend.sohu_crawler import SohuCrawler

urls = [
    'https://www.sohu.com/a/516858961_210667',
    'https://m.sohu.com/a/660709304_210667/',
] * 5  # 测试用 10 个链接

crawler = SohuCrawler()
data = crawler.crawl_urls_batch(urls, batch_size=5, delay=1.0)
print(f'采集到 {len(data)} 条数据')
"
```

Expected: 成功采集数据，显示批次进度

**Step 4: Commit**

```bash
git add backend/sohu_crawler.py
git commit -m "feat: 添加批量爬取和进度保存功能"
```

---

## 阶段 3：数据验证和清洗

### Task 3: 数据去重和验证

**Files:**
- Create: `backend/data_validator.py`

**Step 1: 创建数据验证器**

```python
# -*- coding: utf-8 -*-
"""
数据验证器 - 去重、验证、清洗
"""
import hashlib
from datetime import datetime

class DataValidator:
    def __init__(self):
        self.seen_hashes = set()
    
    def generate_hash(self, item):
        """生成数据指纹"""
        key = f"{item['date']}|{item['specification']}|{item['price']}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def is_duplicate(self, item):
        """检查是否重复"""
        h = self.generate_hash(item)
        if h in self.seen_hashes:
            return True
        self.seen_hashes.add(h)
        return False
    
    def validate_price(self, price):
        """验证价格合理性"""
        try:
            p = float(price)
            return 5 <= p <= 30  # 合理价格范围
        except:
            return False
    
    def validate_date(self, date_str):
        """验证日期格式"""
        if not date_str:
            return False
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except:
            return False
    
    def clean_data(self, data_list):
        """清洗数据"""
        cleaned = []
        for item in data_list:
            # 检查重复
            if self.is_duplicate(item):
                print(f"跳过重复：{item['date']} {item['specification']}")
                continue
            
            # 验证价格
            if not self.validate_price(item['price']):
                print(f"跳过异常价格：{item['price']}")
                continue
            
            # 验证日期
            if not self.validate_date(item.get('date')):
                print(f"跳过异常日期：{item.get('date')}")
                continue
            
            cleaned.append(item)
        
        return cleaned
```

**Step 2: 测试数据验证**

```bash
python -c "
from backend.data_validator import DataValidator

validator = DataValidator()
test_data = [
    {'date': '2022-01-15', 'specification': '大统货', 'price': 12.5},
    {'date': '2022-01-15', 'specification': '大统货', 'price': 12.5},  # 重复
    {'date': '2023-03-29', 'specification': '8 成统货', 'price': 8.5},
]

cleaned = validator.clean_data(test_data)
print(f'原始：{len(test_data)}条，清洗后：{len(cleaned)}条')
"
```

Expected: 检测到重复数据，输出清洗后的数据

**Step 3: Commit**

```bash
git add backend/data_validator.py
git commit -m "feat: 创建数据验证和清洗模块"
```

---

## 阶段 4：执行批量采集

### Task 4: 运行完整采集流程

**Files:**
- Create: `backend/run_batch_collection.py`

**Step 1: 创建批量采集脚本**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量采集执行脚本
"""
import sys
import os
sys.path.insert(0, 'backend')

from smart_link_collector import SmartLinkCollector
from sohu_crawler import SohuCrawler
from data_validator import DataValidator
from md_generator import generate_md_file
from ai_verifier import verify_all_data
from verification_report import generate_report

def main():
    print("=" * 60)
    print("搜狐网历史数据批量采集")
    print("=" * 60)
    
    # 1. 加载链接
    print("\n【步骤 1】加载链接...")
    collector = SmartLinkCollector()
    collector.load_existing_urls()
    
    if len(collector.known_urls) < 10:
        print("⚠️ 链接数量不足，请先收集更多链接")
        print("运行：python backend/smart_link_collector.py")
        return
    
    urls = list(collector.known_urls)
    print(f"共 {len(urls)} 个链接")
    
    # 2. 批量爬取
    print("\n【步骤 2】批量爬取...")
    crawler = SohuCrawler()
    data = crawler.crawl_with_checkpoint(urls)
    print(f"采集到 {len(data)} 条数据")
    
    if not data:
        print("未采集到数据，终止流程")
        return
    
    # 3. 数据清洗
    print("\n【步骤 3】数据清洗...")
    validator = DataValidator()
    cleaned_data = validator.clean_data(data)
    print(f"清洗后：{len(cleaned_data)}条有效数据")
    
    # 4. 生成 Markdown
    print("\n【步骤 4】生成 Markdown...")
    generate_md_file(cleaned_data, 'docs/sohu_batch_data.md')
    print("✓ Markdown 已生成")
    
    # 5. AI 验证
    print("\n【步骤 5】AI 验证...")
    results = verify_all_data('docs/sohu_batch_data.md')
    passed = sum(1 for r in results if r['passed'])
    print(f"验证通过：{passed}/{len(results)}条")
    
    # 6. 生成报告
    print("\n【步骤 6】生成报告...")
    generate_report(results, 'docs/sohu_batch_report.md')
    print("✓ 报告已生成")
    
    # 7. 导入数据库
    print("\n【步骤 7】导入数据库...")
    os.environ['MYSQL_DSN'] = 'mysql://root:YOUR_PASSWORD@127.0.0.1:3306/fish_prices'
    from auto_import import import_verified_data
    import_verified_data('docs/sohu_batch_report.md')
    print("✓ 数据库导入完成")
    
    print("\n" + "=" * 60)
    print("批量采集完成！")
    print("=" * 60)
    print(f"\n统计:")
    print(f"  - 采集链接：{len(urls)}个")
    print(f"  - 获得数据：{len(data)}条")
    print(f"  - 有效数据：{len(cleaned_data)}条")
    print(f"  - 验证通过：{passed}条")

if __name__ == '__main__':
    main()
```

**Step 2: 执行批量采集**

```bash
cd /Users/zcy/IdeaProjects/fish-price-platform
python backend/run_batch_collection.py
```

Expected: 自动完成所有步骤，输出统计信息

**Step 3: Commit**

```bash
git add backend/run_batch_collection.py
git commit -m "feat: 创建批量采集执行脚本"
```

---

## 阶段 5：监控和报告

### Task 5: 生成采集报告

**Files:**
- Create: `backend/generate_statistics.py`

**Step 1: 创建统计报告生成器**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据统计报告生成器
"""
import os
os.environ['MYSQL_DSN'] = 'mysql://root:YOUR_PASSWORD@127.0.0.1:3306/fish_prices'

from app.db import get_conn

def generate_report():
    conn = get_conn()
    cursor = conn.cursor()
    
    print("=" * 60)
    print("搜狐网数据采集统计报告")
    print("=" * 60)
    
    # 总数统计
    cursor.execute("""
        SELECT COUNT(*) 
        FROM prices 
        WHERE market_id=103 AND fish_id=1
    """)
    total = cursor.fetchone()[0]
    print(f"\n数据库总数据量：{total}条")
    
    # 按年份统计
    cursor.execute("""
        SELECT YEAR(ts) as year, COUNT(*) as count
        FROM prices
        WHERE market_id=103 AND fish_id=1
        GROUP BY YEAR(ts)
        ORDER BY year
    """)
    print("\n按年份分布:")
    for row in cursor.fetchall():
        print(f"  {row[0]}年：{row[1]}条")
    
    # 价格统计
    cursor.execute("""
        SELECT MIN(price), MAX(price), AVG(price)
        FROM prices
        WHERE market_id=103 AND fish_id=1
    """)
    min_p, max_p, avg_p = cursor.fetchone()
    print(f"\n价格统计:")
    print(f"  最低：{min_p}元/斤")
    print(f"  最高：{max_p}元/斤")
    print(f"  平均：{avg_p:.2f}元/斤")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    generate_report()
```

**Step 2: 生成统计报告**

```bash
python backend/generate_statistics.py
```

Expected: 输出完整的统计报告

**Step 3: Commit**

```bash
git add backend/generate_statistics.py
git commit -m "feat: 创建统计报告生成器"
```

---

## 阶段 6：自动化调度（可选）

### Task 6: 设置定时任务

**Files:**
- Create: `backend/schedule_collection.py`

**Step 1: 创建定时任务脚本**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时采集任务
"""
import schedule
import time
import subprocess

def job():
    """定时执行采集任务"""
    print("开始定时采集...")
    subprocess.run(['python', 'backend/run_batch_collection.py'])
    print("定时采集完成")

# 每周一上午 9 点执行
schedule.every().monday.at("09:00").do(job)

print("定时任务已启动，按 Ctrl+C 停止")
while True:
    schedule.run_pending()
    time.sleep(60)
```

**Step 2: 测试定时任务**

```bash
python backend/schedule_collection.py
```

**Step 3: Commit**

```bash
git add backend/schedule_collection.py
git commit -m "feat: 创建定时采集任务"
```

---

## 完成标准

✅ 收集到 200+ 个搜狐网文章链接
✅ 成功采集 400+ 条价格数据
✅ AI 验证通过率 > 80%
✅ 成功导入数据库
✅ 生成完整的统计报告
✅ 设置定时自动更新（可选）

---

## 执行顺序

1. **Task 1** - 创建智能链接收集器 (30 分钟)
2. **Task 2** - 优化爬虫性能 (30 分钟)
3. **Task 3** - 数据验证和清洗 (20 分钟)
4. **Task 4** - 运行完整采集流程 (1-2 小时，取决于链接数量)
5. **Task 5** - 生成采集报告 (10 分钟)
6. **Task 6** - 设置定时任务 (可选，15 分钟)

**总预计时间**: 2.5-3.5 小时

---

## 风险和挑战

1. **反爬机制** - 已通过延迟和重试机制缓解
2. **链接失效** - 自动跳过无法访问的链接
3. **数据质量** - 通过 AI 验证和人工抽检保证
4. **日期提取失败** - 已硬编码已知文章日期

---

## 下一步

立即开始执行 Task 1！

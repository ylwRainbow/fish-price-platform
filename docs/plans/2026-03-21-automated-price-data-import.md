# 鲈鱼价格数据全自动导入实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 从微信文章链接自动采集鲈鱼价格数据，AI 智能验证后导入数据库，全程无需人工参与。

**Architecture:** 
1. 爬取微信文章提取价格数据
2. 将原始数据写入 Markdown 文档
3. AI 逐条搜索验证数据准确性
4. 自动导入验证通过的数据到数据库
5. 生成完整的验证和导入报告

**Tech Stack:** Python 3, requests, BeautifulSoup4, lxml, MySQL, Playwright (可选)

---

## 阶段一：数据采集与 Markdown 生成

### Task 1: 创建微信文章爬虫模块

**Files:**
- Create: `backend/wechat_crawler.py`
- Test: `backend/test_crawler.py`

**Step 1: 编写爬虫代码**

```python
# -*- coding: utf-8 -*-
"""
微信文章爬虫 - 自动抓取鲈鱼价格数据
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time

def fetch_article_content(url):
    """获取微信文章内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"获取文章失败：{url} - {e}")
        return None

def extract_price_data(html, source_url):
    """从 HTML 中提取价格数据"""
    soup = BeautifulSoup(html, 'lxml')
    
    # 提取文章标题
    title = soup.find('h2', class_='rich_media_title')
    title_text = title.get_text(strip=True) if title else ""
    
    # 提取正文内容
    content = soup.find('div', class_='rich_media_content')
    if not content:
        return []
    
    text = content.get_text()
    
    # 正则匹配价格信息
    # 模式：日期 + 价格
    patterns = [
        r'(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日号])[^0-9]*(鲈鱼|海鲈)[^0-9]*价格[为是]?(\d+\.?\d*)[元斤]',
        r'(\d{1,2}月\d{1,2}日)[^0-9]*(鲈鱼|海鲈)[^0-9]*价格[为是]?(\d+\.?\d*)[元斤]',
        r'(鲈鱼|海鲈)[^0-9]*(\d+\.?\d*)[元斤][^0-9]*(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日号])',
    ]
    
    data_list = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            date_str = match.group(1)
            price = float(match.group(3))
            
            # 标准化日期格式
            date_standardized = standardize_date(date_str)
            
            if date_standardized:
                data_list.append({
                    'date': date_standardized,
                    'price': price,
                    'source_url': source_url,
                    'original_text': match.group(0),
                    'title': title_text
                })
    
    return data_list

def standardize_date(date_str):
    """将各种日期格式标准化为 YYYY-MM-DD"""
    # 实现日期转换逻辑
    # 处理"2020 年 3 月 15 日"、"3 月 15 日"等格式
    pass

def crawl_all_articles(url_file):
    """爬取所有文章"""
    with open(url_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    all_data = []
    for idx, url in enumerate(urls, 1):
        print(f"[{idx}/{len(urls)}] 爬取：{url}")
        html = fetch_article_content(url)
        if html:
            data = extract_price_data(html, url)
            all_data.extend(data)
            print(f"  -> 提取 {len(data)} 条数据")
        time.sleep(1)  # 避免请求过快
    
    return all_data

if __name__ == '__main__':
    data = crawl_all_articles('数据地址')
    print(f"\n共采集到 {len(data)} 条数据")
```

**Step 2: 测试爬虫**

```bash
cd /Users/zcy/IdeaProjects/fish-price-platform/backend
.venv/bin/python wechat_crawler.py
```

预期：成功爬取部分文章，提取到价格数据

---

### Task 2: 创建 Markdown 文档生成器

**Files:**
- Create: `backend/md_generator.py`

**Step 1: 编写 Markdown 生成代码**

```python
# -*- coding: utf-8 -*-
"""
生成待验证的 Markdown 文档
"""
from datetime import datetime

def generate_md_file(data_list, output_file):
    """生成 Markdown 文档"""
    
    md_content = """# 鲈鱼价格数据 - 待验证

> 生成时间：{timestamp}
> 数据来源：微信文章
> 总数据条数：{total}

---

""".format(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total=len(data_list)
    )
    
    for idx, item in enumerate(data_list, 1):
        md_content += f"""## 第 {idx} 条

- **日期**: {item['date']}
- **价格**: {item['price']} 元/斤
- **来源文章**: {item['title']}
- **来源链接**: {item['source_url']}
- **原始记录**: "{item['original_text']}"

---

"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Markdown 文档已生成：{output_file}")

if __name__ == '__main__':
    # 从爬虫获取数据
    from wechat_crawler import crawl_all_articles
    data = crawl_all_articles('数据地址')
    generate_md_file(data, 'docs/price_data_to_verify.md')
```

**Step 2: 测试生成 Markdown**

```bash
.venv/bin/python md_generator.py
```

预期：生成 `docs/price_data_to_verify.md` 文件

---

## 阶段二：AI 智能验证

### Task 3: 创建 AI 验证模块

**Files:**
- Create: `backend/ai_verifier.py`

**Step 1: 编写 AI 验证代码**

```python
# -*- coding: utf-8 -*-
"""
AI 智能验证 - 逐条搜索验证数据准确性
"""
import requests
from urllib.parse import quote
import re

def search_web(query):
    """执行 Web 搜索"""
    # 使用搜索引擎 API 或直接爬取搜索结果
    url = f"https://www.baidu.com/s?wd={quote(query)}"
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.text[:5000]  # 返回前 5000 字符
    except:
        return ""

def verify_price_data(item, idx):
    """
    验证单条数据
    返回：(是否通过，验证理由，可信度)
    """
    date = item['date']
    price = item['price']
    
    # 构建搜索查询
    queries = [
        f"{date} 鲈鱼 价格",
        f"{date[:7]} 鲈鱼 市场价",
        f"湖州 鲈鱼 价格 {date}",
    ]
    
    evidence = []
    for query in queries:
        html = search_web(query)
        # 提取搜索结果中的价格信息
        prices_found = re.findall(r'鲈鱼 [价格]?[为是]?(\d+\.?\d*)[元斤]', html)
        if prices_found:
            evidence.extend(prices_found)
    
    # 分析证据
    if not evidence:
        return False, "未找到相关证据", "低"
    
    # 计算平均价格
    avg_price = sum(map(float, evidence)) / len(evidence)
    
    # 判断价格是否合理
    if abs(price - avg_price) / avg_price < 0.3:  # 30% 误差范围内
        return True, f"搜索到{len(evidence)}条证据，平均价格{avg_price:.2f}元，数据合理", "高"
    else:
        return False, f"搜索价格 ({avg_price:.2f}元) 与记录 ({price}元) 差异过大", "中"

def verify_all_data(md_file):
    """验证 Markdown 文件中的所有数据"""
    # 解析 Markdown 文件
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取数据块
    import re
    pattern = r'## 第 (\d+) 条.*?- \*\*日期\*\*: (.*?)\n.*?- \*\*价格\*\*: (\d+\.?\d*)'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    results = []
    for idx, match in enumerate(matches, 1):
        item_id = match.group(1)
        date = match.group(2)
        price = float(match.group(3))
        
        print(f"[{idx}] 验证：{date} | {price}元")
        
        passed, reason, confidence = verify_price_data(
            {'date': date, 'price': price}, 
            item_id
        )
        
        results.append({
            'id': item_id,
            'date': date,
            'price': price,
            'passed': passed,
            'reason': reason,
            'confidence': confidence
        })
        
        print(f"  -> {'✅ 通过' if passed else '❌ 跳过'}: {reason}")
    
    return results
```

**Step 2: 测试 AI 验证**

```bash
.venv/bin/python ai_verifier.py
```

预期：逐条验证数据，输出验证结果

---

### Task 4: 生成验证报告

**Files:**
- Create: `backend/verification_report.py`

**Step 1: 编写报告生成代码**

```python
# -*- coding: utf-8 -*-
"""
生成验证报告
"""
from datetime import datetime

def generate_report(results, output_file):
    """生成验证报告"""
    
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    
    report = f"""# 鲈鱼价格数据验证报告

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 总体统计

- 总数据条数：{total}
- 验证通过：{passed} ({passed/total*100:.1f}%)
- 验证未通过：{failed} ({failed/total*100:.1f}%)

## 验证详情

### ✅ 通过的数据 ({passed}条)

"""
    
    for r in results:
        if r['passed']:
            report += f"""
#### 第 {r['id']} 条：{r['date']} | {r['price']}元/斤
- 可信度：{r['confidence']}
- 验证理由：{r['reason']}
- 决策：**导入**
"""
    
    report += f"""
### ❌ 未通过的数据 ({failed}条)

"""
    
    for r in results:
        if not r['passed']:
            report += f"""
#### 第 {r['id']} 条：{r['date']} | {r['price']}元/斤
- 可信度：{r['confidence']}
- 验证理由：{r['reason']}
- 决策：**跳过**
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"验证报告已生成：{output_file}")

if __name__ == '__main__':
    from ai_verifier import verify_all_data
    results = verify_all_data('docs/price_data_to_verify.md')
    generate_report(results, 'docs/verification_report.md')
```

---

## 阶段三：数据导入

### Task 5: 创建数据库导入模块

**Files:**
- Create: `backend/auto_import.py`

**Step 1: 编写导入代码**

```python
# -*- coding: utf-8 -*-
"""
自动导入验证通过的数据到数据库
"""
import sys
sys.path.insert(0, '.')
from app.db import get_conn
from app.repository import save_price

def import_verified_data(report_file):
    """导入验证通过的数据"""
    
    # 解析验证报告
    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    import re
    # 提取通过的数据
    pattern = r'#### 第 (\d+) 条：(\d{4}-\d{2}-\d{2}) \| (\d+\.?\d*) 元/斤.*?决策：\*\*导入\*\*'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    conn = get_conn()
    cursor = conn.cursor()
    
    success_count = 0
    skip_count = 0
    
    for match in matches:
        date = match.group(2)
        price = float(match.group(3))
        market_id = 103  # 默认市场
        fish_id = 1      # 鲈鱼
        
        try:
            # 检查是否已存在
            cursor.execute("""
                SELECT id FROM prices 
                WHERE market_id=%s AND fish_id=%s AND DATE(ts)=%s
            """, (market_id, fish_id, date))
            
            if cursor.fetchone():
                print(f"跳过重复数据：{date}")
                skip_count += 1
                continue
            
            # 插入数据
            cursor.execute("""
                INSERT INTO prices (market_id, fish_id, price, ts)
                VALUES (%s, %s, %s, %s)
            """, (market_id, fish_id, price, date))
            
            conn.commit()
            success_count += 1
            print(f"导入成功：{date} | {price}元")
            
        except Exception as e:
            print(f"导入失败：{date} - {e}")
            conn.rollback()
            skip_count += 1
    
    cursor.close()
    conn.close()
    
    print(f"\n导入完成：成功{success_count}条，跳过{skip_count}条")
    return success_count, skip_count

if __name__ == '__main__':
    import_verified_data('docs/verification_report.md')
```

---

## 阶段四：主流程整合

### Task 6: 创建主执行脚本

**Files:**
- Create: `backend/run_auto_import.py`

**Step 1: 编写主流程代码**

```python
# -*- coding: utf-8 -*-
"""
全自动数据导入 - 一键执行
"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("鲈鱼价格数据全自动导入系统")
print("=" * 60)

# 阶段 1：数据采集
print("\n【阶段 1】数据采集...")
from wechat_crawler import crawl_all_articles
data = crawl_all_articles('数据地址')
print(f"采集到 {len(data)} 条数据")

# 阶段 2：生成 Markdown
print("\n【阶段 2】生成待验证文档...")
from md_generator import generate_md_file
generate_md_file(data, 'docs/price_data_to_verify.md')

# 阶段 3：AI 验证
print("\n【阶段 3】AI 智能验证...")
from ai_verifier import verify_all_data
results = verify_all_data('docs/price_data_to_verify.md')

# 阶段 4：生成验证报告
print("\n【阶段 4】生成验证报告...")
from verification_report import generate_report
generate_report(results, 'docs/verification_report.md')

# 阶段 5：导入数据库
print("\n【阶段 5】导入数据库...")
from auto_import import import_verified_data
success, skip = import_verified_data('docs/verification_report.md')

# 完成
print("\n" + "=" * 60)
print("导入完成!")
print(f"成功导入：{success}条")
print(f"跳过：{skip}条")
print("=" * 60)
```

---

## 测试与运行

### 运行完整流程

```bash
cd /Users/zcy/IdeaProjects/fish-price-platform/backend
.venv/bin/python run_auto_import.py
```

### 预期输出

```
============================================================
鲈鱼价格数据全自动导入系统
============================================================

【阶段 1】数据采集...
[1/166] 爬取：https://...
  -> 提取 3 条数据
...
采集到 250 条数据

【阶段 2】生成待验证文档...
Markdown 文档已生成：docs/price_data_to_verify.md

【阶段 3】AI 智能验证...
[1] 验证：2020-03-15 | 12.5 元
  -> ✅ 通过：搜索到 5 条证据，平均价格 12.8 元，数据合理
...

【阶段 4】生成验证报告...
验证报告已生成：docs/verification_report.md

【阶段 5】导入数据库...
导入成功：2020-03-15 | 12.5 元
...

============================================================
导入完成!
成功导入：220 条
跳过：30 条
============================================================
```

---

## 输出文件

1. `docs/price_data_to_verify.md` - 原始数据文档
2. `docs/verification_report.md` - 验证报告
3. 数据库中的价格记录

---

## 注意事项

1. 微信文章可能有反爬机制，需要添加代理或延迟
2. Web 搜索验证可能需要处理验证码
3. 建议先小批量测试（前 10 条链接）
4. 验证逻辑可以根据实际情况调整

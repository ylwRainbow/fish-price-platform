#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析采集数据 - 检查为什么只有 91 条数据
"""
import sys
sys.path.insert(0, 'backend')
import os
os.environ['MYSQL_DSN'] = 'mysql://root:YOUR_PASSWORD@127.0.0.1:3306/fish_prices'
from app.db import get_conn

# 读取采集的数据
with open('docs/sohu_batch_data.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取所有日期
import re
dates = re.findall(r'\*\*日期\*\*: (\d{4}-\d{2}-\d{2})', content)
prices = re.findall(r'\*\*价格\*\*: ([\d.]+) 元/斤', content)

print(f"采集到的数据总数：{len(dates)}条")

# 查询数据库已存在的数据
conn = get_conn()
cursor = conn.cursor()
cursor.execute('SELECT ts, price FROM prices WHERE market_id=103 AND fish_id=1')
existing = cursor.fetchall()
existing_set = set((str(d), float(p)) for d, p in existing)

print(f"数据库已有数据：{len(existing)}条")

# 检查重复
new_count = 0
duplicate_count = 0
for date, price in zip(dates, prices):
    try:
        key = (date, float(price))
        if key in existing_set:
            duplicate_count += 1
        else:
            new_count += 1
    except:
        pass

print(f"\n重复数据：{duplicate_count}条 ({duplicate_count/len(dates)*100:.1f}%)")
print(f"新数据：{new_count}条 ({new_count/len(dates)*100:.1f}%)")

# 显示新数据
print(f"\n新数据列表:")
cursor.execute('SELECT ts, price FROM prices WHERE market_id=103 AND fish_id=1 ORDER BY created_at DESC LIMIT 20')
for row in cursor.fetchall():
    print(f"  {row[0]} | {row[1]}元")

cursor.close()
conn.close()

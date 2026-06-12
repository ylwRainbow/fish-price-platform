#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库数据
"""
import sys
sys.path.insert(0, 'backend')
import os
import datetime
os.environ['MYSQL_DSN'] = 'mysql://root:YOUR_PASSWORD@127.0.0.1:3306/fish_prices'
from app.db import get_conn

conn = get_conn()
cursor = conn.cursor()

# 检查鲈鱼数据
print('=== 鲈鱼数据统计 ===')
cursor.execute('SELECT COUNT(*) FROM prices WHERE market_id=103 AND fish_id=1')
total = cursor.fetchone()[0]
print(f'总数据量：{total}条')

# 按日期分组
print('\n=== 最近 20 个日期数据 ===')
cursor.execute('''
    SELECT DATE(ts) as date, COUNT(*) as count, AVG(price) as avg_price
    FROM prices 
    WHERE market_id=103 AND fish_id=1
    GROUP BY DATE(ts)
    ORDER BY date DESC
    LIMIT 20
''')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}条 | 平均价格：{row[2]:.2f}元')

# 检查今天的数据
today = datetime.date.today().isoformat()
print(f'\n=== 今天 ({today}) 数据 ===')
cursor.execute('''
    SELECT id, ts, price, price_type
    FROM prices 
    WHERE market_id=103 AND fish_id=1 AND DATE(ts)=%s
    ORDER BY ts
''', (today,))
today_data = cursor.fetchall()
print(f'今天的数据条数：{len(today_data)}')
for row in today_data:
    print(f'  {row[0]}: {row[1]} | {row[2]:.2f}元 | {row[3]}')

# 检查 API 查询逻辑
print(f'\n=== API 默认查询 ({today} 到 {today}) ===')
cursor.execute('''
    SELECT DATE(ts) as d, AVG(price) as v, MIN(currency), MIN(unit)
    FROM prices
    WHERE fish_id=1 AND market_id=103 AND DATE(ts) BETWEEN %s AND %s AND price_type='pond'
    GROUP BY d ORDER BY d
''', (today, today))
rows = cursor.fetchall()
print(f'  返回数据条数：{len(rows)}')
for row in rows:
    print(f'  {row[0]}: {row[1]:.2f}元')

# 检查价格类型分布
print('\n=== 价格类型分布 ===')
cursor.execute('''
    SELECT price_type, COUNT(*) as count
    FROM prices
    WHERE market_id=103 AND fish_id=1
    GROUP BY price_type
''')
for row in cursor.fetchall():
    print(f'  {row[0] if row[0] else "NULL"}: {row[1]}条')

cursor.close()
conn.close()

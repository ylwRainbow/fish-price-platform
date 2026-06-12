#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库数据
"""
import os
import datetime
os.environ['MYSQL_DSN'] = 'mysql://root:YOUR_PASSWORD@127.0.0.1:3306/fish_prices'
from app.db import get_conn

conn = get_conn()
cursor = conn.cursor()

# 检查市场和鱼种
print('=== 市场列表 ===')
cursor.execute('SELECT id, name FROM markets LIMIT 10')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

print('\n=== 鱼种列表 ===')
cursor.execute('SELECT id, name FROM fishes LIMIT 10')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

# 检查鲈鱼数据
print('\n=== 鲈鱼数据统计 ===')
cursor.execute('SELECT COUNT(*) FROM prices WHERE market_id=103 AND fish_id=1')
total = cursor.fetchone()[0]
print(f'总数据量: {total}条')

# 按日期分组
print('\n=== 按日期分组 ===')
cursor.execute('''
    SELECT DATE(ts) as date, COUNT(*) as count, AVG(price) as avg_price
    FROM prices 
    WHERE market_id=103 AND fish_id=1
    GROUP BY DATE(ts)
    ORDER BY date DESC
    LIMIT 20
''')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}条 | 平均价格: {row[2]:.2f}元')

# 检查今天的数据
today = datetime.date.today().isoformat()
print(f'\n=== 今天 ({today}) 数据 ===')
cursor.execute('''
    SELECT id, ts, price, price_type
    FROM prices 
    WHERE market_id=103 AND fish_id=1 AND DATE(ts)=%s
    ORDER BY ts
''', (today,))
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]} | {row[2]:.2f}元 | {row[3]}')

# 检查 API 默认日期的数据
print(f'\n=== API 默认日期 ({today}) 数据 ===')
cursor.execute('''
    SELECT DATE(ts) as d, AVG(price) as v, MIN(currency), MIN(unit)
    FROM prices
    WHERE fish_id=1 AND market_id=103 AND DATE(ts) BETWEEN %s AND %s AND price_type='pond'
    GROUP BY d ORDER BY d
''', (today, today))
rows = cursor.fetchall()
print(f'  数据条数: {len(rows)}')
for row in rows:
    print(f'  {row[0]}: {row[1]:.2f}元')

cursor.close()
conn.close()

# -*- coding: utf-8 -*-
"""检查数据库中的所有数据"""
import os
os.environ['MYSQL_DSN'] = 'mysql://root:YOUR_PASSWORD@127.0.0.1:3306/fish_prices'

from app.db import get_conn

conn = get_conn()
if conn:
    cursor = conn.cursor()
    
    # 检查所有数据统计
    print("=" * 80)
    print("数据库中的所有数据统计")
    print("=" * 80)
    
    cursor.execute("""
        SELECT market_id, fish_id, YEAR(ts) as year, COUNT(*) as count
        FROM prices
        GROUP BY market_id, fish_id, YEAR(ts)
        ORDER BY market_id, fish_id, year DESC
    """)
    results = cursor.fetchall()
    
    print(f"{'市场 ID':<10} {'鱼类 ID':<10} {'年份':<10} {'数据条数':<15}")
    print("-" * 45)
    for row in results:
        market_id, fish_id, year, count = row
        print(f"{market_id:<10} {fish_id:<10} {year:<10} {count:<15}")
    
    # 特别检查市场 103、鱼类 1（鲈鱼）
    print("\n" + "=" * 80)
    print("市场 103、鱼类 1（鲈鱼）的详细数据")
    print("=" * 80)
    
    for year in [2022, 2023, 2024, 2025]:
        cursor.execute("""
            SELECT ts, price
            FROM prices
            WHERE market_id = 103 AND fish_id = 1 AND YEAR(ts) = %s
            ORDER BY ts
            LIMIT 5
        """, (year,))
        results = cursor.fetchall()
        
        if results:
            print(f"\n{year}年（前 5 条）:")
            print(f"{'日期':<25} {'价格':<15}")
            print("-" * 40)
            for ts, price in results:
                print(f"{str(ts):<25} {price:<15.2f}")
        else:
            print(f"\n❌ {year}年没有数据!")
    
    cursor.close()
    conn.close()
else:
    print("数据库连接失败")

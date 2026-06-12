# -*- coding: utf-8 -*-
"""检查市场 103、鱼类 1 的数据"""
from app.db import get_conn

conn = get_conn()
if conn:
    cursor = conn.cursor()
    
    # 检查各年份数据统计
    print("=" * 60)
    print("市场 103、鱼类 1 的数据统计")
    print("=" * 60)
    
    cursor.execute("""
        SELECT YEAR(ts) as year, 
               COUNT(*) as count, 
               MIN(price) as min_price,
               MAX(price) as max_price,
               AVG(price) as avg_price
        FROM prices
        WHERE market_id = 103 AND fish_id = 1
        GROUP BY YEAR(ts)
        ORDER BY YEAR(ts) DESC
    """)
    results = cursor.fetchall()
    
    print(f"{'年份':<10} {'数据条数':<15} {'最低价':<15} {'最高价':<15} {'平均价':<15}")
    print("-" * 70)
    for row in results:
        year, count, min_p, max_p, avg_p = row
        print(f"{year:<10} {count:<15} {min_p:<15.2f} {max_p:<15.2f} {avg_p:<15.2f}" if avg_p else f"{year:<10} {count:<15} {'N/A':<15}")
    
    # 检查 2022-2024 年的具体数据
    for year in [2022, 2023, 2024]:
        print(f"\n{'=' * 60}")
        print(f"{year}年详细数据:")
        print("=" * 60)
        
        cursor.execute("""
            SELECT ts, price
            FROM prices
            WHERE market_id = 103 AND fish_id = 1 AND YEAR(ts) = %s
            ORDER BY ts
        """, (year,))
        results = cursor.fetchall()
        
        if results:
            print(f"共 {len(results)} 条数据:")
            print(f"{'日期':<20} {'价格':<15}")
            print("-" * 35)
            for ts, price in results:
                print(f"{str(ts):<20} {price:<15.2f}")
        else:
            print(f"  ❌ {year}年没有数据!")
    
    cursor.close()
    conn.close()
else:
    print("数据库连接失败")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据统计报告生成器
"""
import os
os.environ['MYSQL_DSN'] = 'mysql://root:YOUR_PASSWORD@127.0.0.1:3306/fish_prices'

from app.db import get_conn


def generate_report():
    """生成统计报告"""
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

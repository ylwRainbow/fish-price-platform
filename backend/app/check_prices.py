#!/usr/bin/env python3
"""
检查数据库中的鲈鱼价格数据
"""

import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from app.db import get_conn

def check_prices():
    """
    检查数据库中的价格数据
    """
    conn = get_conn()
    if not conn:
        print("无法连接数据库")
        return
    
    fish_id = 1
    
    print("=" * 80)
    print("检查数据库中的鲈鱼价格数据")
    print("=" * 80)
    
    with conn.cursor() as cur:
        cur.execute("""
            SELECT market_id, COUNT(*) as count, MIN(ts) as min_date, MAX(ts) as max_date
            FROM prices
            WHERE fish_id = %s
            GROUP BY market_id
            ORDER BY market_id
        """, (fish_id,))
        
        results = cur.fetchall()
        
        print("\n各市场数据统计：")
        print(f"{'市场ID':<10} {'数据条数':<15} {'最早日期':<15} {'最晚日期':<15}")
        print("-" * 60)
        for row in results:
            market_id, count, min_date, max_date = row
            print(f"{market_id:<10} {count:<15} {min_date.strftime('%Y-%m-%d'):<15} {max_date.strftime('%Y-%m-%d'):<15}")
        
        print("\n" + "=" * 80)
        print("湖州市场（market_id=103）数据详情：")
        print("=" * 80)
        
        cur.execute("""
            SELECT ts, price
            FROM prices
            WHERE fish_id = %s AND market_id = 103
            ORDER BY ts
        """, (fish_id,))
        
        huzhou_prices = cur.fetchall()
        
        print(f"\n湖州市场共有 {len(huzhou_prices)} 条数据\n")
        print(f"{'日期':<15} {'价格(元/斤)':<15}")
        print("-" * 30)
        
        for ts, price in huzhou_prices:
            print(f"{ts.strftime('%Y-%m-%d'):<15} {price:<15.2f}")
        
        print("\n" + "=" * 80)
        print("民众渔业市场（market_id=104）数据详情：")
        print("=" * 80)
        
        cur.execute("""
            SELECT ts, price
            FROM prices
            WHERE fish_id = %s AND market_id = 104
            ORDER BY ts
        """, (fish_id,))
        
        minzhong_prices = cur.fetchall()
        
        print(f"\n民众渔业市场共有 {len(minzhong_prices)} 条数据\n")
        print(f"{'日期':<15} {'价格(元/斤)':<15}")
        print("-" * 30)
        
        for ts, price in minzhong_prices:
            print(f"{ts.strftime('%Y-%m-%d'):<15} {price:<15.2f}")
    
    conn.close()

if __name__ == "__main__":
    check_prices()

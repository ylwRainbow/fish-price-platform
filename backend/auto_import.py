# -*- coding: utf-8 -*-
"""
自动导入验证通过的数据到数据库
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import get_conn
import re


def import_verified_data(report_file):
    """导入验证通过的数据"""
    
    # 解析验证报告
    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取通过的数据
    pattern = r'#### 第 (\d+) 条：(\d{4}-\d{2}-\d{2}) \| (\d+\.?\d*)元/斤.*?决策：\*\*导入\*\*'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    conn = get_conn()
    if not conn:
        print("数据库连接失败")
        return 0, 0
    
    cursor = conn.cursor()
    
    success_count = 0
    skip_count = 0
    
    market_id = 103  # 默认市场
    fish_id = 1      # 鲈鱼
    
    for match in matches:
        date = match.group(2)
        price = float(match.group(3))
        
        try:
            # 检查是否已存在（同日期同价格）
            cursor.execute("""
                SELECT id FROM prices 
                WHERE market_id=%s AND fish_id=%s AND DATE(ts)=%s AND price=%s
            """, (market_id, fish_id, date, price))
            
            if cursor.fetchone():
                print(f"跳过重复数据：{date} | {price}元")
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
    import_verified_data('../docs/verification_report.md')

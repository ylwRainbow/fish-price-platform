#!/usr/bin/env python3
"""
导入湖州鲈鱼历史价格数据

从MD文件解析历史价格数据并导入数据库
"""

import os
import sys
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from app.db import get_conn

def parse_price(price_str):
    """
    解析价格字符串，返回平均价格
    
    Args:
        price_str: 价格字符串，可能是 "10-11.8" 或 "14"
    
    Returns:
        float: 平均价格
    """
    price_str = price_str.strip()
    
    if '-' in price_str:
        parts = price_str.split('-')
        try:
            low = float(parts[0].strip())
            high = float(parts[1].strip())
            return round((low + high) / 2, 2)
        except ValueError:
            return None
    else:
        try:
            return float(price_str)
        except ValueError:
            return None

def parse_md_file():
    """
    解析MD文件提取价格数据
    
    Returns:
        list: 包含日期和价格的字典列表
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    project_dir = os.path.dirname(backend_dir)
    md_file = os.path.join(project_dir, 'huzhou_bass_price_history.md')
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = []
    
    pattern = r'\| (\d{4}-\d{2}-\d{2}) \| ([\d\.\-]+) \|'
    matches = re.findall(pattern, content)
    
    for date_str, price_str in matches:
        price = parse_price(price_str)
        if price:
            data.append({
                'date': date_str,
                'price': price
            })
    
    return data

def import_historical_prices():
    """
    导入历史价格数据到数据库
    """
    data = parse_md_file()
    
    if not data:
        print("没有找到历史数据")
        return
    
    conn = get_conn()
    if not conn:
        print("无法连接数据库")
        return
    
    fish_id = 1
    market_id = 103
    
    success_count = 0
    skip_count = 0
    
    print(f"准备导入 {len(data)} 条历史价格数据")
    print("=" * 60)
    
    for item in data:
        date_str = item['date']
        price = item['price']
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO prices (fish_id, market_id, price, ts, currency, unit, price_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE price = VALUES(price)
                """, (fish_id, market_id, price, date_str, 'CNY', 'kg', 'pond'))
            success_count += 1
            print(f"✓ {date_str}: {price} 元/斤")
        except Exception as e:
            skip_count += 1
            print(f"✗ {date_str}: 导入失败 - {e}")
    
    conn.commit()
    conn.close()
    
    print("=" * 60)
    print(f"导入完成: 成功 {success_count}, 跳过/失败 {skip_count}")

if __name__ == "__main__":
    import_historical_prices()

# -*- coding: utf-8 -*-
"""
泥鳅数据验证脚本
查询数据库中泥鳅的价格数据，验证完整性和正确性
"""
import os
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass

try:
    import pymysql
except ImportError:
    pymysql = None

from .db import get_conn, parse_mysql_dsn, get_dsn


LOACH_FISH_ID = 2

LOACH_ALIAS = ["泥鳅", "黄鳝苗", "鳅鱼", "泥鳅苗"]


def query_loach_data(conn) -> List[Dict[str, Any]]:
    """
    查询泥鳅价格数据
    
    Args:
        conn: 数据库连接
        
    Returns:
        泥鳅价格数据列表
    """
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("""
            SELECT 
                p.id,
                p.fish_id,
                p.market_id,
                p.price,
                p.currency,
                p.unit,
                p.ts,
                p.price_type,
                p.source_url,
                m.name as market_name,
                m.region_code,
                f.name as fish_name,
                f.alias as fish_alias
            FROM prices p
            JOIN markets m ON p.market_id = m.id
            JOIN fishes f ON p.fish_id = f.id
            WHERE p.fish_id = %s
            ORDER BY p.ts DESC
        """, (LOACH_FISH_ID,))
        return cur.fetchall()


def validate_price(price: Decimal) -> tuple:
    """
    验证价格是否合理
    
    Args:
        price: 价格
        
    Returns:
        (是否有效, 错误信息)
    """
    if price is None or price <= 0:
        return False, "价格无效或为零"
    
    if price > 100:
        return False, f"价格异常过高: {price}元/斤"
    
    if price < 1:
        return False, f"价格异常过低: {price}元/斤"
    
    return True, ""


def validate_date(ts: datetime) -> tuple:
    """
    验证日期是否合理
    
    Args:
        ts: 时间戳
        
    Returns:
        (是否有效, 错误信息)
    """
    if ts is None:
        return False, "日期为空"
    
    now = datetime.now()
    if ts > now:
        return False, f"日期在未来: {ts.strftime('%Y-%m-%d')}"
    
    if ts.year < 2015:
        return False, f"日期过早: {ts.strftime('%Y-%m-%d')}"
    
    return True, ""


def validate_source_url(source_url: str) -> tuple:
    """
    验证来源URL
    
    Args:
        source_url: 来源URL
        
    Returns:
        (是否有效, 错误信息)
    """
    if not source_url:
        return True, "无来源URL（可接受）"
    
    if not source_url.startswith(('http://', 'https://')):
        return False, f"URL格式错误: {source_url}"
    
    return True, ""


def check_duplicates(conn) -> List[Dict[str, Any]]:
    """
    检查重复数据
    
    Args:
        conn: 数据库连接
        
    Returns:
        重复数据列表
    """
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("""
            SELECT 
                fish_id,
                market_id,
                DATE(ts) as date,
                price,
                COUNT(*) as cnt,
                GROUP_CONCAT(id) as ids
            FROM prices
            WHERE fish_id = %s
            GROUP BY fish_id, market_id, DATE(ts), price
            HAVING COUNT(*) > 1
        """, (LOACH_FISH_ID,))
        return cur.fetchall()


def analyze_data_distribution(conn) -> Dict[str, Any]:
    """
    分析数据分布
    
    Args:
        conn: 数据库连接
        
    Returns:
        数据分布统计
    """
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("""
            SELECT 
                m.name as market_name,
                COUNT(*) as cnt,
                MIN(p.ts) as min_date,
                MAX(p.ts) as max_date,
                MIN(p.price) as min_price,
                MAX(p.price) as max_price,
                AVG(p.price) as avg_price
            FROM prices p
            JOIN markets m ON p.market_id = m.id
            WHERE p.fish_id = %s
            GROUP BY m.name
            ORDER BY cnt DESC
        """, (LOACH_FISH_ID,))
        return cur.fetchall()


def delete_invalid_records(conn, record_ids: List[int]) -> int:
    """
    删除无效记录
    
    Args:
        conn: 数据库连接
        record_ids: 要删除的记录ID列表
        
    Returns:
        删除的记录数
    """
    if not record_ids:
        return 0
    
    with conn.cursor() as cur:
        placeholders = ','.join(['%s'] * len(record_ids))
        cur.execute(f"DELETE FROM prices WHERE id IN ({placeholders})", record_ids)
        return cur.rowcount


def main():
    """
    主函数：验证泥鳅数据
    """
    print("=" * 60)
    print("泥鳅数据验证")
    print("=" * 60)
    
    if pymysql is None:
        print("错误: 需要安装pymysql库")
        return
    
    dsn = get_dsn()
    if not dsn:
        print("错误: 未配置数据库连接 (MYSQL_DSN)")
        return
    
    print(f"\n数据库连接: {parse_mysql_dsn(dsn)['host']}")
    
    conn = get_conn()
    if not conn:
        print("错误: 无法连接数据库")
        return
    
    print("\n1. 查询泥鳅数据...")
    data = query_loach_data(conn)
    print(f"   共查询到 {len(data)} 条泥鳅价格记录")
    
    if not data:
        print("   没有泥鳅数据，验证结束")
        conn.close()
        return
    
    print("\n2. 验证数据完整性...")
    invalid_records = []
    warnings = []
    
    for row in data:
        errors = []
        
        is_valid, error = validate_price(row['price'])
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_date(row['ts'])
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_source_url(row['source_url'])
        if not is_valid:
            errors.append(error)
        
        if errors:
            invalid_records.append({
                'id': row['id'],
                'date': row['ts'].strftime('%Y-%m-%d') if row['ts'] else 'N/A',
                'market': row['market_name'],
                'price': float(row['price']) if row['price'] else 0,
                'errors': errors
            })
    
    if invalid_records:
        print(f"\n   发现 {len(invalid_records)} 条无效记录:")
        for rec in invalid_records[:10]:
            print(f"   - ID:{rec['id']} {rec['date']} {rec['market']} {rec['price']}元/斤")
            print(f"     错误: {', '.join(rec['errors'])}")
        if len(invalid_records) > 10:
            print(f"   ... 还有 {len(invalid_records) - 10} 条无效记录")
    else:
        print("   所有记录数据验证通过")
    
    print("\n3. 检查重复数据...")
    duplicates = check_duplicates(conn)
    if duplicates:
        print(f"   发现 {len(duplicates)} 组重复数据:")
        for dup in duplicates[:5]:
            print(f"   - 市场:{dup['market_id']} 日期:{dup['date']} 价格:{dup['price']} 重复次数:{dup['cnt']}")
    else:
        print("   没有发现重复数据")
    
    print("\n4. 数据分布统计...")
    distribution = analyze_data_distribution(conn)
    print(f"\n   {'市场':<20} {'记录数':<8} {'时间范围':<25} {'价格范围(元/斤)':<20} {'均价':<10}")
    print("   " + "-" * 85)
    total = 0
    for row in distribution:
        time_range = f"{row['min_date'].strftime('%Y-%m-%d')} ~ {row['max_date'].strftime('%Y-%m-%d')}"
        price_range = f"{float(row['min_price']):.1f} ~ {float(row['max_price']):.1f}"
        avg_price = f"{float(row['avg_price']):.2f}"
        print(f"   {row['market_name']:<20} {row['cnt']:<8} {time_range:<25} {price_range:<20} {avg_price:<10}")
        total += row['cnt']
    print(f"\n   总计: {total} 条记录")
    
    if invalid_records:
        print("\n5. 处理无效数据...")
        invalid_ids = [rec['id'] for rec in invalid_records]
        print(f"   是否删除 {len(invalid_ids)} 条无效记录? (y/n): ", end="")
        
        deleted = delete_invalid_records(conn, invalid_ids)
        print(f"   已删除 {deleted} 条无效记录")
    
    print("\n" + "=" * 60)
    print("验证完成!")
    print("=" * 60)
    
    conn.close()


if __name__ == "__main__":
    main()

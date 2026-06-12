# -*- coding: utf-8 -*-
"""
黄颡鱼（汪丁鱼）历史价格数据导入脚本
从Excel文件读取数据，验证后写入数据库
"""
import os
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple, Any

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass

try:
    import pymysql
except ImportError:
    pymysql = None

try:
    from openpyxl import load_workbook
except ImportError:
    load_workbook = None

from .db import get_conn, parse_mysql_dsn, get_dsn


EXCEL_PATH = "/Users/zcy/IdeaProjects/fish-price-platform/湖州黄颡鱼塘口价历史数据.xlsx"

HUANGSHA_FISH_ID = 5

HUANGSHA_FISH_NAME = "黄颡鱼"
HUANGSHA_FISH_ALIAS = "汪丁鱼,黄骨鱼,黄辣丁"
HUANGSHA_SPECIES_CODE = "HUANGSHA"

MARKET_MAPPING = {
    "浙江湖州": 202,
    "浙江南浔区": 202,
    "浙江吴兴区": 202,
    "广东佛山": 201,
    "湖北武汉": 206,
    "湖北枝江": 206,
    "湖北荆州": 206,
    "四川眉山": 204,
    "湖南常德": 205,
    "广西南宁": 102,
    "江苏扬州": 203,
}

MARKET_NAMES = {
    201: ("广东佛山", "440600", "SOHU_BASS"),
    202: ("湖州(历史)", "330500", "SOHU_BASS"),
    203: ("江苏吴江", "320509", "SOHU_BASS"),
    204: ("四川成都", "510100", "SOHU_BASS"),
    205: ("湖南华容", "430623", "SOHU_BASS"),
    206: ("湖北武汉", "420100", "SOHU_BASS"),
    102: ("浙江省综合市场", "330000", "ZJMRK"),
}


def read_excel_data(file_path: str) -> List[Dict[str, Any]]:
    """
    读取Excel文件数据
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        数据列表
    """
    if load_workbook is None:
        print("错误: 需要安装openpyxl库")
        return []
    
    wb = load_workbook(file_path)
    ws = wb.active
    
    headers = []
    data = []
    
    for row_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
        if row_idx == 1:
            headers = [str(h) if h else f"col_{i}" for i, h in enumerate(row)]
            continue
        
        if not row[0]:
            continue
        
        row_data = {}
        for col_idx, value in enumerate(row):
            if col_idx < len(headers):
                row_data[headers[col_idx]] = value
        
        data.append(row_data)
    
    return data


def parse_price(price_str: str) -> Optional[Decimal]:
    """
    解析价格字符串
    
    Args:
        price_str: 价格字符串
        
    Returns:
        价格平均值
    """
    if not price_str:
        return None
    
    price_str = str(price_str).strip()
    
    price_str = re.sub(r'[元斤/]', '', price_str)
    
    if '-' in price_str:
        parts = price_str.split('-')
        try:
            low = Decimal(parts[0].strip())
            high = Decimal(parts[1].strip())
            return (low + high) / 2
        except (InvalidOperation, ValueError, IndexError):
            return None
    
    try:
        return Decimal(price_str.strip())
    except (InvalidOperation, ValueError):
        return None


def parse_date(date_str: str) -> Optional[datetime]:
    """
    解析日期字符串
    
    Args:
        date_str: 日期字符串
        
    Returns:
        datetime对象
    """
    if not date_str:
        return None
    
    if isinstance(date_str, datetime):
        return date_str
    
    date_str = str(date_str).strip()
    
    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def get_market_id(region: str) -> Optional[int]:
    """
    根据地区名称获取市场ID
    
    Args:
        region: 地区名称
        
    Returns:
        市场ID
    """
    if not region:
        return None
    
    region = str(region).strip()
    
    if region in MARKET_MAPPING:
        return MARKET_MAPPING[region]
    
    for key, market_id in MARKET_MAPPING.items():
        if key in region or region in key:
            return market_id
    
    return None


def validate_data(row: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    验证单条数据
    
    Args:
        row: 数据行
        
    Returns:
        (是否有效, 处理后的数据, 错误信息)
    """
    date_val = row.get("日期")
    if not date_val:
        return False, None, "日期为空"
    
    parsed_date = parse_date(date_val)
    if not parsed_date:
        return False, None, f"日期格式错误: {date_val}"
    
    region = row.get("地区", "")
    market_id = get_market_id(region)
    if not market_id:
        return False, None, f"未知地区: {region}"
    
    price_str = row.get("塘口价(元/斤)", "")
    price = parse_price(price_str)
    if price is None or price <= 0:
        return False, None, f"价格无效: {price_str}"
    
    if price > 50:
        return False, None, f"价格异常(超过50元/斤): {price_str}"
    
    source_url = row.get("来源URL", "")
    if source_url:
        source_url = str(source_url).strip()
    
    spec = row.get("规格", "")
    change = row.get("涨跌(元/斤)", "")
    remark = row.get("备注", "")
    
    return True, {
        "date": parsed_date,
        "market_id": market_id,
        "price": price,
        "source_url": source_url,
        "spec": str(spec) if spec else "",
        "change": str(change) if change else "",
        "remark": str(remark) if remark else "",
        "region": region,
    }, ""


def check_existing_price(conn, fish_id: int, market_id: int, ts: datetime, price: Decimal) -> bool:
    """
    检查数据库中是否已存在相同记录
    
    Args:
        conn: 数据库连接
        fish_id: 鱼种ID
        market_id: 市场ID
        ts: 时间戳
        price: 价格
        
    Returns:
        是否存在
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM prices 
            WHERE fish_id = %s AND market_id = %s AND DATE(ts) = %s AND price = %s
        """, (fish_id, market_id, ts.date(), price))
        result = cur.fetchone()
        return result[0] > 0 if result else False


def delete_existing_price(conn, fish_id: int, market_id: int, ts: datetime, price: Decimal) -> int:
    """
    删除已存在的相同记录
    
    Args:
        conn: 数据库连接
        fish_id: 鱼种ID
        market_id: 市场ID
        ts: 时间戳
        price: 价格
        
    Returns:
        删除的记录数
    """
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM prices 
            WHERE fish_id = %s AND market_id = %s AND DATE(ts) = %s AND price = %s
        """, (fish_id, market_id, ts.date(), price))
        return cur.rowcount


def insert_price(conn, fish_id: int, market_id: int, price: Decimal, 
                 ts: datetime, source_url: str) -> bool:
    """
    插入价格记录
    
    Args:
        conn: 数据库连接
        fish_id: 鱼种ID
        market_id: 市场ID
        price: 价格
        ts: 时间戳
        source_url: 来源URL
        
    Returns:
        是否成功
    """
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url)
            VALUES (%s, %s, %s, 'CNY', '斤', %s, 'pond', %s)
        """, (fish_id, market_id, price, ts, source_url))
        return True


def ensure_fish_exists(conn, fish_id: int, name: str, alias: str, species_code: str):
    """
    确保鱼种记录存在
    
    Args:
        conn: 数据库连接
        fish_id: 鱼种ID
        name: 名称
        alias: 别名
        species_code: 物种代码
    """
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO fishes (id, name, alias, species_code)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name = VALUES(name), alias = VALUES(alias)
        """, (fish_id, name, alias, species_code))


def ensure_market_exists(conn, market_id: int, name: str, region_code: str, source_code: str):
    """
    确保市场记录存在
    
    Args:
        conn: 数据库连接
        market_id: 市场ID
        name: 名称
        region_code: 区域代码
        source_code: 来源代码
    """
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO markets (id, name, region_code, source_code)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name = VALUES(name), region_code = VALUES(region_code)
        """, (market_id, name, region_code, source_code))


def main():
    """
    主函数：读取Excel数据并导入数据库
    """
    print("=" * 60)
    print("黄颡鱼（汪丁鱼）历史价格数据导入")
    print("=" * 60)
    
    if pymysql is None:
        print("错误: 需要安装pymysql库")
        return
    
    if load_workbook is None:
        print("错误: 需要安装openpyxl库")
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
    
    print(f"读取Excel文件: {EXCEL_PATH}")
    raw_data = read_excel_data(EXCEL_PATH)
    print(f"读取到 {len(raw_data)} 条原始数据")
    
    print("\n验证数据...")
    valid_data = []
    invalid_count = 0
    errors = {}
    
    for row in raw_data:
        is_valid, processed_data, error = validate_data(row)
        if is_valid:
            valid_data.append(processed_data)
        else:
            invalid_count += 1
            if error not in errors:
                errors[error] = 0
            errors[error] += 1
    
    print(f"有效数据: {len(valid_data)} 条")
    print(f"无效数据: {invalid_count} 条")
    
    if errors:
        print("\n错误统计:")
        for error, count in sorted(errors.items(), key=lambda x: -x[1]):
            print(f"  - {error}: {count} 条")
    
    print("\n确保基础数据存在...")
    ensure_fish_exists(conn, HUANGSHA_FISH_ID, HUANGSHA_FISH_NAME, HUANGSHA_FISH_ALIAS, HUANGSHA_SPECIES_CODE)
    
    for market_id, (name, region_code, source_code) in MARKET_NAMES.items():
        ensure_market_exists(conn, market_id, name, region_code, source_code)
    
    print("\n导入数据...")
    inserted = 0
    updated = 0
    skipped = 0
    
    for data in valid_data:
        try:
            exists = check_existing_price(conn, HUANGSHA_FISH_ID, data["market_id"], data["date"], data["price"])
            
            if exists:
                delete_existing_price(conn, HUANGSHA_FISH_ID, data["market_id"], data["date"], data["price"])
                updated += 1
            else:
                inserted += 1
            
            insert_price(conn, HUANGSHA_FISH_ID, data["market_id"], data["price"], data["date"], data["source_url"])
            
        except Exception as e:
            print(f"  错误: {data['date']} {data['region']} - {e}")
            skipped += 1
    
    print(f"\n导入完成:")
    print(f"  - 新增: {inserted} 条")
    print(f"  - 更新: {updated} 条")
    print(f"  - 跳过: {skipped} 条")
    print(f"  - 总计: {inserted + updated} 条")
    
    print("\n验证导入结果...")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT m.name, COUNT(*) as cnt, MIN(p.ts) as min_date, MAX(p.ts) as max_date
            FROM prices p
            JOIN markets m ON p.market_id = m.id
            WHERE p.fish_id = %s
            GROUP BY m.name
            ORDER BY cnt DESC
        """, (HUANGSHA_FISH_ID,))
        results = cur.fetchall()
        
        print("\n各市场数据统计:")
        total = 0
        for row in results:
            print(f"  - {row[0]}: {row[1]} 条 ({row[2].strftime('%Y-%m-%d')} ~ {row[3].strftime('%Y-%m-%d')})")
            total += row[1]
        
        print(f"\n总计: {total} 条价格记录")
    
    conn.close()
    print("\n" + "=" * 60)
    print("导入完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()

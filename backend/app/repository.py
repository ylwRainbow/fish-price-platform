from typing import List, Dict, Any, Optional, Tuple
from .db import get_conn

def ensure_catalog(fishes: List[Dict[str,Any]], markets: List[Dict[str,Any]]):
    conn = get_conn()
    if not conn: return False
    with conn.cursor() as cur:
        for f in fishes:
            cur.execute("""
                INSERT INTO fishes(id, name, alias, species_code)
                VALUES (%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE name=VALUES(name), alias=VALUES(alias), species_code=VALUES(species_code)
            """, (f["id"], f["name"], f.get("alias"), f.get("species_code")))
        for m in markets:
            cur.execute("""
                INSERT INTO markets(id, name, region_code, source_code)
                VALUES (%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE name=VALUES(name), region_code=VALUES(region_code), source_code=VALUES(source_code)
            """, (m["id"], m["name"], m.get("region_code"), m.get("source_code")))
    return True

def insert_prices(fish_id:int, market_id:int, points:List[Dict[str,Any]], price_type:str="pond", source_url:Optional[str]=None):
    conn = get_conn()
    if not conn: return False
    with conn.cursor() as cur:
        for p in points:
            cur.execute("""
                INSERT IGNORE INTO prices(fish_id, market_id, price, currency, unit, ts, price_type, source_url)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (fish_id, market_id, p["price"], p.get("currency","CNY"), p.get("unit","kg"), p["ts"], price_type, source_url))
    return True

def query_prices(fish_id:int, market_id:int, start:str, end:str, granularity:str="day", price_type:str="pond") -> List[Dict[str,Any]]:
    conn = get_conn()
    if not conn: return []
    with conn.cursor() as cur:
        if granularity == "day":
            cur.execute("""
                SELECT DATE(ts) AS d, AVG(price) AS v, MIN(currency), MIN(unit)
                  FROM prices
                 WHERE fish_id=%s AND market_id=%s AND DATE(ts) BETWEEN %s AND %s AND price_type=%s
                 GROUP BY d ORDER BY d
            """, (fish_id, market_id, start, end, price_type))
        elif granularity == "week":
            cur.execute("""
                SELECT DATE(DATE_SUB(ts, INTERVAL WEEKDAY(ts) DAY)) AS d, AVG(price) AS v, MIN(currency), MIN(unit)
                  FROM prices
                 WHERE fish_id=%s AND market_id=%s AND DATE(ts) BETWEEN %s AND %s AND price_type=%s
                 GROUP BY d ORDER BY d
            """, (fish_id, market_id, start, end, price_type))
        else:
            cur.execute("""
                SELECT DATE_FORMAT(ts,'%Y-%m-01') AS d, AVG(price) AS v, MIN(currency), MIN(unit)
                  FROM prices
                 WHERE fish_id=%s AND market_id=%s AND DATE(ts) BETWEEN %s AND %s AND price_type=%s
                 GROUP BY d ORDER BY d
            """, (fish_id, market_id, start, end, price_type))
        rows = cur.fetchall()
    return [{"ts": str(r[0])+"T00:00:00+08:00", "price": float(r[1]), "currency": r[2], "unit": r[3]} for r in rows]


def get_saved_periods(period_type: str, limit: int = 20) -> List[Dict[str, Any]]:
    """获取已保存的时间段列表
    
    Args:
        period_type: 时间段类型（lunar 或 solar）
        limit: 最大返回数量，默认 20
        
    Returns:
        时间段列表
    """
    conn = get_conn()
    if not conn:
        return []
    
    table = f"saved_{period_type}_periods"
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT id, name, start_date, end_date, created_at, updated_at
            FROM {table}
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
    
    return [{
        "id": r[0],
        "name": r[1],
        "start_date": r[2],
        "end_date": r[3],
        "created_at": r[4],
        "updated_at": r[5]
    } for r in rows]


def count_saved_periods(period_type: str) -> int:
    """统计已保存的时间段数量
    
    Args:
        period_type: 时间段类型（lunar 或 solar）
        
    Returns:
        时间段数量
    """
    conn = get_conn()
    if not conn:
        return 0
    
    table = f"saved_{period_type}_periods"
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        row = cur.fetchone()
    
    return row[0] if row else 0


def save_period(period_type: str, name: str, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
    """保存时间段
    
    Args:
        period_type: 时间段类型（lunar 或 solar）
        name: 时间段名称
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        
    Returns:
        保存成功的记录，失败返回 None
    """
    conn = get_conn()
    if not conn:
        return None
    
    table = f"saved_{period_type}_periods"
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {table} (name, start_date, end_date)
                VALUES (%s, %s, %s)
            """, (name, start_date, end_date))
            conn.commit()
            
            # 获取刚插入的记录
            cur.execute(f"""
                SELECT id, name, start_date, end_date, created_at, updated_at
                FROM {table}
                WHERE id = %s
            """, (cur.lastrowid,))
            row = cur.fetchone()
        
        return {
            "id": row[0],
            "name": row[1],
            "start_date": row[2],
            "end_date": row[3],
            "created_at": row[4],
            "updated_at": row[5]
        } if row else None
        
    except Exception as e:
        conn.rollback()
        print(f"保存时间段失败：{e}")
        return None
    finally:
        conn.close()


def delete_saved_period(period_type: str, period_id: int) -> bool:
    """删除时间段
    
    Args:
        period_type: 时间段类型（lunar 或 solar）
        period_id: 时间段 ID
        
    Returns:
        是否删除成功
    """
    conn = get_conn()
    if not conn:
        return False
    
    table = f"saved_{period_type}_periods"
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                DELETE FROM {table}
                WHERE id = %s
            """, (period_id,))
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"删除时间段失败：{e}")
        return False
    finally:
        conn.close()


def update_saved_period(period_type: str, period_id: int, name: str) -> Optional[Dict[str, Any]]:
    """更新时间段名称
    
    Args:
        period_type: 时间段类型（lunar 或 solar）
        period_id: 时间段 ID
        name: 新名称
        
    Returns:
        更新成功的记录，失败返回 None
    """
    conn = get_conn()
    if not conn:
        return None
    
    table = f"saved_{period_type}_periods"
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                UPDATE {table}
                SET name = %s
                WHERE id = %s
            """, (name, period_id))
            conn.commit()
            
            if cur.rowcount > 0:
                cur.execute(f"""
                    SELECT id, name, start_date, end_date, created_at, updated_at
                    FROM {table}
                    WHERE id = %s
                """, (period_id,))
                row = cur.fetchone()
                
                return {
                    "id": row[0],
                    "name": row[1],
                    "start_date": row[2],
                    "end_date": row[3],
                    "created_at": row[4],
                    "updated_at": row[5]
                } if row else None
        return None
    except Exception as e:
        conn.rollback()
        print(f"更新时间段失败：{e}")
        return None
    finally:
        conn.close()


def get_saved_combinations(period_type: str, limit: int = 20) -> List[Dict[str, Any]]:
    """获取已保存的时间段组合列表
    
    Args:
        period_type: 时间段类型（lunar 或 solar）
        limit: 最大返回数量，默认 20
        
    Returns:
        时间段组合列表
    """
    conn = get_conn()
    if not conn:
        return []
    
    table = f"saved_{period_type}_combinations"
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT id, name, periods, created_at, updated_at
            FROM {table}
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
    
    import json
    return [{
        "id": r[0],
        "name": r[1],
        "periods": json.loads(r[2]) if isinstance(r[2], str) else r[2],
        "created_at": r[3],
        "updated_at": r[4]
    } for r in rows]


def save_combination(period_type: str, name: str, periods: list) -> Optional[Dict[str, Any]]:
    """保存时间段组合
    
    Args:
        period_type: 时间段类型（lunar 或 solar）
        name: 组合名称
        periods: 时间段列表，每个元素包含 name, start, end
        
    Returns:
        保存成功的记录，失败返回 None
    """
    conn = get_conn()
    if not conn:
        return None
    
    table = f"saved_{period_type}_combinations"
    import json
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {table} (name, periods)
                VALUES (%s, %s)
            """, (name, json.dumps(periods, ensure_ascii=False)))
            conn.commit()
            
            # 获取刚插入的记录
            cur.execute(f"""
                SELECT id, name, periods, created_at, updated_at
                FROM {table}
                WHERE id = %s
            """, (cur.lastrowid,))
            row = cur.fetchone()
        
        return {
            "id": row[0],
            "name": row[1],
            "periods": json.loads(row[2]) if isinstance(row[2], str) else row[2],
            "created_at": row[3],
            "updated_at": row[4]
        } if row else None
        
    except Exception as e:
        conn.rollback()
        print(f"保存时间段组合失败：{e}")
        return None
    finally:
        conn.close()


def delete_saved_combination(period_type: str, combination_id: int) -> bool:
    """删除时间段组合
    
    Args:
        period_type: 时间段类型（lunar 或 solar）
        combination_id: 组合 ID
        
    Returns:
        是否删除成功
    """
    conn = get_conn()
    if not conn:
        return False
    
    table = f"saved_{period_type}_combinations"
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                DELETE FROM {table}
                WHERE id = %s
            """, (combination_id,))
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"删除时间段组合失败：{e}")
        return False
    finally:
        conn.close()

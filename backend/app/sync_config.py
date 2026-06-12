# -*- coding: utf-8 -*-
"""
同步配置文件中的鱼种和市场到数据库
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass

import yaml
from .db import get_conn, get_dsn, parse_mysql_dsn

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")


def load_config():
    """
    加载配置文件
    
    Returns:
        配置字典
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def sync_fishes(conn, fishes_config):
    """
    同步鱼种配置到数据库
    
    Args:
        conn: 数据库连接
        fishes_config: 鱼种配置列表
    """
    with conn.cursor() as cur:
        for fish in fishes_config:
            cur.execute("""
                INSERT INTO fishes (id, name, alias, species_code)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name), alias = VALUES(alias)
            """, (fish["id"], fish["name"], fish.get("alias", ""), fish.get("species_code", "")))
    print(f"已同步 {len(fishes_config)} 个鱼种")


def sync_markets(conn, markets_config):
    """
    同步市场配置到数据库
    
    Args:
        conn: 数据库连接
        markets_config: 市场配置列表
    """
    with conn.cursor() as cur:
        for market in markets_config:
            try:
                cur.execute("""
                    INSERT INTO markets (id, name, region_code, source_code)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE name = VALUES(name), region_code = VALUES(region_code), source_code = VALUES(source_code)
                """, (market["id"], market["name"], market.get("region_code", ""), market.get("source_code", "")))
            except Exception as e:
                print(f"  警告: 市场 {market['name']} 同步失败: {e}")
    print(f"已同步 {len(markets_config)} 个市场")


def main():
    """
    主函数：同步配置到数据库
    """
    print("=" * 60)
    print("同步配置到数据库")
    print("=" * 60)
    
    dsn = get_dsn()
    if not dsn:
        print("错误: 未配置数据库连接 (MYSQL_DSN)")
        return
    
    print(f"\n数据库连接: {parse_mysql_dsn(dsn)['host']}")
    
    conn = get_conn()
    if not conn:
        print("错误: 无法连接数据库")
        return
    
    config = load_config()
    
    print("\n同步鱼种...")
    sync_fishes(conn, config.get("fishes", []))
    
    print("\n同步市场...")
    sync_markets(conn, config.get("markets", []))
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("同步完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()

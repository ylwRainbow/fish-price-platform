# -*- coding: utf-8 -*-
"""
检查数据库和配置文件的一致性
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
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_consistency():
    """
    检查数据库和配置文件的一致性
    """
    print("=" * 60)
    print("数据库与配置文件一致性检查")
    print("=" * 60)
    
    dsn = get_dsn()
    if not dsn:
        print("错误: 未配置数据库连接")
        return
    
    conn = get_conn()
    if not conn:
        print("错误: 无法连接数据库")
        return
    
    config = load_config()
    
    print("\n1. 检查鱼种配置...")
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, alias, species_code FROM fishes ORDER BY id")
        db_fishes = {r[0]: {"name": r[1], "alias": r[2], "species_code": r[3]} for r in cur.fetchall()}
    
    config_fishes = {f["id"]: f for f in config.get("fishes", [])}
    
    print(f"\n   配置文件鱼种: {len(config_fishes)} 个")
    print(f"   数据库鱼种: {len(db_fishes)} 个")
    
    fish_issues = []
    for fish_id, fish_config in config_fishes.items():
        if fish_id not in db_fishes:
            fish_issues.append(f"   - 鱼种ID {fish_id} ({fish_config['name']}) 在数据库中不存在")
        elif db_fishes[fish_id]["name"] != fish_config["name"]:
            fish_issues.append(f"   - 鱼种ID {fish_id} 名称不一致: 配置'{fish_config['name']}' vs 数据库'{db_fishes[fish_id]['name']}'")
    
    if fish_issues:
        print("\n   问题:")
        for issue in fish_issues:
            print(issue)
    else:
        print("   ✅ 鱼种配置一致")
    
    print("\n2. 检查市场配置...")
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, region_code, source_code FROM markets ORDER BY id")
        db_markets = {r[0]: {"name": r[1], "region_code": r[2], "source_code": r[3]} for r in cur.fetchall()}
    
    config_markets = {m["id"]: m for m in config.get("markets", [])}
    
    print(f"\n   配置文件市场: {len(config_markets)} 个")
    print(f"   数据库市场: {len(db_markets)} 个")
    
    market_issues = []
    for market_id, market_config in config_markets.items():
        if market_id not in db_markets:
            market_issues.append(f"   - 市场ID {market_id} ({market_config['name']}) 在数据库中不存在")
        elif db_markets[market_id]["name"] != market_config["name"]:
            market_issues.append(f"   - 市场ID {market_id} 名称不一致: 配置'{market_config['name']}' vs 数据库'{db_markets[market_id]['name']}'")
    
    if market_issues:
        print("\n   问题:")
        for issue in market_issues:
            print(issue)
    else:
        print("   ✅ 市场配置一致")
    
    print("\n3. 检查价格数据...")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT f.name as fish_name, m.name as market_name, COUNT(*) as cnt
            FROM prices p
            JOIN fishes f ON p.fish_id = f.id
            JOIN markets m ON p.market_id = m.id
            GROUP BY f.name, m.name
            ORDER BY f.name, cnt DESC
        """)
        price_stats = cur.fetchall()
        
        print("\n   价格数据分布:")
        current_fish = None
        for row in price_stats:
            if current_fish != row[0]:
                current_fish = row[0]
                print(f"\n   【{row[0]}】")
            print(f"      - {row[1]}: {row[2]} 条")
    
    print("\n4. 检查API接口参数...")
    
    print("\n   后端API接口:")
    print("   - GET /api/fishes - 返回鱼种列表")
    print("   - GET /api/markets - 返回市场列表")
    print("   - GET /api/prices - 参数: fish_id, market_id, start, end, granularity, lunar_mode")
    print("   - POST /api/prices - 参数: fish_id, market_id, price, ts, currency, unit, price_type, source_url")
    
    print("\n   前端调用:")
    print("   - 从 /config.yaml 加载鱼种和市场配置")
    print("   - 调用 /api/prices 获取价格数据")
    
    print("\n" + "=" * 60)
    print("检查完成!")
    print("=" * 60)
    
    conn.close()


if __name__ == "__main__":
    check_consistency()

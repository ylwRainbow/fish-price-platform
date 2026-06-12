import sys
import csv
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_conn

def load_fish_market_map():
    conn = get_conn()
    if not conn:
        return {}, {}
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, alias, species_code FROM fishes")
        fish_map = {}
        for r in cur.fetchall():
            fish_map[r[0]] = r[0]
            fish_map[r[1]] = r[0]
            if r[2]:
                fish_map[r[2]] = r[0]
            if r[3]:
                fish_map[r[3]] = r[0]
        cur.execute("SELECT id, name, source_code FROM markets")
        market_map = {}
        for r in cur.fetchall():
            market_map[r[0]] = r[0]
            market_map[r[1]] = r[0]
            if r[2]:
                market_map[r[2]] = r[0]
    return fish_map, market_map

def import_csv(file_path: str):
    fish_map, market_map = load_fish_market_map()
    if not fish_map or not market_map:
        print("Error: Cannot load fish/market data from database")
        return False
    print(f"Loaded {len(fish_map)} fishes, {len(market_map)} markets")
    conn = get_conn()
    if not conn:
        print("Error: Cannot connect to database")
        return False
    added = 0
    skipped = 0
    errors = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            try:
                fish_key = row.get('fish_code') or row.get('fish_name') or row.get('fish')
                market_key = row.get('market_code') or row.get('market_name') or row.get('market')
                price_str = row.get('price') or row.get('价格')
                date_str = row.get('ts') or row.get('date') or row.get('日期') or row.get('date_str')
                if not all([fish_key, market_key, price_str, date_str]):
                    print(f"Row {row_num}: Missing required fields, skipped")
                    skipped += 1
                    continue
                fish_id = fish_map.get(fish_key)
                market_id = market_map.get(market_key)
                if not fish_id:
                    print(f"Row {row_num}: Unknown fish '{fish_key}', skipped")
                    skipped += 1
                    continue
                if not market_id:
                    print(f"Row {row_num}: Unknown market '{market_key}', skipped")
                    skipped += 1
                    continue
                try:
                    price = float(price_str)
                except:
                    print(f"Row {row_num}: Invalid price '{price_str}', skipped")
                    skipped += 1
                    continue
                try:
                    if 'T' in date_str:
                        ts = date_str
                    else:
                        ts = date_str + "T00:00:00+08:00"
                    datetime.fromisoformat(ts.replace('Z', '+00:00'))
                except:
                    print(f"Row {row_num}: Invalid date '{date_str}', skipped")
                    skipped += 1
                    continue
                currency = row.get('currency', 'CNY') or row.get('货币', 'CNY')
                unit = row.get('unit', 'kg') or row.get('单位', 'kg')
                price_type = row.get('price_type', 'pond') or row.get('价格类型', 'pond')
                source_url = row.get('source_url') or row.get('来源') or None
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT IGNORE INTO prices(fish_id, market_id, price, currency, unit, ts, price_type, source_url)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (fish_id, market_id, price, currency, unit, ts, price_type, source_url))
                added += 1
            except Exception as e:
                print(f"Row {row_num}: Error - {e}")
                errors += 1
    conn.commit()
    print(f"\nImport completed: added={added}, skipped={skipped}, errors={errors}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.import_csv <csv_file>")
        print("\nCSV format:")
        print("  fish_code,market_code,price,ts,currency,unit,price_type,source_url")
        print("  or")
        print("  fish_name,market_name,价格,日期,货币,单位,价格类型,来源")
        print("\nExample:")
        print("  fish_code,market_code,price,ts")
        print("  loach,SH,12.5,2024-01-15")
        print("  grass_carp,MZYY,8.2,2024-01-15")
        sys.exit(1)
    csv_file = sys.argv[1]
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        sys.exit(1)
    import_csv(csv_file)

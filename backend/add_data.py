import pymysql

conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='YOUR_PASSWORD',
    database='fish_prices',
    charset='utf8mb4'
)

# 要插入的数据 (日期, 价格)
data = [
    ('2026-02-05', 8.0),
    ('2026-02-15', 7.4),
    ('2026-03-15', 4.8),
]

fish_id = 2  # 泥鳅
market_id = 104  # 民众渔业

with conn.cursor() as cur:
    for date_str, price in data:
        cur.execute("""
            INSERT INTO prices (fish_id, market_id, price, ts, currency, unit, price_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE price = VALUES(price)
        """, (fish_id, market_id, price, date_str, 'CNY', 'kg', 'pond'))
        print(f'已插入: {date_str} - {price} 元/斤')
    conn.commit()

print('数据补充完成!')

# 验证
with conn.cursor() as cur:
    cur.execute("SELECT ts, price FROM prices WHERE fish_id=2 AND market_id=104 AND ts >= '2026-01-01' ORDER BY ts")
    rows = cur.fetchall()
    print(f'2026年数据验证 ({len(rows)} 条):')
    for r in rows:
        print(f'  {r[0]}: {r[1]} 元/斤')

conn.close()

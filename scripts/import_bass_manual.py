# -*- coding: utf-8 -*-
"""
加州鲈价格数据导入脚本 - 手动数据版
从搜狐"杰大饲料特约·加州鲈行情周报"获取塘口价数据
"""
import pymysql
from datetime import datetime

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'YOUR_PASSWORD',
    'database': 'fish_prices',
    'charset': 'utf8mb4'
}

FISH_ID = 1

BASS_PRICE_DATA = [
    {
        'date': '2026-03-04',
        'source': 'https://m.sohu.com/a/992571562_210667/',
        'prices': {
            '广东佛山': {'1斤上': 8.1, '9两上': 8.05, '8两上': 8.55},
            '浙江湖州': {'8成统货': 9.0},
            '江苏吴江': {'9两上': 9.25},
            '四川成都': {'1斤上': 11.0},
            '湖南华容': {'9两上': 9.75},
            '湖北武汉': {'8.5两上': 9.5},
            '河南郑州': {'1斤上': 10.5}
        }
    },
    {
        'date': '2026-02-25',
        'source': 'https://m.sohu.com/a/989985535_210667/',
        'prices': {
            '广东佛山': {'1斤上': 8.6, '9两上': 8.5, '8两上': 8.9},
            '浙江湖州': {'8成统货': 9.25},
            '江苏吴江': {'9两上': 9.5},
            '四川成都': {'1斤上': 11.0},
            '湖南华容': {'9两上': 9.5},
            '湖北武汉': {'8.5两上': 9.5},
            '河南郑州': {'1斤上': 10.5}
        }
    },
    {
        'date': '2026-02-11',
        'source': 'https://m.sohu.com/a/989622806_210667/',
        'prices': {
            '广东佛山': {'1斤上': 8.4, '9两上': 8.3, '8两上': 8.7},
            '浙江湖州': {'8成统货': 9.25},
            '江苏吴江': {'9两上': 9.5},
            '四川成都': {'1斤上': 11.0},
            '湖南华容': {'9两上': 10.0},
            '湖北武汉': {'8.5两上': 9.5},
            '河南郑州': {'1斤上': 10.5}
        }
    },
    {
        'date': '2025-12-24',
        'source': 'https://www.sohu.com/a/968994799_210667',
        'prices': {
            '广东佛山': {'1斤上': 9.0, '9两上': 9.2, '8两上': 9.0},
            '浙江湖州': {'8成统货': 10.5},
            '江苏吴江': {'9两上': 10.5},
            '四川成都': {'1斤上': 11.0},
            '湖南华容': {'9两上': 10.5},
            '湖北武汉': {'8.5两上': 10.0},
            '河南郑州': {'1斤上': 11.0}
        }
    },
    {
        'date': '2025-12-10',
        'source': 'https://www.sohu.com/a/951315758_210667',
        'prices': {
            '广东佛山': {'1斤上': 9.0, '9两上': 9.0, '8两上': 8.9},
            '浙江湖州': {'8成统货': 10.5},
            '江苏吴江': {'9两上': 10.5},
            '四川成都': {'1斤上': 11.0},
            '湖南华容': {'9两上': 10.5},
            '湖北武汉': {'8.5两上': 10.0},
            '河南郑州': {'1斤上': 11.0}
        }
    },
    {
        'date': '2025-11-26',
        'source': 'https://www.sohu.com/a/946535621_210667',
        'prices': {
            '广东佛山': {'1斤上': 9.2, '9两上': 9.0, '8两上': 8.9},
            '浙江湖州': {'8成统货': 10.5},
            '江苏吴江': {'9两上': 10.5},
            '四川成都': {'1斤上': 11.0},
            '湖南华容': {'9两上': 10.5},
            '湖北武汉': {'8.5两上': 10.0},
            '河南郑州': {'1斤上': 11.0}
        }
    },
    {
        'date': '2025-05-21',
        'source': 'https://www.sohu.com/a/897442360_210667',
        'prices': {
            '广东佛山': {'1斤上': 22.5, '8两上': 21.5},
            '浙江湖州': {'8成统货': 20.5},
            '江苏吴江': {'9两上': 20.5},
            '四川成都': {'1斤上': 21.0},
            '湖南华容': {'9两上': 20.0},
            '湖北武汉': {'8.5两上': 20.0},
            '河南郑州': {'1斤上': 21.0}
        }
    },
    {
        'date': '2025-06-10',
        'source': 'https://www.sohu.com/a/919232291_210667',
        'prices': {
            '广东佛山': {'1斤上': 19.5, '9两上': 19.0},
            '浙江湖州': {'8成统货': 18.5},
            '江苏吴江': {'9两上': 18.5},
            '四川成都': {'1斤上': 19.0},
            '湖南华容': {'9两上': 18.0},
            '湖北武汉': {'8.5两上': 18.0},
            '河南郑州': {'1斤上': 19.0}
        }
    }
]

MARKET_ID_MAP = {
    '广东佛山': 201,
    '浙江湖州': 202,
    '江苏吴江': 203,
    '四川成都': 204,
    '湖南华容': 205,
    '湖北武汉': 206,
    '河南郑州': 207
}

def save_to_database():
    """保存价格数据到数据库"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    inserted = 0
    for data in BASS_PRICE_DATA:
        date = data['date']
        source = data['source']
        
        for market_name, specs in data['prices'].items():
            market_id = MARKET_ID_MAP.get(market_name)
            if not market_id:
                continue
            
            for spec, price in specs.items():
                try:
                    sql = """
                    INSERT INTO prices (fish_id, market_id, price, ts, price_type, source_url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE price = VALUES(price)
                    """
                    cursor.execute(sql, (
                        FISH_ID,
                        market_id,
                        price,
                        date,
                        'pond',
                        source
                    ))
                    if cursor.rowcount > 0:
                        inserted += 1
                        print("插入: {} {} {} {}元/斤".format(date, market_name, spec, price))
                except Exception as e:
                    print("Insert error: {}".format(e))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return inserted

def main():
    """主函数"""
    print("=" * 60)
    print("加州鲈价格数据导入脚本")
    print("=" * 60)
    
    print("\n正在写入数据库...")
    inserted = save_to_database()
    print("\n成功写入 {} 条记录".format(inserted))
    print("\n完成！")

if __name__ == '__main__':
    main()

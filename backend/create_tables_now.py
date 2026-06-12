# -*- coding: utf-8 -*-
"""立即创建组合表"""
import os
os.environ['MYSQL_DSN'] = 'mysql://root:YOUR_PASSWORD@127.0.0.1:3306/fish_prices'

from app.db import get_conn

conn = get_conn()
if conn:
    cursor = conn.cursor()
    
    # 创建农历组合表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_lunar_combinations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            periods JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    
    # 创建公历组合表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_solar_combinations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            periods JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    
    conn.commit()
    print('表创建成功')
    cursor.close()
    conn.close()
else:
    print('数据库连接失败')

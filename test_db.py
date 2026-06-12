#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库连接
"""
import pymysql

print('pymysql 版本:', pymysql.__version__)

try:
    # 尝试连接 MySQL 服务器
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='YOUR_PASSWORD',
        database='fish_prices',
        charset='utf8mb4'
    )
    print('✅ 数据库连接成功！')
    
    # 检查数据库版本
    cursor = conn.cursor()
    cursor.execute('SELECT VERSION()')
    version = cursor.fetchone()[0]
    print(f'📦 MySQL 版本: {version}')
    
    # 检查表结构
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    print(f'📋 数据库表: {[t[0] for t in tables]}')
    
    # 检查鲈鱼数据
    cursor.execute('SELECT COUNT(*) FROM prices WHERE market_id=103 AND fish_id=1')
    count = cursor.fetchone()[0]
    print(f'🐟 鲈鱼数据: {count}条')
    
    cursor.close()
    conn.close()
    print('\n✅ 数据库运行正常！')
except Exception as e:
    print('❌ 连接失败:', e)
    
    # 尝试只连接到 MySQL 服务器（不指定数据库）
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='YOUR_PASSWORD',
            charset='utf8mb4'
        )
        print('\n✅ 连接到 MySQL 服务器成功！')
        
        # 检查数据库是否存在
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES LIKE 'fish_prices'")
        if cursor.fetchone():
            print('✅ 数据库 fish_prices 存在！')
        else:
            print('❌ 数据库 fish_prices 不存在！')
            
        cursor.close()
        conn.close()
    except Exception as e2:
        print(f'❌ 连接到 MySQL 服务器失败: {e2}')

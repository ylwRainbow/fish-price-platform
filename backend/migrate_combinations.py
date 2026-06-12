# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 添加时间段组合表
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.db import get_conn

conn = get_conn()
if not conn:
    print("数据库连接失败，请检查配置")
    sys.exit(1)

cursor = conn.cursor()

# 创建农历组合表
cursor.execute("""
CREATE TABLE IF NOT EXISTS `saved_lunar_combinations` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `periods` JSON NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""")

# 创建公历组合表
cursor.execute("""
CREATE TABLE IF NOT EXISTS `saved_solar_combinations` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `periods` JSON NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""")

conn.commit()
print("时间段组合表创建成功")

cursor.close()
conn.close()

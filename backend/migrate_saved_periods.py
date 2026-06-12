"""
创建保存时间段功能的数据库表
"""
from app.db import get_conn

def migrate():
    """创建 saved_solar_periods 和 saved_lunar_periods 表"""
    conn = get_conn()
    if not conn:
        print("数据库连接失败")
        return False
    
    try:
        with conn.cursor() as cur:
            # 创建阳历时间段表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS saved_solar_periods (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_created_at (created_at DESC)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 创建农历时间段表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS saved_lunar_periods (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_created_at (created_at DESC)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            conn.commit()
            
        print("✅ 数据库表创建成功：saved_solar_periods, saved_lunar_periods")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 数据库迁移失败：{e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

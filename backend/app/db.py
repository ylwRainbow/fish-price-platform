import os
from typing import Optional
from urllib.parse import urlparse
try:
    import pymysql
except Exception:
    pymysql = None

def get_dsn() -> Optional[str]:
    return os.environ.get("MYSQL_DSN")

def parse_mysql_dsn(dsn: str):
    u = urlparse(dsn)
    return {
        "host": u.hostname or "127.0.0.1",
        "port": u.port or 3306,
        "user": u.username or "root",
        "password": u.password or "",
        "database": (u.path or "/").lstrip("/") or None
    }

def get_conn():
    dsn = get_dsn()
    if not dsn or not pymysql:
        return None
    try:
        cfg = parse_mysql_dsn(dsn)
        return pymysql.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            autocommit=True,
            charset="utf8mb4"
        )
    except Exception:
        return None

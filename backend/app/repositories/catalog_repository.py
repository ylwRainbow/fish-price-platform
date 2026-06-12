from typing import Any

from app.db import get_conn
from app.repositories.errors import RepositoryUnavailableError


def _get_conn():
    conn = get_conn()
    if conn is None:
        raise RepositoryUnavailableError("Database is not configured or unavailable")
    return conn


def list_fishes(q: str | None = None) -> list[dict[str, Any]]:
    conn = _get_conn()
    try:
        sql = """
            SELECT id, name, alias, species_code
            FROM fishes
        """
        params: tuple[Any, ...] = ()
        if q:
            like = f"%{q}%"
            sql += " WHERE name LIKE %s OR alias LIKE %s OR species_code LIKE %s"
            params = (like, like, like)
        sql += " ORDER BY id"

        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "alias": row[2],
            "species_code": row[3],
        }
        for row in rows
    ]


def list_markets(region_code: str | None = None) -> list[dict[str, Any]]:
    conn = _get_conn()
    try:
        sql = """
            SELECT id, name, region_code, source_code
            FROM markets
        """
        params: tuple[Any, ...] = ()
        if region_code:
            sql += " WHERE region_code = %s"
            params = (region_code,)
        sql += " ORDER BY id"

        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "region_code": row[2],
            "source_code": row[3],
        }
        for row in rows
    ]


def get_fish(fish_id: int) -> dict[str, Any] | None:
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, alias, species_code
                FROM fishes
                WHERE id = %s
                """,
                (fish_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "alias": row[2],
        "species_code": row[3],
    }


def get_market(market_id: int) -> dict[str, Any] | None:
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, region_code, source_code
                FROM markets
                WHERE id = %s
                """,
                (market_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "region_code": row[2],
        "source_code": row[3],
    }

from typing import Any

from app.db import get_conn
from app.repositories.errors import RepositoryUnavailableError


def query_price_points(
    fish_id: int,
    market_id: int,
    start: str,
    end: str,
    granularity: str = "day",
    price_type: str = "pond",
    unit: str | None = "kg",
    trusted_only: bool = True,
) -> list[dict[str, Any]]:
    conn = get_conn()
    if conn is None:
        raise RepositoryUnavailableError("Database is not configured or unavailable")

    trust_filter = ""
    if trusted_only:
        trust_filter = " AND m.source_code = 'MZYY_WECHAT'"

    unit_filter = ""
    params: list[Any] = [fish_id, market_id, start, end, price_type]
    if unit:
        unit_filter = " AND p.unit = %s"
        params.append(unit)

    if granularity == "day":
        bucket_sql = "DATE(p.ts)"
    elif granularity == "week":
        bucket_sql = "DATE(DATE_SUB(p.ts, INTERVAL WEEKDAY(p.ts) DAY))"
    else:
        bucket_sql = "DATE_FORMAT(p.ts, '%Y-%m-01')"

    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    {bucket_sql} AS d,
                    AVG(p.price) AS price,
                    MIN(p.currency) AS currency,
                    MIN(p.unit) AS unit,
                    COUNT(*) AS sample_count,
                    MIN(p.source_url) AS source_url,
                    MIN(m.source_code) AS market_source_code
                FROM prices p
                JOIN markets m ON m.id = p.market_id
                WHERE p.fish_id = %s
                  AND p.market_id = %s
                  AND DATE(p.ts) BETWEEN %s AND %s
                  AND p.price_type = %s
                  {unit_filter}
                  {trust_filter}
                GROUP BY d
                ORDER BY d
                """,
                params,
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return [
        {
            "ts": f"{row[0]}T00:00:00+08:00",
            "price": float(row[1]),
            "currency": row[2],
            "unit": row[3],
            "sample_count": int(row[4]),
            "source_url": row[5],
            "data_trust": "trusted_candidate"
            if row[6] == "MZYY_WECHAT"
            else "unverified",
        }
        for row in rows
    ]

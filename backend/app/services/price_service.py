from typing import Any
from datetime import datetime

from app.lunar_utils import get_lunar_festivals, get_solar_terms, solar_to_lunar
from app.repositories import price_repository
from app.repositories.errors import RepositoryUnavailableError
from app.services import catalog_service
from app.services.catalog_service import DatabaseUnavailableError


def query_prices(
    fish_id: int,
    market_id: int,
    start: str,
    end: str,
    granularity: str = "day",
    price_type: str = "pond",
    lunar_mode: bool = False,
    include_unverified: bool = False,
) -> dict[str, Any]:
    fish = catalog_service.get_fish(fish_id)
    market = catalog_service.get_market(market_id)
    if fish is None or market is None:
        return {"fish": fish, "market": market, "points": []}

    try:
        points = price_repository.query_price_points(
            fish_id=fish_id,
            market_id=market_id,
            start=start,
            end=end,
            granularity=granularity,
            price_type=price_type,
            trusted_only=not include_unverified,
        )
    except RepositoryUnavailableError as exc:
        raise DatabaseUnavailableError("Database is not configured or unavailable") from exc

    if lunar_mode:
        points = add_lunar_info(points)

    return {
        "fish": fish,
        "market": market,
        "points": points,
        "meta": {
            "granularity": granularity,
            "price_type": price_type,
            "include_unverified": include_unverified,
            "query_mode": "database_only",
        },
    }


def add_lunar_info(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for point in points:
        ts = point.get("ts", "")
        solar_date = datetime.fromisoformat(ts.replace("Z", "+00:00")).date()
        lunar_info = solar_to_lunar(solar_date)
        result.append(
            {
                **point,
                "solar_date": solar_date.isoformat(),
                "lunar_year": lunar_info["lunar_year"],
                "lunar_month": lunar_info["lunar_month"],
                "lunar_day": lunar_info["lunar_day"],
                "lunar_date_str": lunar_info["lunar_date_str"],
                "lunar_month_str": lunar_info["lunar_month_str"],
                "lunar_day_str": lunar_info["lunar_day_str"],
                "is_leap_month": lunar_info["is_leap"],
                "festivals": get_lunar_festivals(
                    lunar_info["lunar_month"],
                    lunar_info["lunar_day"],
                ),
                "solar_terms": get_solar_terms(solar_date),
            }
        )
    return result

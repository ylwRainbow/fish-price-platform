from typing import Any

from app.repositories import catalog_repository
from app.repositories.errors import RepositoryUnavailableError


class DatabaseUnavailableError(RuntimeError):
    pass


def list_fishes(q: str | None = None) -> list[dict[str, Any]]:
    try:
        return catalog_repository.list_fishes(q)
    except RepositoryUnavailableError as exc:
        raise DatabaseUnavailableError("Database is not configured or unavailable") from exc


def list_markets(region_code: str | None = None) -> list[dict[str, Any]]:
    try:
        return catalog_repository.list_markets(region_code)
    except RepositoryUnavailableError as exc:
        raise DatabaseUnavailableError("Database is not configured or unavailable") from exc


def get_fish(fish_id: int) -> dict[str, Any] | None:
    try:
        return catalog_repository.get_fish(fish_id)
    except RepositoryUnavailableError as exc:
        raise DatabaseUnavailableError("Database is not configured or unavailable") from exc


def get_market(market_id: int) -> dict[str, Any] | None:
    try:
        return catalog_repository.get_market(market_id)
    except RepositoryUnavailableError as exc:
        raise DatabaseUnavailableError("Database is not configured or unavailable") from exc

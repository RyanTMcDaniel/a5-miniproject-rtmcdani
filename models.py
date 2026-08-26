from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    sku: str
    name: str
    rarity: str
    qty: int
    base_price: float
    tags: list[str]

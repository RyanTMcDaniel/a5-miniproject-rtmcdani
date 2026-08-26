from __future__ import annotations

from dataclasses import dataclass


class Item:
    """TODO: Replace this stub with the required frozen dataclass.

    Required fields, in order:
      sku: str
      name: str
      rarity: str
      qty: int
      base_price: float
      tags: list[str]

    `frozen=True` prevents attribute reassignment. It does not make the nested
    tags list deeply immutable.
    """

    pass

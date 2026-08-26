from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any


class InventorySource(ABC):
    """Abstract source of a guild inventory tree."""

    @abstractmethod
    def root(self) -> Any:
        """Return the root of the world tree."""
        raise NotImplementedError

    @abstractmethod
    def version(self) -> int | str:
        """Return the source version; a missing JSON version defaults to 1."""
        raise NotImplementedError


class JSONInventorySource(InventorySource):
    """Load an inventory from a JSON file.

    You may assume that grading files follow the documented inventory schema.
    Full schema validation is not required.
    """

    def __init__(self, path: str):
        self.path = path
        with open(self.path, "r", encoding="utf-8") as f:
            self._root = json.load(f)
        self._version = self._root.get("version", 1)

    def root(self) -> Any:
        return self._root

    def version(self) -> int | str:
        return self._version

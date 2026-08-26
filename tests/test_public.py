from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import FrozenInstanceError

from abc_sources import InventorySource, JSONInventorySource
from engine import QueryEngine
from errors import QueryValidationError
from models import Item
import cli as guild_cli


SAMPLE = os.path.join(os.path.dirname(__file__), "..", "data", "sample_small.json")


class PublicAssignmentTests(unittest.TestCase):
    def engine(self) -> QueryEngine:
        return QueryEngine(JSONInventorySource(SAMPLE))

    def test_item_fields_equality_and_frozen_assignment(self):
        first = Item("A", "Arrow", "common", 2, 1.5, ["ammo"])
        second = Item("A", "Arrow", "common", 2, 1.5, ["ammo"])
        self.assertEqual(first, second)
        with self.assertRaises(FrozenInstanceError):
            first.qty = 10  # type: ignore[misc]

    def test_inventory_source_is_abstract(self):
        with self.assertRaises(TypeError):
            InventorySource()  # type: ignore[abstract]

    def test_json_source_loads_and_reports_version(self):
        source = JSONInventorySource(SAMPLE)
        self.assertEqual(source.root()["world"], "Azeron")
        self.assertEqual(source.version(), 1)

    def test_walk_preserves_sample_order(self):
        skus = [item.sku for item in self.engine().walk_items()]
        self.assertEqual(skus, ["7F-ICE-BOW", "HP-POT-SM", "SR-SWD-LG", "MP-POT-MD"])

    def test_filter_and_map(self):
        engine = self.engine()
        epic_names = [item.name for item in engine.filter_items(lambda item: item.rarity == "epic")]
        self.assertEqual(epic_names, ["Ice Bow"])
        self.assertIn("Ice Bow", list(engine.map_items(lambda item: item.name)))

    def test_map_is_lazy(self):
        calls: list[str] = []
        mapped = self.engine().map_items(lambda item: calls.append(item.sku) or item.name)
        self.assertEqual(calls, [])
        next(mapped)
        self.assertEqual(calls, ["7F-ICE-BOW"])

    def test_reduce_uses_initial_value(self):
        total = self.engine().reduce_items(lambda acc, item: acc + item.qty, 10)
        self.assertEqual(total, 20)

    def test_binary_search_hit_and_miss(self):
        engine = self.engine()
        self.assertEqual(engine.find_item_by_sku("MP-POT-MD").name, "Medium Mana Potion")
        self.assertIsNone(engine.find_item_by_sku("NOT-REAL"))

    def test_non_bool_predicate_raises(self):
        with self.assertRaises(QueryValidationError):
            list(self.engine().filter_items(lambda _item: "yes"))

    def test_logging_occurs_after_exhaustion(self):
        output = io.StringIO()
        with redirect_stdout(output):
            iterator = self.engine().walk_items()
            self.assertEqual(output.getvalue(), "")
            list(iterator)
        self.assertEqual(output.getvalue().strip(), "[LOG] walk_items returned 4 items")

    def test_cli_find_missing_contract(self):
        args = guild_cli.build_parser().parse_args([SAMPLE, "find", "--sku", "NOT-REAL"])
        output = io.StringIO()
        with redirect_stdout(output):
            result = args.func(args)
        self.assertEqual(result, 1)
        self.assertEqual(output.getvalue().splitlines()[-1], "Not found")

    def test_cli_value_has_two_decimal_places_on_final_line(self):
        args = guild_cli.build_parser().parse_args([SAMPLE, "value", "--rarity", "rare"])
        output = io.StringIO()
        with redirect_stdout(output):
            result = args.func(args)
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue().splitlines()[-1], "250.00")


if __name__ == "__main__":
    unittest.main()

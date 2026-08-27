import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from abc_sources import InventorySource, JSONInventorySource
from cli import main
from engine import QueryEngine
from errors import QueryValidationError
from models import Item

SAMPLE = {
    "world": "Azeron",
    "regions": [
        {
            "name": "Frostvale",
            "dungeons": [
                {
                    "name": "Grimhold",
                    "rooms": [
                        {
                            "name": "Antechamber",
                            "chests": [
                                {
                                    "name": "Iron Chest #1",
                                    "items": [
                                        {
                                            "sku": "7F-ICE-BOW",
                                            "name": "Ice Bow",
                                            "rarity": "epic",
                                            "qty": 1,
                                            "base_price": 420.0,
                                            "tags": ["bow", "ice"],
                                        },
                                        {
                                            "sku": "HP-POT-SM",
                                            "name": "Small Potion",
                                            "rarity": "common",
                                            "qty": 10,
                                            "base_price": 5.0,
                                            "tags": ["potion"],
                                        },
                                    ],
                                },
                                {
                                    "name": "Iron Chest #2",
                                    "items": [
                                        {
                                            "sku": "AA-DAGGER",
                                            "name": "Dagger",
                                            "rarity": "rare",
                                            "qty": 2,
                                            "base_price": 50.0,
                                            "tags": [],
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        },
    ],
    "version": 1,
}

EXPECTED_ORDER = ["7F-ICE-BOW", "HP-POT-SM", "AA-DAGGER"]


class DictSource(InventorySource):
    """In-memory source, proving the ABC allows non-JSON backends."""

    def __init__(self, data, version=1):
        self._root = data
        self._version = version

    def root(self):
        return self._root

    def version(self):
        return self._version


class TestModels(unittest.TestCase):
    def test_frozen_blocks_reassignment(self):
        item = Item("A", "n", "rare", 1, 2.0, [])
        with self.assertRaises(Exception):
            item.sku = "B"

    def test_tags_not_deeply_immutable(self):
        item = Item("A", "n", "rare", 1, 2.0, ["x"])
        item.tags.append("y")
        self.assertEqual(item.tags, ["x", "y"])


class TestSource(unittest.TestCase):
    def test_json_round_trip(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(SAMPLE, fh)
            path = fh.name
        self.addCleanup(os.unlink, path)
        src = JSONInventorySource(path)
        self.assertEqual(src.version(), 1)
        self.assertEqual(src.root()["world"], "Azeron")

    def test_missing_version_defaults_to_one(self):
        data = {k: v for k, v in SAMPLE.items() if k != "version"}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(data, fh)
            path = fh.name
        self.addCleanup(os.unlink, path)
        self.assertEqual(JSONInventorySource(path).version(), 1)

    def test_abstract_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            InventorySource()


class TestTraversal(unittest.TestCase):
    def setUp(self):
        self.engine = QueryEngine(DictSource(SAMPLE))

    def test_json_order_preserved(self):
        skus = [i.sku for i in self.engine.walk_items()]
        self.assertEqual(skus, EXPECTED_ORDER)

    def test_traversal_is_lazy(self):
        gen = self.engine._walk_node(SAMPLE)
        self.assertEqual(next(gen).sku, EXPECTED_ORDER[0])

    def test_empty_tree_yields_nothing(self):
        engine = QueryEngine(DictSource({"world": "X", "regions": []}))
        self.assertEqual(list(engine._walk_node({"world": "X", "regions": []})), [])


class TestQueries(unittest.TestCase):
    def setUp(self):
        self.engine = QueryEngine(DictSource(SAMPLE))

    def test_filter_items(self):
        got = list(self.engine.filter_items(lambda i: i.rarity == "epic"))
        self.assertEqual([i.sku for i in got], ["7F-ICE-BOW"])

    def test_map_items(self):
        self.assertEqual(list(self.engine.map_items(lambda i: i.sku)), EXPECTED_ORDER)

    def test_reduce_total_value(self):
        total = self.engine.reduce_items(lambda a, i: a + i.qty * i.base_price, 0.0)
        self.assertAlmostEqual(total, 570.0)

    def test_reduce_empty_returns_initial(self):
        engine = QueryEngine(DictSource({"regions": []}))
        self.assertEqual(engine.reduce_items(lambda a, i: a + 1, 99), 99)


class TestBinarySearch(unittest.TestCase):
    def setUp(self):
        self.engine = QueryEngine(DictSource(SAMPLE))

    def test_finds_each_sku(self):
        for sku in EXPECTED_ORDER:
            self.assertEqual(self.engine.find_item_by_sku(sku).sku, sku)

    def test_missing_returns_none(self):
        self.assertIsNone(self.engine.find_item_by_sku("NOPE"))

    def test_case_sensitive(self):
        self.assertIsNone(self.engine.find_item_by_sku("7f-ice-bow"))


class TestValidatePredicate(unittest.TestCase):
    def setUp(self):
        self.engine = QueryEngine(DictSource(SAMPLE))

    def test_non_callable_raises(self):
        with self.assertRaises(QueryValidationError):
            list(self.engine.filter_items(42))

    def test_validation_is_lazy(self):
        self.engine.filter_items(42)

    def test_non_bool_raises(self):
        with self.assertRaises(QueryValidationError):
            list(self.engine.filter_items(lambda i: 1))

    def test_predicate_exception_preserves_cause(self):
        def boom(item):
            raise ZeroDivisionError("boom")

        with self.assertRaises(QueryValidationError) as cm:
            list(self.engine.filter_items(boom))
        self.assertIsInstance(cm.exception.__cause__, ZeroDivisionError)


class TestLoggedQuery(unittest.TestCase):
    def setUp(self):
        self.engine = QueryEngine(DictSource(SAMPLE))

    def test_call_alone_prints_nothing(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.engine.walk_items()
        self.assertEqual(buf.getvalue(), "")

    def test_logs_after_exhaustion(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            list(self.engine.walk_items())
        self.assertIn("[LOG] walk_items returned 3 items", buf.getvalue())

    def test_partial_iteration_does_not_log(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            gen = self.engine.walk_items()
            next(gen)
        self.assertEqual(buf.getvalue(), "")


class TestCLI(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(SAMPLE, fh)
            self.path = fh.name
        self.addCleanup(os.unlink, self.path)

    def _run(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main([self.path, *argv])
        return code, buf.getvalue()

    def test_find_hit_returns_zero(self):
        code, out = self._run("find", "--sku", "7F-ICE-BOW")
        self.assertEqual(code, 0)
        self.assertIn("7F-ICE-BOW", out)

    def test_find_miss_returns_one(self):
        code, out = self._run("find", "--sku", "NOPE")
        self.assertEqual(code, 1)
        self.assertEqual(out.strip(), "Not found")

    def test_value_two_decimals(self):
        code, out = self._run("value")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip().splitlines()[-1], "570.00")

    def test_list_rarity_filter(self):
        code, out = self._run("list", "--rarity", "epic")
        self.assertEqual(code, 0)
        self.assertIn("7F-ICE-BOW", out)
        self.assertNotIn("HP-POT-SM", out)


if __name__ == "__main__":
    unittest.main()

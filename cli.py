from __future__ import annotations

import argparse

from abc_sources import JSONInventorySource
from engine import QueryEngine
from models import Item


def _fmt_item(item: Item) -> str:
    return (
        f"{item.sku:12} | {item.rarity:7} | {item.qty:3} | "
        f"{item.base_price:8.2f} | {item.name}"
    )


def cmd_list(args: argparse.Namespace) -> int:
    # TODO: Use QueryEngine methods; print matching items with _fmt_item.
    raise NotImplementedError


def cmd_find(args: argparse.Namespace) -> int:
    # TODO: Return 0 for a hit. For a miss, print exactly "Not found" and return 1.
    raise NotImplementedError


def cmd_value(args: argparse.Namespace) -> int:
    # TODO: Print the total with exactly two decimal places and return 0.
    raise NotImplementedError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="guild", description="Guild Inventory CLI")
    parser.add_argument("data", help="Path to an inventory JSON file")
    sub = parser.add_subparsers(dest="cmd", required=True)

    list_parser = sub.add_parser("list", help="List inventory items")
    list_parser.add_argument("--rarity", help="Case-sensitive rarity filter")
    list_parser.set_defaults(func=cmd_list)

    find_parser = sub.add_parser("find", help="Find one item by SKU")
    find_parser.add_argument("--sku", required=True)
    find_parser.set_defaults(func=cmd_find)

    value_parser = sub.add_parser("value", help="Compute total inventory value")
    value_parser.add_argument("--rarity", help="Case-sensitive rarity filter")
    value_parser.set_defaults(func=cmd_value)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

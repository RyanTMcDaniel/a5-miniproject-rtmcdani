# Design and Complexity

Answer in approximately one page.

## Traversal

\_walk_node is an iterative DFS implemented through 5 nested loops. It is one loop per level of the schema : regions -> dungeons -> rooms -> chests -> items. Each level uses .get(key, []) so a missing room/chest/dungeon/region contributes nothing rather than raising error. JSON order is preserved since Python decodes arrays into ordered lists and objects into insertion ordered dicts. The traversal iterates each list front to back without reordering. The method is lazy because it contains yield so it is a generator function. Calling it does not execute the body and each next() resumes it, produces one item, and pauses the loop. At most one item exists at a time. A full run of items would take O(n+m) time where n is number of items and m is interior nodes. Each node is visited once and each item is built in constant time. Auxiliary space is O(1), 5 iterators and a single item regardless of tree size.

## Binary Search

The binary search calls sorted() which pulls the items from the generator into a list making the space O(n) and running in O(nlogn) time. The 'key=lambda item: item.sku' is necessary since the Item dataclass has no defined ordering so trying to sort directly would raise error, it then searches based on this key. One run of the binary search then has O(logn) time since each miss cuts the search zone in half. The sorted view is required since each loop is checking the midpoint and discarding either the upper or lower half based on the target's value, if the values weren't sorted then there would be no ordering about the midpoint so values would be incorrectly discarded.

## Decorators

The decorators keep logging and validation out of the query logic entirely. walk_items and filter_items don't have any counting or type checking code and either function can be attached to a new method with a single line. validate_predicate improves safety by collapsing 3 failures into one QueryValidationError, an uncallable predicate, one that returns non-bool, and one that raises during evaluation. Using raise from e preserves the original exception as the cause so the real issue isn't hidden. Both wrappers are generator functions so nothing happens when each method is called, validation occurs on the every next() and logging only prints after each generator is exhausted.

# Process Log

Include at least three concise entries from different development moments.
Repository history and this log are evidence of process, not proof of authorship.

## Entry 1 — 8/26

walk_items falsely returning empty list.
Evidence : Printing inside each loop showed the regions loop entering once and the dungeons loop never running. The inner loops were
calling node.get("dungeons") instead of region.get("dungeons"), so .get() returned default [].
Change : Fixed variable so loop would enter correctly.
Verified with example input which printed correct SKUs.

## Entry 2 — 8/26

TypeError on e.filter_items() while map_items worked
Evidence : map_items had no decorator and worked but filter_items had a decorator and didn't. Decorator itself was returning nothing.
Change : Added return wrapper to logged_query and validate_predicate
Verified : print(QueryEngine.filter_items) showed a function instead of None and filter_items(lambda i: i.rarity=='epic') returned the ice bow

## Entry 3 — 8/26

Reading JSON once instead of on every call
Evidence : My first version opened and parsed the file inside both root() and version(). So every engine method read the entire tree
from disk unnecesarily. The assignment description also said the version should be cached.
Change : Parse once in **init** and store self.\_root and self.\_version
Verified : Bad path raises FileNotFoundError at construction and correct path returns 1

# ICS 33 Assignment 5 — Guild Inventory Explorer

Summer 2026 release 1.0.

The [Google Doc assignment description](https://docs.google.com/document/d/1BXjwUY3BFdPGz5JfrwxufRUWxt6Bxszt1TQt3VEXlMM/edit)
is the authoritative specification. This starter deliberately contains incomplete
implementations, but every Python file must import and compile successfully before
you begin.

## Required root-level files

Do not move the Python modules into a package directory. Gradescope imports these
modules directly from the repository root:

- `models.py`
- `errors.py`
- `abc_sources.py`
- `decorators.py`
- `engine.py`
- `cli.py`
- `guild.py`

Also submit `design_and_complexity.md`, `process_log.md`, and your tests.

## Run the public tests

```text
python -m unittest discover -s tests -p 'test_public.py'
```

The public tests are representative, not exhaustive. Gradescope uses additional
tests for documented boundary cases and generalization.

## Run the CLI

```text
python guild.py data/sample_small.json list --rarity epic
python guild.py data/sample_small.json find --sku 7F-ICE-BOW
python guild.py data/sample_small.json value --rarity rare
```

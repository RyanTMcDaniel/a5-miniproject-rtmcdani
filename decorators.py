from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from functools import wraps
from typing import Any, TypeVar

from errors import QueryValidationError

T = TypeVar("T")


def logged_query(fn: Callable[..., Iterable[T]]) -> Callable[..., Iterator[T]]:
    """Lazily yield results and log the count after normal exhaustion.

    Required output:
      [LOG] function_name returned N items

    Calling the decorated method alone must not run the query or print.
    """

    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Iterator[T]:
        # TODO: Return a lazy iterator that counts as it yields.
        raise NotImplementedError

    return wrapper


def validate_predicate(fn: Callable[..., Iterable[T]]) -> Callable[..., Iterator[T]]:
    """Validate a filter predicate lazily.

    Raise QueryValidationError when the predicate is not callable, returns a
    non-bool result, or raises an exception. Preserve a predicate exception with
    `raise QueryValidationError(...) from original_exception`.
    """

    @wraps(fn)
    def wrapper(
        self: Any,
        pred: Callable[[Any], bool],
        *args: Any,
        **kwargs: Any,
    ) -> Iterator[T]:
        # TODO: Return a lazy iterator that uses a guarded predicate.
        raise NotImplementedError

    return wrapper

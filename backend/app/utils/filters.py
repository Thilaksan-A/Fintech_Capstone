from typing import Callable, Iterable, TypeVar

T = TypeVar('T')


def compose_filters(
    *filters: Callable[[Iterable[T]], Iterable[T]]
) -> Callable[[Iterable[T]], Iterable[T]]:
    """
    Compose multiple filter functions for any type.
    Each filter should accept and return an iterable of T.
    """

    def composed_filter(items: Iterable[T]) -> Iterable[T]:
        current = items
        for filter_func in filters:
            current = filter_func(current)
        return current

    return composed_filter

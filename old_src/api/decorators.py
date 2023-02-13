from copy import deepcopy
from functools import wraps
from random import choice
from typing import Any, Callable, List, Tuple, TypeVar

from old_src.model.individual import Individual

T = TypeVar("T")
Decorator = Callable[[Callable[..., T]], Callable[..., T]]


def staticLimit(key: Callable[..., Any], max_value: int) -> Decorator[Tuple[Individual, ...]]:
    def decorator(func: Callable[..., Tuple[Individual, ...]]):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            individuals = list(filter(lambda item: isinstance(item, Individual), args))
            keep_inds = [deepcopy(ind) for ind in individuals]
            new_inds: List[Individual] = list(func(*args, **kwargs))
            for i, ind in enumerate(new_inds):
                if key(ind) > max_value:
                    new_inds[i] = choice(keep_inds)
            return tuple(new_inds)
        return wrapper
    return decorator

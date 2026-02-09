from functools import wraps
from typing import Any, Callable, Dict

type PredicateFn[T] = Callable[[T], bool]
type RuleDef = Callable[..., bool]
type PredicateFactory[T] = Callable[..., Predicate[T]]

RULES: Dict[str, PredicateFactory[Any]] = {}

class Predicate[T]:
    """
    """
    def __init__(self, fn: PredicateFn[T]):
        self.fn = fn

    def __call__(self, obj: T) -> bool:
        return self.fn(obj)

    def __and__(self, other: "Predicate"[T]) -> "Predicate"[T]:
        return Predicate(lambda x: self(x) and other(x))

    def __or__(self, other: "Predicate"[T]) -> "Predicate"[T]:
        return Predicate(lambda x: self(x) or other(x))

    def __invert__(self) -> "Predicate"[T]:
        return Predicate(lambda x: not self(x))

def predicate[T](fn: PredicateFn[T]) -> Predicate[T]:
    @wraps(fn)
    def wrapper(obj: T) -> bool:
        return fn(obj)

    return Predicate(wrapper)


def rule[T](fn: RuleDef) -> PredicateFactory[Any]:
    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Predicate[T]:
        return Predicate(lambda obj: fn(*args, obj, **kwargs))

    RULES[fn.__name__] = wrapper
    return wrapper
import threading
from typing import TypeVar, Type, Dict, cast

T = TypeVar("T", bound="Singleton")

class Singleton:
    _instances: Dict[Type["Singleton"], "Singleton"] = {}
    _lock = threading.Lock()

    def __new__(cls: Type[T], *args, **kwargs) -> T:
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = cast(T, object.__new__(cls))
                    cls._instances[cls] = instance
                    instance._init_once(*args, **kwargs)
        return cast(T, cls._instances[cls])
    
    def _init_once(self, *args, **kwargs) -> None:
        pass
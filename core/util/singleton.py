import threading
from typing import Any, TypeVar, Type, Dict, cast

T = TypeVar("T", bound="Singleton")

class Singleton:
    """
    Thread-safe Singleton base classusing double-checked locking.
    Subclasses should implement '_init_once' instead of '__init__'.
    """
    # Map of class to Single Instance
    _instances: Dict[Type["Singleton"], Any] = {}
    _lock = threading.Lock()

    # Typing cls as Type[T] tells the IDE that calling MySubClass() returns MySubClass
    def __new__(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        # Check if instance already exists
        if cls not in cls._instances:
            # Block concurrent instantion
            with cls._lock:
                # Guard against race condition
                if cls not in cls._instances:
                    # Cast class to 'type' to satisfy the super().__new__ signature
                    instance = super().__new__(cast(type, cls))
                    # Initialize once before adding to map to prevent partial
                    if hasattr(instance, "_init_once"):
                        instance._init_once(*args, **kwargs)
                    cls._instances[cls] = instance

        return cast(T, cls._instances[cls])

    def _init_once(self, *args: Any, **kwargs: Any) -> None:
        """
        One time initialization logic.
        Replaces __init__ to prevent re-running on every access.
        """
        pass

import threading
from typing import Dict, Generic, TypeVar, Optional, Mapping

K = TypeVar("K")
V = TypeVar("V")


class CopyOnWriteDict(Generic[K, V]):
    def __init__(self, initial: Optional[Dict[K, V]] = None):
        self._data: Dict[K, V] = dict(initial) if initial is not None else {}
        self._lock = threading.Lock()

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __setitem__(self, key: K, value: V) -> None:
        self.set(key, value)

    # ---- READ API -------------------------------------------------------

    def get(self, key: K, default=None) -> V:
        return self._data.get(key, default)

    def snapshot(self) -> Dict[K, V]:
        return dict(self._data)

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def __contains__(self, key: K) -> bool:
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    # ---- WRITE API ------------------------------------------------------

    def set(self, key: K, value: V) -> None:
        with self._lock:
            new_dict = self._data.copy()
            new_dict[key] = value
            self._data = new_dict

    def remove(self, key: K) -> None:
        with self._lock:
            if key not in self._data:
                return
            new_dict = self._data.copy()
            del new_dict[key]
            self._data = new_dict

    def clear(self) -> None:
        with self._lock:
            self._data = {}

    def update_all(self, other: Mapping[K, V]) -> None:
        """
        Copy-on-write bulk insertion.
        Equivalent to dict.update(), but thread-safe and atomic for readers.
        """
        if not other:
            return

        with self._lock:
            new_dict = self._data.copy()
            new_dict.update(other)
            self._data = new_dict

    # Alias for convenien

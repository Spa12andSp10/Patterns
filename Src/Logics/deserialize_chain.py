class deserialize_chain:
    """Цепочка обязанностей: dict -> значение (обратная к convert_chain)."""

    def __init__(self):
        self._handlers: list = []

    def register(self, predicate, handler) -> "deserialize_chain":
        self._handlers.append((predicate, handler))
        return self

    def clear(self) -> None:
        self._handlers.clear()

    def deserialize(self, source, resolver, visited: set = None):
        if visited is None:
            visited = set()
        for predicate, handler in self._handlers:
            if predicate(source, resolver):
                return handler(source, self, resolver, visited)
        return source
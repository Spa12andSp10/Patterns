from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class deserializer(Protocol):
    """Контракт цепочки десериализации."""

    def deserialize(self, source: Any, resolver: Any,
                    visited: set[str] | None = None) -> Any:
        """Преобразует source в значение/модель/список."""
        ...

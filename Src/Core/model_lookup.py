from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class model_lookup(Protocol):
    """Контракт поиска модели по имени."""

    def get_by_name(self, model_cls: type, name: str) -> Any:
        """Возвращает модель указанного класса с именем name или None."""
        ...

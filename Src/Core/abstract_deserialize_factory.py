from abc import ABC, abstractmethod


class abstract_deserialize_factory(ABC):
    """Абстрактная фабрика десериализаторов"""

    @abstractmethod
    def create(self):
        """Создаёт и возвращает цепочку десериализации."""
        ...

    @abstractmethod
    def deserialize(self, source):
        """Точка входа: dict -> значение/модель/список."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Сбрасывает кэш резолвера."""
        ...
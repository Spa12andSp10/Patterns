from abc import ABC, abstractmethod

class abstract_convert_factory(ABC):
    """Абстрактная фабрика конвертеров доменных моделей."""

    @abstractmethod
    def create(self):
        """Создаёт и возвращает готовую к работе цепочку конвертации."""
        ...
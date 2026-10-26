from abc import ABC, abstractmethod

class abstract_json_factory(ABC):

    """
    Абстрактная фабрика конвертеров JSON.
    """
    @abstractmethod
    def create(self):
        """
        Создаёт и возвращает готовый к работе конвертер.
        """
        ...
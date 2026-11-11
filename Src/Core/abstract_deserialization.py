from abc import ABC, abstractmethod

class abstract_deserialization(ABC):

    """Абстрактный базовый класс для десериализатора"""

    @abstractmethod
    def deserialized(self, source: dict) -> bool:
        """Десериализатор"""
        ...

    @abstractmethod
    def load(self, file_name: str) -> bool:
        """Загрузка данных из файла"""
        ...
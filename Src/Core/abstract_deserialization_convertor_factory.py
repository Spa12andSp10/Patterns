from abc import ABC, abstractmethod

class abstract_deserialization_convertor_factory(ABC):

    """Абстрактный конвертор для десериализации данных"""

    @abstractmethod
    def convert(self, source: str):
        pass
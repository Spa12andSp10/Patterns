from abc import ABC, abstractmethod
from typing import ClassVar


class abstract_deserialization_convertor_factory(ABC):
    """Абстрактный конвертор десериализации (dict -> доменная модель)"""

    _registry: ClassVar[dict] = {}
    entity: ClassVar = None

    def __init_subclass__(cls, **kwargs):
        """Регистрирует наследника по его entity."""
        super().__init_subclass__(**kwargs)
        if getattr(cls, "entity", None) is not None:
            abstract_deserialization_convertor_factory._registry[cls.entity] = cls

    @classmethod
    @abstractmethod
    def create(cls, repository, *args, **kwargs):
        """Фабричный метод: создаёт экземпляр конвертера."""
        ...

    @abstractmethod
    def deserialize(self, source: dict):
        """Преобразует dict в доменную модель."""
        ...
from abc import ABC, abstractmethod

from Src.Core.validator import validator
from Src.Dtos.filter_dto import filter_dto


class abstract_prototype(ABC):
    """Абстрактный прототип, который хранит данные и умеет клонировать себя."""

    def __init__(self, data: list) -> None:
        """Инициализирует прототип.

        """
        super().__init__()
        validator.validate(data, list)
        self._data = list(data)

    @property
    def data(self) -> list:
        """Возвращает текущие данные прототипа."""
        return self._data

    @abstractmethod
    def clone(self, filters: filter_dto = None) -> "abstract_prototype":
        """Возвращает новый прототип с отфильтрованными данными.

        """
        ...

from enum import Enum


class field_kind(str, Enum):
    """Способ построения значения поля модели."""

    PRIMITIVE = "primitive"
    MODEL = "model"
    LIST = "list"
    DICT = "dict"

    @classmethod
    def is_valid(cls, value) -> bool:
        """Проверяет, что значение входит в перечень допустимых kind."""
        return value in {item.value for item in cls}

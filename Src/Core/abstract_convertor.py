import json
from abc import ABC, abstractmethod

from Src.Logics.json_convertor_factory import json_convertor_factory


class abstract_convertor(ABC):
    """Абстрактный конвертер объекта в JSON-совместимый словарь."""

    _json_convertor = json_convertor_factory().create()

    @abstractmethod
    def convert(self, source: object) -> dict:
        ...

    @staticmethod
    def _public(source: object) -> list:
        """Список публичных property-полей объекта (без служебных)."""
        result = []
        for name in dir(type(source)):
            if name.startswith("_"):
                continue
            attr = getattr(type(source), name, None)
            if isinstance(attr, property):
                result.append(name)
        return result

    @staticmethod
    def _to_json(value):
        """Приводит значение к JSON-сериализуемому виду.
        """
        return abstract_convertor._json_convertor.convert(value)

    @classmethod
    def to_json(cls, data: dict) -> str:
        """Сериализует результат convert() в JSON-строку."""
        return json.dumps(
            cls._to_json(data),
            ensure_ascii=False,
            indent=2,
        )
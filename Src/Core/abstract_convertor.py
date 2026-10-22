import json
from abc import ABC, abstractmethod
from datetime import date, datetime, time, timedelta


class abstract_convertor(ABC):
    """Абстрактный конвертер объекта в JSON-совместимый словарь."""

    @abstractmethod
    def convert(self, source: object) -> dict:
        """Возвращает словарь, пригодный для json.dumps."""
        pass

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
        """Приводит значение к JSON-сериализуемому виду."""
        if isinstance(value, dict):
            return {k: abstract_convertor._to_json(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [abstract_convertor._to_json(v) for v in value]
        if isinstance(value, (datetime, date, time)):
            return value.isoformat()
        if isinstance(value, timedelta):
            return value.total_seconds()
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)

    @classmethod
    def to_json(cls, data: dict) -> str:
        """Сериализует результат convert() в JSON-строку."""
        return json.dumps(
            cls._to_json(data),
            ensure_ascii=False,
            indent=2,
        )
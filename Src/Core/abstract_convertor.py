import json
from abc import ABC, abstractmethod

from Src.Core.json_convertor_factory import json_convertor_factory

# Явная регистрация стандартных обработчиков (идемпотентна).
json_convertor_factory.create_default()


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
        """Приводит значение к JSON-сериализуемому виду.

        Делегирует разбор типов фабрике json_convertor_factory.
        Новые типы регистрируются через register() без правки
        этого метода.
        """
        return json_convertor_factory.convert(value, abstract_convertor._to_json)

    @classmethod
    def to_json(cls, data: dict) -> str:
        """Сериализует результат convert() в JSON-строку."""
        return json.dumps(
            cls._to_json(data),
            ensure_ascii=False,
            indent=2,
        )
from datetime import date, datetime

from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_model import abstract_model
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Logics import convert_strategies as st


class convert_factory:
    """Фабрика: реестр стратегий разбора значения.

    Каждая стратегия — пара (predicate, handler). Первая подходящая
    выигрывает. Порядок регистрации = приоритет.

    handler(source, visited, factory) -> dict | list | scalar
    """

    def __init__(self):
        self._handlers: list = []
        self._basic = basic_convertor()
        self._date = datetime_convertor()
        self._reference = reference_convertor()

    @classmethod
    def create_default(cls) -> "convert_factory":
        """Создаёт фабрику с набором стандартных стратегий.

        Порядок регистрации = приоритет:
          1. примитивы (str/int/float, кроме bool);
          2. даты;
          3. ссылочные модели (abstract_model, с защитой от циклов);
          4. произвольные объекты с публичными property;
          5. списки/кортежи;
          6. словари;
        Fallback {"value": source} — внутри convert().
        """

        factory = cls()
        factory.register(st.is_simple, st.handle_simple)
        factory.register(st.is_date, st.handle_date)
        factory.register(st.is_reference, st.handle_reference)
        factory.register(
            st.is_object_with_properties,
            st.handle_object_with_properties,
        )
        factory.register(st.is_list, st.handle_list)
        factory.register(st.is_dict, st.handle_dict)
        return factory

    @property
    def basic(self) -> basic_convertor:
        return self._basic

    @property
    def date(self) -> datetime_convertor:
        return self._date

    @property
    def reference(self) -> reference_convertor:
        return self._reference

    def register(self, predicate, handler) -> "convert_factory":
        """Регистрирует стратегию. Возвращает self для цепочки."""
        self._handlers.append((predicate, handler))
        return self

    def clear(self) -> None:
        """Очищает реестр (для тестов)."""
        self._handlers.clear()

    @classmethod
    def to_json(cls, data: dict) -> str:
        return abstract_convertor.to_json(data)

    def convert(self, source: object, visited: set = None) -> dict:
        if visited is None:
            visited = set()
        for predicate, handler in self._handlers:
            if predicate(source):
                return handler(source, visited, self)
        return {"value": source}

    def _value_for_field(self, value, visited: set):
        """Приводит значение поля модели к «плоскому» виду.

        Внутри модели примитивы и даты остаются «сырыми» значениями
        (строка/число/ISO-строка), а вложенные модели, списки и словари
        разбираются рекурсивно.
        """
        if value is None:
            return None

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, (list, tuple)):
            return {
                str(index): self.convert(item, visited)
                for index, item in enumerate(value)
            }

        if isinstance(value, dict):
            return {
                key: self.convert(item, visited)
                for key, item in value.items()
            }

        if isinstance(value, abstract_model):
            return self.convert(value, visited)

        # Произвольный объект с публичными property (Composite/WithList).
        if abstract_convertor._public(value):
            return self.convert(value, visited)

        # Примитив (str/int/float/bool) — как есть.
        return value

    def collect_members(self, source: object, visited: set) -> dict:
        """Обходит публичные property объекта и разбирает каждое поле.

        Для примитивов и дат значение кладётся «как есть» (для дат —
        ISO-строка), для моделей/списков/словарей/объектов с property —
        рекурсивно разбирается. None-поля пропускаются.
        """
        result = {}

        for field_name in abstract_convertor._public(source):
            try:
                value = getattr(source, field_name)
            except Exception:
                continue

            if value is None:
                continue

            result[field_name] = self._value_for_field(value, visited)

        return result
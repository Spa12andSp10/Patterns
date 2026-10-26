from datetime import datetime, date
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_model import abstract_model

class walker:

    """Обходит доменную модель через публичные property."""

    def __init__(self, chain):
        self._chain = chain

    def convert(self, value, visited: set = None):
        """Разбирает значение через цепочку.

        Точка входа для внешних потребителей (settings_manager,
        storage_manager) и для рекурсии из стратегий.

        :param value: Исходное значение.
        :param visited: Множество unique_code посещённых моделей.
        :return: Разобранное значение.
        """
        if visited is None:
            visited = set()
        return self._chain.convert(value, self, visited)

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
    
            if abstract_convertor._public(value):
                return self.convert(value, visited)
    
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
            if value == "" and field_name == "item_type":
                continue
            result[field_name] = self._value_for_field(value, visited)
    
        return result
    
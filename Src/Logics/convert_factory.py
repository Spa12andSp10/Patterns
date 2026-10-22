from datetime import date, datetime

from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_model import abstract_model
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor


class convert_factory:
    """Фабрика конвертеров: разбирает любой объект на набор словарей."""

    def __init__(self):
        self.__basic = basic_convertor()
        self.__date = datetime_convertor()
        self.__reference = reference_convertor()

    @classmethod
    def to_json(cls, data: dict) -> str:
        return abstract_convertor.to_json(data)

    def __collect_members(self, source: object, visited: set) -> dict:
        """Обходит публичные property объекта и разбирает каждое поле.

        - простые типы   → значение как есть;
        - даты           → ISO-строка;
        - ссылки         → компактное описание (unique_code, type, name);
        - вложенные      → рекурсивный convert();
        - None           → пропускается.
        """
        result = {}

        for field_name in abstract_convertor._public(source):
            try:
                value = getattr(source, field_name)
            except Exception:
                continue

            if value is None:
                continue

            # Ссылочная модель (кроме самого себя) — компактное описание.
            if isinstance(value, abstract_model) and value is not source:
                desc = self.__reference.convert(value)
                result[field_name] = desc.get("value", desc)
                continue

            # Простое значение (str/int/float, без bool).
            simple_part = self.__basic.convert(value)
            if simple_part:
                result[field_name] = simple_part.get("value", simple_part)
                continue

            # Дата / datetime.
            datetime_part = self.__date.convert(value)
            if datetime_part:
                result[field_name] = datetime_part.get("value", datetime_part)
                continue

            # Всё остальное (вложенные объекты, списки, словари) — рекурсия.
            result[field_name] = self.convert(value, visited)

        return result

    def convert(self, source: object, visited: set = None) -> dict:
        if visited is None:
            visited = set()

        if isinstance(source, (str, int, float)) and not isinstance(source, bool):
            return self.__basic.convert(source)

        if isinstance(source, (datetime, date)):
            return self.__date.convert(source)

        if isinstance(source, abstract_model):
            code = getattr(source, "unique_code", None)

            if code is not None and code in visited:
                return {"value": self.__reference.convert(source)["value"]}

            if code is not None:
                visited.add(code)

            try:
                return self.__collect_members(source, visited)
            finally:
                if code is not None:
                    visited.discard(code)

        if isinstance(source, (list, tuple)):
            return {
                str(i): self.convert(item, visited)
                for i, item in enumerate(source)
            }

        if isinstance(source, dict):
            return {
                str(k): self.convert(v, visited)
                for k, v in source.items()
            }

        if abstract_convertor._public(source):
            return self.__collect_members(source, visited)

        return {"value": source}
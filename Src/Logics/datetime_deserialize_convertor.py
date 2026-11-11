from datetime import date, datetime
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import arguments_exeption


class datetime_deserialize_convertor(abstract_convertor):
    """Десериализация по типам с временем и датами"""

    def convert(self, source: object) -> object:
        if source is None:
            raise arguments_exeption("convert", "Объект не задан")
        
        if not isinstance(source, dict) or set(source.keys()) != {"value"}:
            raise arguments_exeption("convert", "Ожидался dict вида {'value': 'ISO'}")
        
        raw = source["value"]
        if not isinstance(raw, str):
            raise arguments_exeption("convert", "Ожидалась ISO-строка")
        
        try:
            if len(raw) == 10:
                return date.fromisoformat(raw)
            return datetime.fromisoformat(raw)
        except ValueError as e:
            raise arguments_exeption("convert", f"Некорректная дата")
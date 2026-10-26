from datetime import date, datetime, time, timedelta

from Src.Core.abstract_json_factory import abstract_json_factory
from Src.Logics.json_convertor import json_convertor


class json_convertor_factory(abstract_json_factory):
    """Конкретная фабрика: стандартный набор стратегий для JSON.

    Создаёт НОВЫЙ экземпляр json_convertor при каждом вызове create()
    и регистрирует в нём стандартные стратегии.
    """

    def create(self) -> json_convertor:
        """Создаёт конвертер со стандартными стратегиями."""
        return (
            json_convertor()
            .register(self._is_dict, self._convert_dict)
            .register(self._is_sequence, self._convert_sequence)
            .register(self._is_datetime, self._convert_datetime)
            .register(self._is_timedelta, self._convert_timedelta)
            .register(self._is_primitive, self._convert_primitive)
        )


    @staticmethod
    def _is_dict(value) -> bool:
        return isinstance(value, dict)

    @staticmethod
    def _is_sequence(value) -> bool:
        return isinstance(value, (list, tuple))

    @staticmethod
    def _is_datetime(value) -> bool:
        return isinstance(value, (datetime, date, time))

    @staticmethod
    def _is_timedelta(value) -> bool:
        return isinstance(value, timedelta)

    @staticmethod
    def _is_primitive(value) -> bool:
        return isinstance(value, (str, int, float, bool)) or value is None


    @staticmethod
    def _convert_dict(value, converter: json_convertor):
        return {k: converter.convert(v) for k, v in value.items()}

    @staticmethod
    def _convert_sequence(value, converter: json_convertor):
        return [converter.convert(v) for v in value]

    @staticmethod
    def _convert_datetime(value, converter: json_convertor):
        return value.isoformat()

    @staticmethod
    def _convert_timedelta(value, converter: json_convertor):
        return value.total_seconds()

    @staticmethod
    def _convert_primitive(value, converter: json_convertor):
        return value
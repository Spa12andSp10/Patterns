from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import arguments_exeption
from datetime import date, datetime

class datetime_convertor(abstract_convertor):

    DATETIME_TYPES = (datetime, date)

    @classmethod
    def _is_date(cls, value: object) -> bool:

        return isinstance(value, cls.DATETIME_TYPES)

    def convert(self, source: object) -> dict:

        if source is None:
            raise arguments_exeption("convert", "Объект не задан")

        if self._is_date(source):
            return {"value": self._to_json(source)}

        result = {}
        for i in self._public(source):

            try:
                value = getattr(source, i)
            except Exception:
                continue

            if self._is_date(value):
                result[i] = self._to_json(value)

        return result        
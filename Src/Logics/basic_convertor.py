from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import arguments_exeption

class basic_convertor(abstract_convertor):

    SIMPLE_TYPES = (str, int, float)

    @classmethod
    def _is_simple(cls, value: object) -> bool:

        if isinstance(value, bool):
            return False
        return isinstance(value, cls.SIMPLE_TYPES)

    def convert(self, source: object) -> dict:

        if source is None:
            raise arguments_exeption("convert", "Объект не задан")

        if self._is_simple(source):
            return {"value": source}

        result = {}
        for i in self._public(source):
            try:
                value = getattr(source, i)
            except Exception:
                continue

            if self._is_simple(value):
                result[i] = value

        return result
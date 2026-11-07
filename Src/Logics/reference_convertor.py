from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import arguments_exeption
from Src.Core.abstract_model import abstract_model

class reference_convertor(abstract_convertor):

    @staticmethod
    def _is_reference(value: object) -> bool:

        return isinstance(value, abstract_model)

    @staticmethod
    def _desc(value: object) -> dict:

        return {
            "unique_code": value.unique_code,
            "type": value.item_type,
            "name": getattr(value, "name", ""),
        }

    def convert(self, source: object) -> dict:

        if source is None:
            raise arguments_exeption("convert", "Объект не задан")

        if self._is_reference(source):
            return {"value": self._desc(source)}

        result = {}
        for i in self._public(source):

            try:
                value = getattr(source, i)
            except Exception:
                continue

            if self._is_reference(value):
                result[i] = self._desc(value)

        return result     
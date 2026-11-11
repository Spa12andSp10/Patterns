from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import arguments_exeption


class basic_deserialize_convertor(abstract_convertor):
    """Десериализатор для простым типам"""

    SIMPLE_TYPES = (str, int, float)

    @classmethod
    def _is_simple(cls, value) -> bool:
        if isinstance(value, bool):
            return False
        return isinstance(value, cls.SIMPLE_TYPES)

    def convert(self, source: object) -> object:
        if source is None:
            raise arguments_exeption("convert", "Объект не задан")
        
        if not isinstance(source, dict) or set(source.keys()) != {"value"}:
            raise arguments_exeption("convert", "Ожидался dict вида {'value': ...}")
        
        value = source["value"]
        if not self._is_simple(value):
            raise arguments_exeption("convert",f"Ожидался примитив (str/int/float, не bool), "f"получено {type(value).__name__}",)
        return value
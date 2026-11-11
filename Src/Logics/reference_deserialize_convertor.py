from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import arguments_exeption
from Src.Logics.model_resolver import model_resolver


class reference_deserialize_convertor(abstract_convertor):
    """Обратный к reference_convertor / handle_reference."""

    _SHORT_REQUIRED = {"unique_code", "type"}
    _SHORT_ALLOWED = {"unique_code", "type", "name"}

    def __init__(self, resolver: model_resolver):
        self._resolver = resolver
        self._chain = None

    def bind(self, chain) -> "reference_deserialize_convertor":
        self._chain = chain
        return self

    @classmethod
    def _is_short_reference(cls, source: dict) -> bool:
        if not isinstance(source, dict):
            return False
        if not cls._SHORT_REQUIRED <= source.keys():
            return False
        return set(source.keys()) <= cls._SHORT_ALLOWED

    def convert(self, source: object, visited: set = None) -> object:
        if visited is None:
            visited = set()
        if source is None:
            raise arguments_exeption("convert", "Объект не задан")
        if not isinstance(source, dict):
            raise arguments_exeption("convert", "Ожидался dict")
        if self._chain is None:
            raise arguments_exeption(
                "convert", "Конвертер не привязан к chain (вызовите bind)"
            )

        code = source.get("unique_code")

        if self._is_short_reference(source):
            if code and self._resolver.has(code):
                return self._resolver.get_by_code(code)
            raise arguments_exeption(
                "unique_code",
                f"Ссылка на несуществующий объект {code!r}",
            )

        if code and code in visited:
            exist = self._resolver.get_by_code(code)
            if exist is not None:
                return exist
            raise arguments_exeption(
                "unique_code",
                f"Циклическая ссылка на объект {code!r}, который ещё собирается",
            )

        if code:
            visited.add(code)
        try:
            return self._resolver.build(source, self._chain, visited)
        finally:
            if code:
                visited.discard(code)
from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exeption
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.technicalmap_model import technicalmap_model
from Src.Models.warehouse_model import warehouse_model


class model_resolver:
    """Собирает модели из dict по декларативному описанию полей."""

    _parsers = (
        technicalmap_model,
        ingredient_model,
        nomenclature_model,
        range_model,
        warehouse_model,
        group_model,
    )

    def __init__(self, cache: dict | None = None):
        self._cache = cache if cache is not None else {}
        self._name_cache: dict = {}

    def has(self, code: str) -> bool:
        return code in self._cache

    def get_by_code(self, code: str):
        return self._cache.get(code)

    def clear(self) -> None:
        self._cache.clear()
        self._name_cache.clear()

    def register_name(self, model_cls, model) -> None:
        """Регистрирует модель в кэше имён (вызывает bootstrap)."""
        name = getattr(model, "name", None)
        if name is None:
            return
        self._name_cache.setdefault(model_cls, {})[name] = model

    def can_resolve(self, source: dict) -> bool:
        return any(cls.required_keys() <= source.keys() for cls in self._parsers)

    def build(self, source: dict, chain, visited: set = None):
        if visited is None:
            visited = set()
        for cls in self._parsers:
            if cls.required_keys() <= source.keys():
                model = cls.from_dict(source, chain, self, visited)
                return self._finish(model, source)
        raise arguments_exeption("model", "Не удалось определить тип модели")

    def _finish(self, model: abstract_model, source: dict):
        """Возвращает модель из кэша по unique_code, если она уже собрана.
        """
        code = source.get("unique_code")
        if code:
            if code in self._cache:
                return self._cache[code]
            model.unique_code = code
            self._cache[code] = model
        return model
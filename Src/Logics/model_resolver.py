from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exeption
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.technicalmap_model import technicalmap_model
from Src.Models.warehouse_model import warehouse_model


class model_resolver:
    """Собирает модели из dict по required_keys"""

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
        self._builders = {
            group_model:        self._build_group,
            range_model:        self._build_range,
            nomenclature_model: self._build_nomenclature,
            ingredient_model:   self._build_ingredient,
            technicalmap_model: self._build_recipe,
            warehouse_model:    self._build_warehouse,
        }


    def has(self, code: str) -> bool:
        return code in self._cache

    def get_by_code(self, code: str):
        return self._cache.get(code)

    def clear(self) -> None:
        self._cache.clear()

    def can_resolve(self, source: dict) -> bool:
        return any(cls.required_keys() <= source.keys() for cls in self._parsers)

    def build(self, source: dict, chain, visited: set = None):
        if visited is None:
            visited = set()
        for cls in self._parsers:
            if cls.required_keys() <= source.keys():
                return self._finish(self._builders[cls](source, chain, visited), source)
        raise arguments_exeption("model", "Не удалось определить тип модели")


    def _build_group(self, source, chain, visited):
        return group_model.create(source["name"])

    def _build_range(self, source, chain, visited):
        base = (
            chain.deserialize(source["base"], self, visited)
            if source.get("base") else None
        )
        return range_model.create(
            name=source["name"],
            conversion_factor=float(source.get("conversion_factor", 1.0)),
            base=base,
        )

    def _build_nomenclature(self, source, chain, visited):
        return nomenclature_model.create(
            full_name=source["full_name"],
            name=source["name"],
            group=chain.deserialize(source.get("group"), self, visited),
            range=chain.deserialize(source.get("range"), self, visited),
            item_type=source.get("item_type", ""),
        )

    def _build_ingredient(self, source, chain, visited):
        return ingredient_model.create(
            full_name=source.get("full_name") or source["name"],
            brutto=float(source["brutto"]),
            proteins=float(source["proteins"]),
            fats=float(source["fats"]),
            carbohydrates=float(source["carbohydrates"]),
            coef=float(source.get("coef", 1.0)),
            item_type=source.get("item_type"),
        )

    def _build_recipe(self, source, chain, visited):
        ingredients_raw = chain.deserialize(source.get("ingredients", {}), self, visited)
        if isinstance(ingredients_raw, dict):
            ingredients_raw = list(ingredients_raw.values())
        method = {
            k: chain.deserialize(v, self, visited)
            for k, v in source.get("preparation_method", {}).items()
        }
        return technicalmap_model.create(
            ingredients=ingredients_raw,
            preparation_method=method,
            description=source["description"],
            time=source["time"],
            name=source["name"],
        )

    def _build_warehouse(self, source, chain, visited):
        return warehouse_model.create(source["name"], source["address"])

    def _finish(self, model: abstract_model, source: dict):
        code = source.get("unique_code")
        if code:
            if code in self._cache:
                return self._cache[code]
            model.unique_code = code
            self._cache[code] = model
        return model
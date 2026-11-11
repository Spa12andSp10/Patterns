from Src.Core.abstract_manager import abstract_manager
from Src.Models.group_model import group_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.technicalmap_model import technicalmap_model
from Src.Models.warehouse_model import warehouse_model


class storage_manager(abstract_manager):
    """Singleton-хранилище доменных справочников."""

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(storage_manager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._groups = []
            self._nomenclature = []
            self._warehouse = []
            self._ranges = []
            self._recipes = []
            self._ingredients = []
            self._is_loaded = False

    @property
    def groups(self) -> list:
        return self._groups

    @property
    def ranges(self) -> list:
        return self._ranges

    @property
    def nomenclatures(self) -> list:
        return self._nomenclature

    @property
    def warehouses(self) -> list:
        return self._warehouse

    @property
    def recipes(self) -> list:
        return self._recipes

    @property
    def ingredients(self) -> list:
        return self._ingredients

    @staticmethod
    def _is_unique(items: list, candidate) -> bool:
        name = getattr(candidate, "name", None)
        if name is not None:
            return all(getattr(item, "name", None) != name for item in items)
        return all(item != candidate for item in items)

    def add_group(self, value: group_model) -> bool:
        if self._is_unique(self._groups, value):
            self._groups.append(value)
            return True
        return False

    def add_range(self, value: range_model) -> bool:
        if self._is_unique(self._ranges, value):
            self._ranges.append(value)
            return True
        return False

    def add_nomenclature(self, value: nomenclature_model) -> bool:
        if self._is_unique(self._nomenclature, value):
            self._nomenclature.append(value)
            return True
        return False

    def add_warehouse(self, value: warehouse_model) -> bool:
        if self._is_unique(self._warehouse, value):
            self._warehouse.append(value)
            return True
        return False

    def add_recipe(self, value) -> bool:
        if self._is_unique(self._recipes, value):
            self._recipes.append(value)
            return True
        return False

    def add_ingredient(self, value: ingredient_model) -> bool:
        if self._is_unique(self._ingredients, value):
            self._ingredients.append(value)
            return True
        return False

    def load_default_ranges(self) -> None:
        gram = range_model.create_gram()
        self.add_range(gram)

        kilogram = range_model.create_kilogram(base=gram)
        self.add_range(kilogram)

        tonna = range_model.create_tonna(base=kilogram)
        self.add_range(tonna)
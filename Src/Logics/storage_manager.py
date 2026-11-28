from pathlib import Path

from Src.Core.abstract_manager import abstract_manager
from Src.Models.group_model import group_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.transaction_model import transaction_model
from Src.Core.event_type import event_types
from Src.Core.message_type import message_type
from Src.Logics.observer import observer


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
            self._transactions = []
            self._is_loaded = False

    def load(self, models_file: str = "", raw_file: str = "") -> bool:
        """Загружает хранилище из слепка или выполняет первый старт.

        :param models_file: Путь к serialized_storage.json.
        :param raw_file: Путь к storage_data.json для первого старта.
        :return: True, если хранилище загружено.
        """
        if self._is_loaded:
            return True
        # Библиотеки объявлены в функции, чтобы избежать цикла
        from Src.Logics.storage_deserializer import storage_deserializer
        from Src.Logics.storage_bootstrap import storage_bootstrap

        if models_file:
            models_path = Path(models_file)
            if models_path.exists():
                if storage_deserializer(self).load(str(models_path)):
                    self._is_loaded = True
                    observer.create(event_types.LOAD_STORAGE, {"message": f"Хранилище загружено из {models_path}","system_name": "storage","message_type": message_type.INFO})
                    observer.create(event_types.CHANGE_STORAGE, {"message": "Данные изменены","system_name": "storage","message_type": message_type.INFO})
                    return True

        if raw_file:
            raw_path = Path(raw_file)
            if raw_path.exists():
                if storage_bootstrap(self).first_start(str(raw_path)):
                    self._is_loaded = True
                    observer.create(event_types.LOAD_STORAGE, {"message": f"Хранилище загружено из {raw_path}","system_name": "storage","message_type": message_type.INFO})
                    observer.create(event_types.CHANGE_STORAGE, {"message": "Данные изменены","system_name": "storage","message_type": message_type.INFO})
                    return True

        return False

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

    @property
    def transactions(self) -> list:
        return self._transactions

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

    def add_transaction(self, value: transaction_model) -> bool:
        if not self._is_unique(self._transactions, value):
            return False
        self._transactions.append(value)

        if value.value > 0:
            event = event_types.WAREHOUSE_INCOME
            what_event = "Приход"
        elif value.value < 0:
            event = event_types.WAREHOUSE_OUTCOME
            what_event = "Расход"

        observer.create(event, {"message": (f"{what_event}: {abs(value.value)} "
        f"в продукте {value.nomenclatures.name} "
        f"на складе {value.warehouses.name}"),"system_name": "warehouse","message_type": message_type.INFO})
        return True
        

    def load_default_ranges(self) -> None:
        gram = range_model.create_gram()
        self.add_range(gram)

        kilogram = range_model.create_kilogram(base=gram)
        self.add_range(kilogram)

        tonna = range_model.create_tonna(base=kilogram)
        self.add_range(tonna)
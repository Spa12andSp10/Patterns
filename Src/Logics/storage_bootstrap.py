import json

from Src.Core.exception import arguments_exeption
from Src.Core.ingredient_types import ingredient_type
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.group_model import group_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.technicalmap_model import technicalmap_model
from Src.Models.warehouse_model import warehouse_model


class storage_bootstrap:
    """Формирует эталонные данные при первом старте из «сырого» storage_data.json"""

    def __init__(self, storage: storage_manager = None) -> None:
        self._storage = storage if storage is not None else storage_manager()


    @staticmethod
    def _read_json(file_name: str) -> dict:
        with open(file_name, "r", encoding="utf-8") as file:
            return json.load(file)


    def _convert_ranges(self, data: list) -> None:
        by_name: dict = {}
        for item in data:
            param = range_model.create(
                name=item["name"],
                conversion_factor=item.get(
                    "conversion_factor",
                    item.get("conversation_factor", 1),
                ),
                base=None,
            )
            by_name[param.name] = param
            self._storage.add_range(param)

        for item in data:
            base_name = item.get("base")
            if base_name and item["name"] in by_name and base_name in by_name:
                by_name[item["name"]].base = by_name[base_name]

    def _convert_groups(self, data: list) -> None:
        for item in data:
            self._storage.add_group(group_model.create(name=item["name"]))

    def _find_group(self, name: str):
        for g in self._storage.groups:
            if g.name == name:
                return g
        return None

    def _find_range(self, name: str):
        for r in self._storage.ranges:
            if r.name == name:
                return r
        return None

    def _convert_nomenclature(self, data: list) -> None:
        for item in data:
            gr = self._find_group(item["group"])
            rn = self._find_range(item["range"])
            if gr is None or rn is None:
                raise arguments_exeption(
                    "nomenclature",
                    f"Не найдена группа/единица для '{item['name']}'",
                )
            self._storage.add_nomenclature(
                nomenclature_model.create(
                    full_name=item["full_name"],
                    name=item["name"],
                    group=gr,
                    range=rn,
                    item_type=item.get("item_type", item.get("type", "")),
                )
            )

    def _convert_warehouse(self, data: list) -> None:
        for item in data:
            self._storage.add_warehouse(
                warehouse_model.create(name=item["name"], address=item["address"])
            )

    def _convert_recipes(self, data: list) -> None:
        for item in data:
            ingredients = [
                ingredient_model.create(
                    full_name=ing["full_name"],
                    brutto=ing["brutto"],
                    proteins=ing["proteins"],
                    fats=ing["fats"],
                    carbohydrates=ing["carbohydrates"],
                    coef=ing.get("coef", 1.0),
                    item_type=ing.get("item_type", ing.get("type", ingredient_type.PRODUCT)),
                )
                for ing in item.get("ingredients", [])
            ]
            self._storage.add_recipe(
                technicalmap_model.create(
                    ingredients=ingredients,
                    preparation_method=item.get("preparation_method", {}),
                    description=item["description"],
                    time=item["time"],
                    name=item["name"],
                )
            )

    def _convert(self, data: dict) -> bool:
        self._storage._groups = []
        self._storage._nomenclature = []
        self._storage._warehouse = []
        self._storage._ranges = []
        self._storage._recipes = []
        self._storage._ingredients = []

        self._convert_ranges(data.get("ranges", []))
        self._convert_groups(data.get("groups", []))
        self._convert_nomenclature(data.get("nomenclature", []))
        self._convert_warehouse(data.get("warehouse", []))
        self._convert_recipes(data.get("recipes", []))
        return True

    def first_start(self, file_name: str = "") -> bool:
        """Загружает «сырые» эталонные данные, если установлен флаг первого старта."""
        manager = settings_manager()
        if not manager.is_loaded:
            manager.load()

        if not manager.settings.first_launch_flag:
            return False

        try:
            data = self._read_json(file_name or "storage_data.json")
        except (FileNotFoundError, json.JSONDecodeError):
            return False

        norm = self._convert(data)

        manager.settings.first_launch_flag = False
        manager.save()
        return norm
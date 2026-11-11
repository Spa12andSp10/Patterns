import json

from Src.Core.exception import base_exception
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model


class storage_bootstrap:
    """Формирует эталонные данные при первом старте.

    Десериализация моделей — через deserialize_factory.
    """

    __default_file_name = "storage_data.json"

    _mapping = (
        ("groups",       "add_group",       group_model),
        ("ranges",       "add_range",       range_model),
        ("nomenclature", "add_nomenclature", nomenclature_model),
        ("warehouse",    "add_warehouse",   warehouse_model),
        ("recipes",      "add_recipe",      None),
    )

    def __init__(self, storage: storage_manager = None,
                 factory: deserialize_factory = None) -> None:
        self._storage = storage if storage is not None else storage_manager()
        self._factory = factory if factory is not None else deserialize_factory()

    def _resolve_ranges(self, items: list) -> list:
        prepared = []
        by_name: dict = {}
        for raw in items:
            copy = dict(raw)
            copy["base"] = None
            prepared.append(copy)
            by_name[raw["name"]] = copy

        for raw, prepared_item in zip(items, prepared):
            base_name = raw.get("base")
            if base_name and base_name in by_name:
                prepared_item["base"] = by_name[base_name]
        return prepared

    def _load_section(self, items: list, add_method: str,
                      model_cls=None) -> None:
        if not items:
            return
        add = getattr(self._storage, add_method, None)
        if add is None:
            return
        for raw in items:
            model = self._factory.deserialize(raw)
            add(model)
            if model_cls is not None:
                self._factory.resolver.register_name(model_cls, model)

    def _load(self, data: dict) -> bool:
        self._factory.clear()

        self._load_section(data.get("groups", []),
                           "add_group", group_model)

        ranges_raw = self._resolve_ranges(data.get("ranges", []))
        self._load_section(ranges_raw, "add_range", range_model)

        self._load_section(data.get("nomenclature", []),
                           "add_nomenclature", nomenclature_model)

        self._load_section(data.get("warehouse", []),
                           "add_warehouse", warehouse_model)

        self._load_section(data.get("recipes", []),
                           "add_recipe", None)

        return True

    def first_start(self, file_name: str = "") -> bool:
        manager = settings_manager()
        if not manager.is_loaded:
            manager.load()

        if not manager.settings.first_launch_flag:
            return False

        inner = file_name or self.__default_file_name
        try:
            with open(inner, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return False

        try:
            loaded = self._load(data)
        except base_exception:
            return False
        if not loaded:
            return False

        manager.settings.first_launch_flag = False
        manager.save()
        return True
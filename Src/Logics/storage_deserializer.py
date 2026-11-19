import json
import logging
from Src.Core.abstract_deserialization import abstract_deserialization
from Src.Core.exception import base_exception
from Src.Core.validator import validator
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.storage_manager import storage_manager


logger = logging.getLogger(__name__)


class storage_deserializer(abstract_deserialization):
    """JSON -> storage_manager через deserialize_factory."""

    _mapping = (
        ("groups",        "add_group"),
        ("ranges",        "add_range"),
        ("nomenclature",  "add_nomenclature"),
        ("warehouse",     "add_warehouse"),
        ("recipes",       "add_recipe"),
    )

    def __init__(self, storage: storage_manager = None,
                 factory: deserialize_factory = None) -> None:
        self._storage = storage or storage_manager()
        self._factory = factory or deserialize_factory()

    @property
    def storage(self) -> storage_manager:
        """Публичный доступ к хранилищу (нужен в тестах и клиентах)."""
        return self._storage

    @property
    def factory(self) -> deserialize_factory:
        """Публичный доступ к фабрике (нужен в тестах)."""
        return self._factory

    def load(self, file_name: str) -> bool:
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, PermissionError,
                IsADirectoryError, json.JSONDecodeError) as e:
            logger.warning("storage_deserializer.load: %s", e)
            return False
        try:
            return self.deserialized(data)
        except base_exception as e:
            logger.warning("storage_deserializer.load: domain error %s", e)
            return False

    def deserialized(self, source: dict) -> bool:
        validator.validate(source, dict, "storage")
        self._factory.clear()

        for section, add_method in self._mapping:
            if section == "ranges":
                continue
            items = source.get(section)
            if not items:
                continue
            add = getattr(self._storage, add_method, None)
            if add is None:
                logger.warning(
                    "storage_deserializer: storage has no %s", add_method
                )
                continue
            for item in self._as_list(items):
                model = self._factory.deserialize(item)
                add(model)
                self._register(model)

        ranges = source.get("ranges")
        if ranges:
            self._deserialize_ranges(self._as_list(ranges))

        return True

    def _deserialize_ranges(self, items: list) -> None:
        """Двухфазная сборка ranges.
        """
        add = getattr(self._storage, "add_range", None)
        if add is None:
            logger.warning("storage_deserializer: storage has no add_range")
            return

        prepared = []
        by_code: dict = {}
        by_name: dict = {}

        for raw in items:
            if not isinstance(raw, dict):
                prepared.append((raw, None))
                continue
            copy = dict(raw)
            copy["base"] = None
            model = self._factory.deserialize(copy)
            add(model)
            self._register(model)
            prepared.append((raw, model))
            code = getattr(model, "unique_code", None)
            if code:
                by_code[code] = model
            name = getattr(model, "name", None)
            if name:
                by_name[name] = model

        for raw, model in prepared:
            if model is None:
                continue
            base_ref = raw.get("base")
            if not base_ref:
                continue
            base = self._resolve_base(base_ref, by_code, by_name)
            if base is not None:
                model.base = base

    @staticmethod
    def _resolve_base(base_ref, by_code: dict, by_name: dict):
        """base может быть: None, str (name), dict с unique_code,
        либо полным объектом с unique_code."""
        if base_ref is None:
            return None
        if isinstance(base_ref, str):
            return by_name.get(base_ref)
        if isinstance(base_ref, dict):
            code = base_ref.get("unique_code")
            if code and code in by_code:
                return by_code[code]
            name = base_ref.get("name")
            if name and name in by_name:
                return by_name[name]
        return None

    def _register(self, model) -> None:
        """Регистрирует модель в резолвере по типу и коду/имени,
        чтобы последующие ссылки резолвились в ТОТ ЖЕ объект."""
        resolver = self._factory.resolver
        register = getattr(resolver, "register", None)
        if register is not None:
            register(model)
            return
        register_name = getattr(resolver, "register_name", None)
        if register_name is not None:
            register_name(type(model), model)

    def deserialize_item(self, data: dict):
        return self._factory.deserialize(data)

    @staticmethod
    def _as_list(value) -> list:
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            keys = sorted(value.keys(), key=int)
            return [value[k] for k in keys]
        raise base_exception("storage", "Ожидался список или словарь")
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
            items = source.get(section)
            if not items:
                continue
            add = getattr(self._storage, add_method, None)
            if add is None:
                logger.warning("storage_deserializer: storage has no %s", add_method)
                continue
            for item in self._as_list(items):
                add(self._factory.deserialize(item))
        return True

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
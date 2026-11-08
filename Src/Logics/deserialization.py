import json

from Src.Core.abstract_deserialization import abstract_deserialization
from Src.Core.entity_type import entity_type
from Src.Core.exception import base_exception
from Src.Core.validator import validator
from Src.Logics.deserialization_convertor_factory import deserialization_convertor_factory
from Src.Logics.model_repository import model_repository


class deserialization(abstract_deserialization):
    """Модельный JSON -> storage_manager (только десериализация)."""

    _mapping = (
        ("groups",       entity_type.GROUP,        "add_group"),
        ("ranges",       entity_type.RANGE,        "add_range"),
        ("nomenclature", entity_type.NOMENCLATURE, "add_nomenclature"),
        ("warehouse",    entity_type.WAREHOUSE,    "add_warehouse"),
        ("ingredients",  entity_type.INGREDIENT,   "add_ingredient"),
        ("recipes",      entity_type.RECIPE,       "add_recipe"),
    )

    def __init__(self, storage, repository: model_repository = None,
                 factory: deserialization_convertor_factory = None) -> None:
        self._storage = storage
        self._repository = repository or model_repository()
        self._factory = factory or deserialization_convertor_factory(self._repository)

    def load(self, file_name: str) -> bool:
        """Читает модельный JSON и наполняет хранилище.

        Любая ошибка превращается в `False`.

        :param file_name: Путь к JSON-файлу.
        :return: True при успехе, иначе False.
        """
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
            return self.deserialized(data)
        except (FileNotFoundError, PermissionError, IsADirectoryError):
            return False
        except json.JSONDecodeError:
            return False
        except base_exception:
            return False
        except Exception:
            return False

    def deserialized(self, data: dict) -> bool:
        """Наполняет storage_manager моделями по _mapping.

        :param data: Разобранный модельный JSON.
        :return: True при успехе.
        """
        validator.validate(data, dict, "storage")
        self._repository.clear()

        for section, entity, add_method in self._mapping:
            items = data.get(section)
            if not items:
                continue

            convertor = self._factory.create(entity)
            add = getattr(self._storage, add_method)

            for item in items:
                add(convertor.deserialize(item))

        return True
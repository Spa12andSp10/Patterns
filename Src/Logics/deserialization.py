import json

from Src.Core.abstract_deserialization import abstract_deserialization
from Src.Core.validator import validator
from Src.Logics.model_repository import model_repository
from Src.Logics.deserialization_convertor_factory import deserialization_convertor_factory


class deserialization(abstract_deserialization):
    """Модельный JSON -> storage_manager.

    Секции JSON обрабатываются по порядку, заданному _mapping.

    """

    _mapping = (
        ("groups",       "group",        "add_group"),
        ("ranges",       "range",        "add_range"),
        ("nomenclature", "nomenclature", "add_nomenclature"),
        ("warehouse",    "warehouse",    "add_warehouse"),
        ("ingredients",  "ingredient",   "add_ingredient"),
        ("recipes",      "recipe",       "add_recipe"),
    )

    def __init__(self, storage, repository: model_repository = None,
                 factory: deserialization_convertor_factory = None) -> None:
        self._storage = storage
        self._repository = repository or model_repository()
        self._factory = factory or deserialization_convertor_factory(self._repository)

    def load(self, file_name: str) -> bool:
        """Читает модельный JSON из файла и наполняет хранилище.

        :param file_name: Путь к JSON-файлу.
        :return: True при успехе.
        """
        with open(file_name, encoding="utf-8") as f:
            data = json.load(f)
        return self.deserialized(data)

    def deserialized(self, data: dict) -> bool:
        """Наполняет storage_manager моделями по _mapping.

        :param data: Разобранный модельный JSON.
        :return: True при успехе.
        """
        validator.validate(data, dict, "storage")
        self._repository.clear()

        for section, entity_type, add_method in self._mapping:
            items = data.get(section)
            if not items:
                continue

            convertor = self._factory.create(entity_type)
            add = getattr(self._storage, add_method)

            for item in items:
                add(convertor.convert(item))

        return True
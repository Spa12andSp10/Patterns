from Src.Core.entity_type import entity_type
from Src.Core.exception import arguments_exeption
from Src.Logics.model_repository import model_repository
from Src.Core.abstract_deserialization_convertor_factory import (
    abstract_deserialization_convertor_factory,
)

import Src.Logics.group_from_json
import Src.Logics.range_from_json 
import Src.Logics.nomenclature_from_json
import Src.Logics.ingredient_from_json
import Src.Logics.technicalmap_from_json
import Src.Logics.warehouse_from_json
import Src.Logics.organization_from_json


class deserialization_convertor_factory:
    """Фабрика конвертеров десериализации (dict -> доменная модель)."""

    def __init__(self, repository: model_repository = None) -> None:
        self._repository = repository or model_repository()

    def create(self, entity):
        """Создаёт конвертер по типу сущности."""
        try:
            key = entity_type(entity)
        except ValueError:
            key = entity

        cls = abstract_deserialization_convertor_factory._registry.get(key)
        if cls is None:
            raise arguments_exeption(
                "entity",
                f"Нет конвертера типа {entity!r}. "
                f"Доступны: {sorted(e.value for e in entity_type)}",
            )
        return cls.create(self._repository)

    def types(self) -> list:
        return sorted(e.value for e in entity_type)
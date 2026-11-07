from Src.Core.exception import arguments_exeption
from Src.Logics.model_repository import model_repository
from Src.Logics.group_from_json import group_from_json
from Src.Logics.range_from_json import range_from_json
from Src.Logics.nomenclature_from_json import nomenclature_from_json
from Src.Logics.ingredient_from_json import ingredient_from_json
from Src.Logics.technicalmap_from_json import technicalmap_from_json
from Src.Logics.warehouse_from_json import warehouse_from_json
from Src.Logics.organization_from_json import organization_from_json


class deserialization_convertor_factory:
    """Фабрика конвертеров dict -> доменная модель.

    Единственное место, где перечислены все конвертеры.
    """

    _registry: dict = {
        "group":        group_from_json,
        "range":        range_from_json,
        "nomenclature": nomenclature_from_json,
        "ingredient":   ingredient_from_json,
        "recipe":       technicalmap_from_json,
        "warehouse":    warehouse_from_json,
        "organization": organization_from_json,
    }

    def __init__(self, repository: model_repository = None) -> None:
        self._repository = repository or model_repository()

    def create(self, entity: str):
        """Создаёт конвертер по имени типа сущности.

        :param entity: Имя типа (ключ из _registry).
        :return: Экземпляр конвертера, связанный с репозиторием.
        :raises arguments_exeption: Если тип неизвестен.
        """
        cls = self._registry.get(entity)
        if cls is None:
            raise arguments_exeption(
                "entity",
                f"Нет конверта типа {entity!r}. "
                f"Доступны: {sorted(self._registry)}"
            )
        return cls(self._repository)

    def types(self) -> list:
        """Возвращает список поддерживаемых типов."""
        return sorted(self._registry)
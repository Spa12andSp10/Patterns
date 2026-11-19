from Src.Core.exception import arguments_exeption
from Src.Logics.storage_manager import storage_manager


class entity_resolver:
    """Резолвер сущностей по типу и уникальному коду."""

    def __init__(self, storage: storage_manager = None):
        """Инициализирует резолвер.

        :param storage: Хранилище. Если None — берётся Singleton.
        """
        self.__storage = storage if storage is not None else storage_manager()

        self.__providers: dict = {
            "recipe":       lambda: self.__storage.recipes,
            "nomenclature": lambda: self.__storage.nomenclatures,
            "range":        lambda: self.__storage.ranges,
            "warehouse":    lambda: self.__storage.warehouses,
            "group":        lambda: self.__storage.groups,
        }

    def supported_types(self) -> list[str]:
        """Возвращает список поддерживаемых типов сущностей."""
        return list(self.__providers.keys())

    def provider_for(self, entity_type: str):
        """Возвращает callable для получения списка сущностей данного типа.

        :param entity_type: Тип сущности.
        :return: Callable без аргументов, возвращающий список.
        :raises arguments_exeption: Если тип не поддерживается.
        """
        entity_type = (entity_type or "").strip().lower()
        provider = self.__providers.get(entity_type)
        if provider is None:
            raise arguments_exeption(
                "type",
                f"Неизвестный тип сущности: {entity_type!r}. "
                f"Допустимые: {self.supported_types()}"
            )
        return provider

    def resolve(self, entity_type: str, code: str):
        """Находит сущность по типу и уникальному коду.

        :param entity_type: Тип сущности ('recipe', 'nomenclature', 'range',
            'warehouse', 'group').
        :param code: Уникальный код сущности.
        :return: Найденная доменная модель.
        :raises arguments_exeption: Если тип не поддерживается.
        :raises LookupError: Если сущность с таким кодом не найдена.
        """
        entity_type = (entity_type or "").strip().lower()
        code = (code or "").strip()

        if not entity_type:
            raise arguments_exeption("type", "Параметр 'type' обязателен")
        if not code:
            raise arguments_exeption("code", "Параметр 'code' обязателен")

        provider = self.__providers.get(entity_type)
        if provider is None:
            raise arguments_exeption(
                "type",
                f"Неизвестный тип сущности: {entity_type!r}. "
                f"Допустимые: {self.supported_types()}"
            )

        for item in provider():
            if item.unique_code == code:
                return item

        raise LookupError(
            f"Сущность типа '{entity_type}' с кодом '{code}' не найдена"
        )

    def all_entities(self):
        """Итерирует все сущности всех поддерживаемых типов."""
        for provider in self.__providers.values():
            yield from provider()

    def find_by_code(self, code: str):
        """Находит сущность по уникальному коду без указания типа.

        :param code: Уникальный код сущности.
        :return: Найденная модель или None.
        """
        normalized = (code or "").strip()
        if not normalized:
            return None

        for entity in self.all_entities():
            if entity.unique_code == normalized:
                return entity

        return None

    def collection_for(self, entity):
        """Возвращает коллекцию, в которой хранится сущность.

        :param entity: Доменная модель.
        :return: Список сущностей или None.
        """
        for provider in self.__providers.values():
            items = provider()
            if any(item is entity or item == entity for item in items):
                return items

        return None

    def remove(self, entity) -> bool:
        """Удаляет сущность из соответствующей коллекции.

        :param entity: Доменная модель.
        :return: True при успешном удалении.
        """
        items = self.collection_for(entity)
        if items is None:
            return False

        try:
            items.remove(entity)
        except ValueError:
            return False

        return True

    def replace(self, entity, replacement) -> bool:
        """Заменяет сущность в её коллекции.

        :param entity: Старая модель.
        :param replacement: Новая модель.
        :return: True при успешной замене.
        """
        items = self.collection_for(entity)
        if items is None:
            return False

        for index, item in enumerate(items):
            if item is entity or item == entity:
                items[index] = replacement
                return True

        return False
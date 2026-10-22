from Src.Core.exception import arguments_exeption
from Src.Logics.storage_manager import storage_manager


class entity_resolver:
    """Резолвер сущностей по типу и уникальному коду.

    Инкапсулирует знание о том, где в хранилище лежит та или иная
    коллекция. main.py больше не знает про storage.recipes /
    storage.nomenclatures / storage.ranges — он просто просит
    резолвер найти сущность.

    Фабрика {тип: метод получения списка} позволяет добавлять новые
    типы сущностей без правки метода resolve (принцип Open/Closed).
    """

    def __init__(self, storage: storage_manager = None):
        """Инициализирует резолвер.

        :param storage: Хранилище. Если None — берётся Singleton.
        """
        self.__storage = storage if storage is not None else storage_manager()

        # Фабрика: {тип сущности: метод получения списка из хранилища}.
        # Методы — лямбды без аргументов, чтобы не тащить storage в каждую.
        self.__providers: dict = {
            "recipe": lambda: self.__storage.recipes,
            "nomenclature": lambda: self.__storage.nomenclatures,
            "range": lambda: self.__storage.ranges,
        }

    def supported_types(self) -> list[str]:
        """Возвращает список поддерживаемых типов сущностей."""
        return list(self.__providers.keys())

    def resolve(self, entity_type: str, code: str):
        """Находит сущность по типу и уникальному коду.

        :param entity_type: Тип сущности ('recipe', 'nomenclature', 'range').
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
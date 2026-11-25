from Src.Core.entity_type import entity_type
from Src.Core.exception import arguments_exeption
from Src.Core.filters_type import filters_type
from Src.Dtos.filter_item_dto import filter_item_dto
from Src.Core.validator import validator


class filter_dto:
    """Набор условий фильтрации DOMAIN-модели.
    """

    SUPPORTED_DOMAINS: tuple = (
        entity_type.NOMENCLATURE,
        entity_type.GROUP,
        entity_type.RANGE,
        entity_type.RECIPE,
    )

    _filters: list[filter_item_dto]
    __domain: str = ""

    def __init__(
        self,
        filters: list[filter_item_dto] | None = None,
        domain: str = "",
    ) -> None:
        """Создаёт набор условий фильтрации.

        """
        self._filters = []
        self.domain = domain

        if filters is not None:
            self.filters = filters

    @property
    def domain(self) -> str:
        """Возвращает тип DOMAIN-модели.

        Пустая строка означает, что DTO не привязан к конкретной модели.
        """
        return self.__domain

    @domain.setter
    def domain(self, value: str | entity_type) -> None:
        """Устанавливает тип DOMAIN-модели.

        """
        if value is None:
            self.__domain = ""
            return

        if isinstance(value, entity_type):
            value = value.value

        if not isinstance(value, str):
            raise arguments_exeption(
                "domain",
                "Ожидалась строка или значение entity_type",
            )

        normalized = value.strip().lower()
        if normalized == "":
            self.__domain = ""
            return

        allowed = {item.value for item in self.SUPPORTED_DOMAINS}
        if normalized not in allowed:
            raise arguments_exeption(
                "domain",
                f"Допустимые модели: {', '.join(sorted(allowed))}",
            )

        self.__domain = normalized

    @property
    def filters(self) -> list[filter_item_dto]:
        """Возвращает список условий фильтрации."""
        return self._filters

    @filters.setter
    def filters(self, value: list[filter_item_dto]) -> None:
        """Устанавливает список условий фильтрации.

        """
        if not isinstance(value, list):
            raise arguments_exeption("filters", "Должен быть списком")

        for item in value:
            if not isinstance(item, filter_item_dto):
                raise arguments_exeption(
                    "filters[]",
                    "Ожидался filter_item_dto",
                )

        self._filters = list(value)

    def add(self, item: filter_item_dto) -> "filter_dto":
        """Добавляет условие фильтрации.

        """
        if not isinstance(item, filter_item_dto):
            raise arguments_exeption("item", "Ожидался filter_item_dto")

        self._filters.append(item)
        return self

    def add_name(
        self,
        value: str,
        filter_type: filters_type = filters_type.LIKE,
    ) -> "filter_dto":
        """Добавляет условие фильтрации по наименованию.

        """
        return self.add(filter_item_dto.by_name(value, filter_type))

    def add_unique_code(self, value: str) -> "filter_dto":
        """Добавляет условие фильтрации по уникальному коду.

        """
        return self.add(filter_item_dto.by_unique_code(value))

    def add_path(
        self,
        path: str,
        value: str,
        filter_type: filters_type = filters_type.LIKE,
    ) -> "filter_dto":
        """Добавляет условие фильтрации по вложенному пути.

        """
        return self.add(filter_item_dto.by_path(path, value, filter_type))

    @classmethod
    def create(
        cls,
        filters: list[filter_item_dto] | None = None,
        domain: str = "",
    ) -> "filter_dto":
        """Создаёт набор условий фильтрации.

        """
        return cls(filters=filters, domain=domain)

    @classmethod
    def name_filter(
        cls,
        value: str,
        filter_type: filters_type = filters_type.LIKE,
        domain: str = "",
    ) -> "filter_dto":
        """Создаёт DTO с одним условием фильтрации по наименованию.

        """
        return cls(domain=domain).add_name(value, filter_type)

    @classmethod
    def unique_code_filter(
        cls,
        value: str = "",
        domain: str = "",
    ) -> "filter_dto":
        """Создаёт DTO с одним условием фильтрации по уникальному коду.

        """
        return cls(domain=domain).add_unique_code(value)

    @classmethod
    def path_filter(
        cls,
        path: str,
        value: str,
        filter_type: filters_type = filters_type.LIKE,
        domain: str = "",
    ) -> "filter_dto":
        """Создаёт DTO с одним условием фильтрации по вложенному пути.

        """
        return cls(domain=domain).add_path(path, value, filter_type)

    @classmethod
    def from_dict(cls, data: dict, domain: str = "") -> "filter_dto":
        validator.validate(data, dict)

        filt = data.get("filters", [])
        if not isinstance(filt, list):
            raise arguments_exeption("from_dict", "Должен быть списком")

        res = cls(domain=domain)
        for f in filt:
            res.add(filter_item_dto.from_dict(f))

        return res


    def __iter__(self):
        return iter(self._filters)

    def __len__(self) -> int:
        return len(self._filters)

    def __getitem__(self, index: int) -> filter_item_dto:
        return self._filters[index]

    def __repr__(self) -> str:
        return f"filter_dto(domain={self.__domain!r}, filters={self._filters!r})"

import re

from Src.Core.exception import arguments_exeption
from Src.Core.filters_type import filters_type
from Src.Core.validator import validator


class filter_item_dto:
    """Одно условие фильтрации DOMAIN-модели.

    Условие описывает поле, значение и способ обработки. Поддерживаются
    прямые поля ``name`` и ``unique_code``, числовые поля (``value``,
    ``conversion_factor`` и т.п.), а также вложенные пути.
    """

    FIELD_NAME: str = "name"
    FIELD_UNIQUE_CODE: str = "unique_code"
    _STRING_FIELDS: tuple = (
        "full_name",
        "address",
        "description",
        "time",
        "system_name",
        "message_type",
        "message",
    )
    
    _NUMERIC_FIELDS: tuple = (
        "conversion_factor",
        "brutto",
        "proteins",
        "fats",
        "carbohydrates",
        "coef",
        "value",
        "period",
    )
    _ALLOWED_FIELDS: tuple = (
        FIELD_NAME,
        FIELD_UNIQUE_CODE,
        *_STRING_FIELDS,
        *_NUMERIC_FIELDS,
    )
    SORTING_TYPES: tuple = (
        filters_type.ALPHABET,
        filters_type.ALPHABET_DESC,
    )
    _TYPE_ALIASES: dict = {
        "reverse_alphabet": filters_type.ALPHABET_DESC,
        "alphabet_reverse": filters_type.ALPHABET_DESC,
        "alphabet_desc": filters_type.ALPHABET_DESC,
        "reverse": filters_type.ALPHABET_DESC,
    }
    _PATH_PATTERN = re.compile(
        r"^[A-Za-z_]\w*(\[\])?(\.[A-Za-z_]\w*(\[\])?)*$"
    )

    _filter_name: str = ""
    _filter_type: filters_type = filters_type.EQUALS
    _filter_value: str = ""

    def __init__(
        self,
        filter_name: str = FIELD_NAME,
        filter_value: str = "",
        filter_type: filters_type = filters_type.EQUALS,
    ) -> None:
        """Создаёт условие фильтрации.

        """
        self.filter_name = filter_name
        self.filter_type = filter_type
        self.filter_value = filter_value

    @property
    def filter_name(self) -> str:
        """Возвращает путь к полю, по которому выполняется фильтрация."""
        return self._filter_name

    @filter_name.setter
    def filter_name(self, value: str) -> None:
        """Устанавливает путь к полю фильтрации.

        """
        validator.validate(value, str, "filter_name")
        normalized = value.strip().lower()

        if not self._PATH_PATTERN.fullmatch(normalized):
            raise arguments_exeption(
                "filter_name",
                "Ожидался путь к полю, например: name, base.name, "
                "group.name, ingredients[].name",
            )

        last_field = normalized.split(".")[-1].replace("[]", "")
        if last_field not in self._ALLOWED_FIELDS:
            raise arguments_exeption(
                "filter_name",
                f"Допустимые конечные поля: "
                f"{', '.join(self._ALLOWED_FIELDS)}",
            )

        self._filter_name = normalized

    @property
    def filter_type(self) -> filters_type:
        """Возвращает способ сравнения значения."""
        return self._filter_type

    @filter_type.setter
    def filter_type(self, value: filters_type) -> None:
        """Устанавливает способ обработки значения.
        """
        if isinstance(value, filters_type):
            self._filter_type = value
            return

        if isinstance(value, str):
            normalized = value.strip().lower()
            value = self._TYPE_ALIASES.get(normalized, normalized)

        try:
            self._filter_type = filters_type(value)
        except (TypeError, ValueError):
            allowed = [item.value for item in filters_type]
            allowed.extend(self._TYPE_ALIASES.keys())
            raise arguments_exeption(
                "filter_type",
                f"Допустимые значения: {allowed}",
            )

    @property
    def filter_value(self) -> str:
        """Возвращает искомое значение."""
        return self._filter_value

    @filter_value.setter
    def filter_value(self, value: str) -> None:
        """Устанавливает искомое значение.

        """
        if not isinstance(value, str):
            raise arguments_exeption("filter_value", "Ожидалась строка")

        self._filter_value = value.strip()

    @classmethod
    def create(
        cls,
        filter_name: str,
        filter_value: str,
        filter_type: filters_type = filters_type.EQUALS,
    ) -> "filter_item_dto":
        """Создаёт условие фильтрации.
        """
        return cls(
            filter_name=filter_name,
            filter_value=filter_value,
            filter_type=filter_type,
        )

    @classmethod
    def by_name(
        cls,
        value: str,
        filter_type: filters_type = filters_type.LIKE,
    ) -> "filter_item_dto":
        """Создаёт условие фильтрации по наименованию.
        """
        return cls.create(cls.FIELD_NAME, value, filter_type)

    @classmethod
    def by_unique_code(cls, value: str) -> "filter_item_dto":
        """Создаёт условие фильтрации по уникальному коду.
        """
        return cls.create(
            cls.FIELD_UNIQUE_CODE,
            value,
            filters_type.EQUALS,
        )

    @classmethod
    def by_path(
        cls,
        path: str,
        value: str,
        filter_type: filters_type = filters_type.LIKE,
    ) -> "filter_item_dto":
        """Создаёт условие фильтрации по вложенному пути.

        """
        return cls.create(path, value, filter_type)

    @classmethod
    def from_dict(cls, data: dict) -> "filter_item_dto":
        """Создаёт условие из словаря.
        """
        validator.validate(data, dict)

        if "filter_name" not in data:
            raise arguments_exeption("filter_name", "Обязательное поле")

        item = cls(
            filter_name=data["filter_name"],
            filter_type=data.get("filter_type", filters_type.EQUALS),
        )

        if "filter_value" in data:
            item.filter_value = data["filter_value"]
        elif item.filter_type not in cls.SORTING_TYPES:
            raise arguments_exeption("filter_value", "Обязательное поле")

        return item
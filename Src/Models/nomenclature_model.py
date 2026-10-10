from Src.Core.entity_model import entity_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exeption, max_length_exeption
from Src.Core.validator import validator


class nomenclature_model(entity_model):
    """Модель номенклатуры.

    Содержит определения: наименование, полное наименование,
    максимальную длину полного наименования, группу номенклатуры
    и единицу измерения.
    """

    __full_name: str = ""
    __full_name_max_lenght: int = 255
    __group: group_model = None
    __range: range_model = None
    __type: str = ""

    def __init__(self, full_name: str = "", name: str = "",
                 group: group_model = None,
                 range: range_model = None,
                 type: str = "") -> None:
        """Инициализирует номенклатуру.

        :param full_name: Полное наименование номенклатуры.
        :param name: Краткое наименование номенклатуры.
        :param group: Группа номенклатуры или None.
        :param range: Единица измерения или None.
        """
        super().__init__()
        self.name = name
        self.full_name = full_name
        self.group = group
        self.range = range

    @property
    def full_name(self) -> str:
        """Возвращает полное наименование номенклатуры."""
        return self.__full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        """Устанавливает полное наименование номенклатуры.

        :param value: Полное наименование.
        :raises arguments_exeption: Если значение не строка или None.
        :raises max_length_exeption: Если длина превышает максимально допустимую.
        """
        validator.validate(value, str, self.__full_name_max_lenght)
        self.__full_name = value

    @property
    def group(self) -> group_model:
        """Возвращает группу номенклатуры."""
        return self.__group

    @group.setter
    def group(self, value: group_model) -> None:
        if value is not None and not isinstance(value, group_model):
            raise arguments_exeption("group", "Некорректно переданный аргумент")
        self.__group = value

    @property
    def range(self) -> range_model:
        """Возвращает единицу измерения номенклатуры."""
        return self.__range
    
    @range.setter
    def range(self, value: range_model) -> None:
        if value is not None and not isinstance(value, range_model):
            raise arguments_exeption("range", "Некорректно переданный аргумент")
        self.__range = value

    @property
    def type(self) -> str:
        return self.__type

    @type.setter
    def type(self, value: str):
        validator.validate(value, str, "type")
        self.__type = value




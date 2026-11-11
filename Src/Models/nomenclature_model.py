from Src.Core.entity_model import entity_model
from Src.Core.exception import arguments_exeption
from Src.Core.validator import validator
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model


class nomenclature_model(entity_model):
    """Модель номенклатуры."""

    __full_name: str = ""
    __full_name_max_lenght: int = 255
    __group: group_model = None
    __range: range_model = None

    _fields = (
        ("full_name", "primitive", None, str),
        ("name", "primitive", None, str),
        ("group", "model", group_model, None, (), False, None),
        ("range", "model", range_model, None, (), False, None),
        ("item_type", "primitive", None, str, ("type",), False, ""),
    )

    def __init__(self, full_name: str = "", name: str = "",
                 group: group_model = None,
                 range: range_model = None,
                 item_type: str = "") -> None:
        super().__init__()
        self.name = name
        self.full_name = full_name
        self.group = group
        self.range = range
        self.item_type = item_type

    @classmethod
    def create(cls, full_name: str, name: str,
               group: group_model = None,
               range: range_model = None,
               item_type: str = "") -> "nomenclature_model":
        return cls(
            full_name=full_name, name=name, group=group,
            range=range, item_type=item_type,
        )

    @property
    def full_name(self) -> str:
        return self.__full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        validator.validate(value, str, "full_name",
                           max_len=self.__full_name_max_lenght)
        self.__full_name = value

    @property
    def group(self) -> group_model:
        return self.__group

    @group.setter
    def group(self, value: group_model) -> None:
        if value is not None and not isinstance(value, group_model):
            raise arguments_exeption("group", "Некорректно переданный аргумент")
        self.__group = value

    @property
    def range(self) -> range_model:
        return self.__range

    @range.setter
    def range(self, value: range_model) -> None:
        if value is not None and not isinstance(value, range_model):
            raise arguments_exeption("range", "Некорректно переданный аргумент")
        self.__range = value
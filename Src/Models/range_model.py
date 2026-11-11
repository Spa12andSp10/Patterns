from Src.Core.entity_model import entity_model
from Src.Core.exception import arguments_exeption
from Src.Core.validator import validator


class range_model(entity_model):
    """Модель единицы измерения."""

    __base: "range_model" = None
    __conversion_factor: float = 1.0

    _fields = (
        ("name", "primitive", None, str),
        ("conversion_factor", "primitive", None, float),
        ("base", "model", None, None, (), False, None),
    )
    def __init__(self, name: str = "", conversion_factor: float = 1.0,
                 base: "range_model" = None) -> None:
        super().__init__()
        self.name = name
        self.base = base
        self.conversion_factor = conversion_factor

    @classmethod
    def create(cls, name: str, conversion_factor: float = 1.0,
               base: "range_model" = None) -> "range_model":
        return cls(name=name, conversion_factor=conversion_factor, base=base)

    @classmethod
    def create_gram(cls) -> "range_model":
        return cls(name="Gram", conversion_factor=1, base=None)

    @classmethod
    def create_milliliter(cls) -> "range_model":
        return cls(name="Milliliter", conversion_factor=1, base=None)

    @classmethod
    def create_kilogram(cls, base: "range_model" = None) -> "range_model":
        if base is None:
            base = cls.create_gram()
        return cls(name="Kilogram", conversion_factor=1000, base=base)

    @classmethod
    def create_tonna(cls, base: "range_model" = None) -> "range_model":
        if base is None:
            base = cls.create_kilogram()
        return cls(name="Tonna", conversion_factor=1000, base=base)

    @classmethod
    def create_liter(cls, base: "range_model" = None) -> "range_model":
        if base is None:
            base = cls.create_milliliter()
        return cls(name="Liter", conversion_factor=1000, base=base)

    @property
    def base(self) -> "range_model":
        return self.__base

    @base.setter
    def base(self, value) -> None:
        if value is not None and not isinstance(value, range_model):
            raise arguments_exeption("base", "Некорректно переданный аргумент")
        self.__base = value

    @property
    def conversion_factor(self) -> float:
        return self.__conversion_factor

    @conversion_factor.setter
    def conversion_factor(self, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise arguments_exeption("conversion_factor",
                                     "Некорректно переданный аргумент")
        validator.no_lower_that_zero_validate(value, "conversion_factor")
        self.__conversion_factor = float(value)
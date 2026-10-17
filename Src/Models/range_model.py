from Src.Core.entity_model import entity_model
from Src.Core.exception import arguments_exeption
from Src.Core.validator import validator


class range_model(entity_model):
    """Модель единицы измерения.

    Содержит базовую единицу измерения и коэффициент пересчёта.
    Создаётся через classmethod-конструкторы create / create_gram /
    create_kilogram / create_tonna / create_milliliter / create_liter.
    """

    __base: "range_model" = None
    __conversion_factor: float = 1.0

    def __init__(self, name: str = "", conversion_factor: float = 1.0,
                 base: "range_model" = None) -> None:
        """Инициализирует единицу измерения.

        :param name: Наименование (например, 'кг').
        :param conversion_factor: Коэффициент пересчёта к базовой единице.
        :param base: Базовая единица измерения (например, 'грамм').
        """
        super().__init__()
        self.name = name
        self.base = base
        self.conversion_factor = conversion_factor

    @classmethod
    def create(cls, name: str, conversion_factor: float = 1.0,
               base: "range_model" = None) -> "range_model":
        """Создаёт единицу измерения по параметрам.

        :param name: Наименование единицы.
        :param conversion_factor: Коэффициент пересчёта к базовой единице.
        :param base: Базовая единица измерения.
        :return: Созданная единица измерения.
        """
        return cls(name=name, conversion_factor=conversion_factor, base=base)

    @classmethod
    def create_gram(cls) -> "range_model":
        """Создаёт грамм — базовую единицу массы."""
        return cls(name="Gram", conversion_factor=1, base=None)

    @classmethod
    def create_milliliter(cls) -> "range_model":
        """Создаёт миллилитр — базовую единицу объёма."""
        return cls(name="Milliliter", conversion_factor=1, base=None)

    @classmethod
    def create_kilogram(cls, base: "range_model" = None) -> "range_model":
        """Создаёт килограмм (1000 грамм).

        :param base: Базовая единица. Если None — создаётся грамм.
        """
        if base is None:
            base = cls.create_gram()
        return cls(name="Kilogram", conversion_factor=1000, base=base)

    @classmethod
    def create_tonna(cls, base: "range_model" = None) -> "range_model":
        """Создаёт тонну (1000 килограмм).

        :param base: Базовая единица. Если None — создаётся килограмм.
        """
        if base is None:
            base = cls.create_kilogram()
        return cls(name="Tonna", conversion_factor=1000, base=base)

    @classmethod
    def create_liter(cls, base: "range_model" = None) -> "range_model":
        """Создаёт литр (1000 миллилитров).

        :param base: Базовая единица. Если None — создаётся миллилитр.
        """
        if base is None:
            base = cls.create_milliliter()
        return cls(name="Liter", conversion_factor=1000, base=base)

    @property
    def base(self) -> "range_model":
        """Возвращает базовую единицу измерения."""
        return self.__base

    @base.setter
    def base(self, value) -> None:
        if value is not None and not isinstance(value, range_model):
            raise arguments_exeption("base", "Некорректно переданный аргумент")
        self.__base = value

    @property
    def conversion_factor(self) -> float:
        """Возвращает коэффициент пересчёта относительно базовой единицы."""
        return self.__conversion_factor

    @conversion_factor.setter
    def conversion_factor(self, value: float) -> None:
        """Устанавливает коэффициент пересчёта (должен быть > 0).

        :param value: Числовое значение коэффициента.
        :raises arguments_exeption: Если значение не число или <= 0.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise arguments_exeption("conversion_factor",
                                     "Некорректно переданный аргумент")
        validator.no_lower_that_zero_validate(value, "conversion_factor")
        self.__conversion_factor = float(value)
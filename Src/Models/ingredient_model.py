from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.validator import validator


class ingredient_model(nomenclature_model):
    """Модель ингредиента.

    Наследует полное наименование, группу и единицу измерения от
    номенклатуры. Дополнительно содержит брутто, пищевую ценность
    (белки, жиры, углеводы) и коэффициент пересчёта.
    """

    __brutto: float = 0.0
    __proteins: float = 0.0
    __fats: float = 0.0
    __carbohydrates: float = 0.0
    __coef: float = 0.0

    def __init__(self, full_name: str, brutto: float, proteins: float,
                 fats: float, carbohydrates: float, coef: float, type: str = None) -> None:
        """Инициализирует ингредиент.

        :param full_name: Полное наименование ингредиента.
        :param brutto: Масса брутто.
        :param proteins: Количество белков.
        :param fats: Количество жиров.
        :param carbohydrates: Количество углеводов.
        :param coef: Коэффициент пересчёта.
        """
        super().__init__(full_name=full_name, name=full_name)
        self.brutto = brutto
        self.proteins = proteins
        self.fats = fats
        self.carbohydrates = carbohydrates
        self.coef = coef
        if type is not None:
            self.type = type
        else:
            self.type = "product"

    @property
    def brutto(self) -> float:
        """Возвращает массу брутто."""
        return self.__brutto

    @brutto.setter
    def brutto(self, value: float) -> None:
        """Устанавливает массу брутто.

        :param value: Масса брутто (число, большее либо равное нулю).
        :raises arguments_exeption: Если значение не число.
        """
        validator.validate(value, (int, float), "brutto")
        self.__brutto = float(value)

    @property
    def proteins(self) -> float:
        """Возвращает количество белков."""
        return self.__proteins

    @proteins.setter
    def proteins(self, value: float) -> None:
        """Устанавливает количество белков.

        :param value: Количество белков.
        :raises arguments_exeption: Если значение не число.
        """
        validator.validate(value, (int, float), "proteins")
        self.__proteins = float(value)

    @property
    def fats(self) -> float:
        """Возвращает количество жиров."""
        return self.__fats

    @fats.setter
    def fats(self, value: float) -> None:
        """Устанавливает количество жиров.

        :param value: Количество жиров.
        :raises arguments_exeption: Если значение не число.
        """
        validator.validate(value, (int, float), "fats")
        self.__fats = float(value)

    @property
    def carbohydrates(self) -> float:
        """Возвращает количество углеводов."""
        return self.__carbohydrates

    @carbohydrates.setter
    def carbohydrates(self, value: float) -> None:
        """Устанавливает количество углеводов.

        :param value: Количество углеводов.
        :raises arguments_exeption: Если значение не число.
        """
        validator.validate(value, (int, float), "carbohydrates")
        self.__carbohydrates = float(value)

    @property
    def coef(self) -> float:
        """Возвращает коэффициент пересчёта."""
        return self.__coef

    @coef.setter
    def coef(self, value: float) -> None:
        """Устанавливает коэффициент пересчёта.

        :param value: Коэффициент пересчёта.
        :raises arguments_exeption: Если значение не число.
        """
        validator.validate(value, (int, float), "coef")
        self.__coef = float(value)
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.validator import validator
from Src.Core.nutrition_component import nutrition_component
from Src.Core.ingredient_types import ingredient_type
from Src.Core.exception import arguments_exeption


class ingredient_model(nomenclature_model, nutrition_component):
    """Модель ингредиента.

    Наследует полное наименование, группу и единицу измерения от
    номенклатуры. Дополнительно содержит брутто, пищевую ценность
    (белки, жиры, углеводы) и коэффициент пересчёта.

    Реализует интерфейс nutrition_component как «лист» дерева
    состава блюда: его методы calculate_* возвращают собственные
    значения без рекурсии.

    Создаётся через classmethod-конструкторы create / create_product /
    create_semi_finished / create_packaging.
    """

    __brutto: float = 0.0
    __proteins: float = 0.0
    __fats: float = 0.0
    __carbohydrates: float = 0.0
    __coef: float = 0.0

    def __init__(self, full_name: str, brutto: float, proteins: float,
                 fats: float, carbohydrates: float, coef: float,
                 item_type: str = None) -> None:
        """Инициализирует ингредиент.

        :param full_name: Полное наименование ингредиента.
        :param brutto: Масса брутто.
        :param proteins: Количество белков.
        :param fats: Количество жиров.
        :param carbohydrates: Количество углеводов.
        :param coef: Коэффициент пересчёта.
        :param item_type: Тип ингредиента (по умолчанию product).
        """
        super().__init__(
            full_name=full_name,
            name=full_name,
            item_type=item_type if item_type is not None else ingredient_type.PRODUCT,
        )
        self.brutto = brutto
        self.proteins = proteins
        self.fats = fats
        self.carbohydrates = carbohydrates
        self.coef = coef

    @classmethod
    def create(cls, full_name: str, brutto: float, proteins: float,
               fats: float, carbohydrates: float, coef: float,
               item_type: str = None) -> "ingredient_model":
        """Создаёт ингредиент по параметрам.

        :param full_name: Полное наименование ингредиента.
        :param brutto: Масса брутто.
        :param proteins: Количество белков.
        :param fats: Количество жиров.
        :param carbohydrates: Количество углеводов.
        :param coef: Коэффициент пересчёта.
        :param item_type: Тип ингредиента (product / semi_finished / packaging).
        :return: Созданный ингредиент.
        """
        return cls(
            full_name=full_name, brutto=brutto, proteins=proteins,
            fats=fats, carbohydrates=carbohydrates, coef=coef,
            item_type=item_type,
        )

    @classmethod
    def create_product(cls, full_name: str, brutto: float, proteins: float,
                       fats: float, carbohydrates: float,
                       coef: float) -> "ingredient_model":
        """Создаёт ингредиент-продукт.

        :return: Ингредиент с типом product.
        """
        return cls.create(
            full_name=full_name, brutto=brutto, proteins=proteins,
            fats=fats, carbohydrates=carbohydrates, coef=coef,
            item_type=ingredient_type.PRODUCT,
        )

    @classmethod
    def create_semi_finished(cls, full_name: str, brutto: float, proteins: float,
                             fats: float, carbohydrates: float,
                             coef: float) -> "ingredient_model":
        """Создаёт ингредиент-полуфабрикат.

        :return: Ингредиент с типом semi_finished.
        """
        return cls.create(
            full_name=full_name, brutto=brutto, proteins=proteins,
            fats=fats, carbohydrates=carbohydrates, coef=coef,
            item_type=ingredient_type.SEMI_FINISHED,
        )

    @classmethod
    def create_packaging(cls, full_name: str, brutto: float) -> "ingredient_model":
        """Создаёт упаковку.

        Упаковка не имеет пищевой ценности, поэтому БЖУ задаются
        нулями, а коэффициент пересчёта — единицей.

        :param full_name: Наименование упаковки.
        :param brutto: Масса упаковки.
        :return: Ингредиент с типом packaging.
        """
        return cls.create(
            full_name=full_name, brutto=brutto, proteins=0.0,
            fats=0.0, carbohydrates=0.0, coef=1.0,
            item_type=ingredient_type.PACKAGING,
        )

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


    def calculate_brutto(self, visited: set = None) -> float:
        """Возвращает брутто листового ингредиента.

        :param visited: Не используется (для совместимости с контрактом).
        :return: Масса брутто.
        """
        return self.brutto

    def calculate_netto(self, visited: set = None) -> float:
        """Возвращает нетто листового ингредиента.

        :param visited: Не используется (для совместимости с контрактом).
        :return: Масса нетто (брутто * коэффициент пересчёта).
        """
        return self.brutto * self.coef

    def calculate_nutrient(self, nutrient: str, visited: set = None) -> float:
        """Возвращает значение нутриента у листового ингредиента.

        Единая точка входа для рекурсивного обхода состава.
        У листового ингредиента БЖУ хранятся как атрибуты,
        поэтому visited не используется — он нужен только для
        совместимости с контрактом.

        :param nutrient: 'proteins' | 'fats' | 'carbohydrates'.
        :param visited: Не используется (для совместимости с контрактом).
        :return: Значение нутриента.
        :raises arguments_exeption: При неизвестном имени нутриента.
        """
        if nutrient not in self.NUTRIENTS:
            raise arguments_exeption(
                "nutrient",
                f"Неизвестный нутриент: {nutrient!r}. "
                f"Ожидается один из {self.NUTRIENTS}"
            )
        return getattr(self, nutrient)
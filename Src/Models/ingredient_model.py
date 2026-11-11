from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.validator import validator
from Src.Core.nutrition_component import nutrition_component
from Src.Core.ingredient_types import ingredient_type
from Src.Core.exception import arguments_exeption


class ingredient_model(nomenclature_model, nutrition_component):
    """Модель ингредиента."""

    __brutto: float = 0.0
    __proteins: float = 0.0
    __fats: float = 0.0
    __carbohydrates: float = 0.0
    __coef: float = 0.0

    _fields = (
        ("full_name", "primitive", None, str, ("name",)),
        ("brutto", "primitive", None, float),
        ("proteins", "primitive", None, float),
        ("fats", "primitive", None, float),
        ("carbohydrates", "primitive", None, float),
        ("coef", "primitive", None, float, (), False, 1.0),
        ("item_type", "primitive", None, str, ("type",), False, None),
    )

    def __init__(self, full_name: str, brutto: float, proteins: float,
                 fats: float, carbohydrates: float, coef: float,
                 item_type: str = None) -> None:
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
        return cls(
            full_name=full_name, brutto=brutto, proteins=proteins,
            fats=fats, carbohydrates=carbohydrates, coef=coef,
            item_type=item_type,
        )

    @classmethod
    def create_product(cls, full_name: str, brutto: float, proteins: float,
                       fats: float, carbohydrates: float,
                       coef: float) -> "ingredient_model":
        return cls.create(
            full_name=full_name, brutto=brutto, proteins=proteins,
            fats=fats, carbohydrates=carbohydrates, coef=coef,
            item_type=ingredient_type.PRODUCT,
        )

    @classmethod
    def create_semi_finished(cls, full_name: str, brutto: float, proteins: float,
                             fats: float, carbohydrates: float,
                             coef: float) -> "ingredient_model":
        return cls.create(
            full_name=full_name, brutto=brutto, proteins=proteins,
            fats=fats, carbohydrates=carbohydrates, coef=coef,
            item_type=ingredient_type.SEMI_FINISHED,
        )

    @classmethod
    def create_packaging(cls, full_name: str, brutto: float) -> "ingredient_model":
        return cls.create(
            full_name=full_name, brutto=brutto, proteins=0.0,
            fats=0.0, carbohydrates=0.0, coef=1.0,
            item_type=ingredient_type.PACKAGING,
        )

    @property
    def brutto(self) -> float:
        return self.__brutto

    @brutto.setter
    def brutto(self, value: float) -> None:
        validator.validate(value, (int, float), "brutto")
        self.__brutto = float(value)

    @property
    def proteins(self) -> float:
        return self.__proteins

    @proteins.setter
    def proteins(self, value: float) -> None:
        validator.validate(value, (int, float), "proteins")
        self.__proteins = float(value)

    @property
    def fats(self) -> float:
        return self.__fats

    @fats.setter
    def fats(self, value: float) -> None:
        validator.validate(value, (int, float), "fats")
        self.__fats = float(value)

    @property
    def carbohydrates(self) -> float:
        return self.__carbohydrates

    @carbohydrates.setter
    def carbohydrates(self, value: float) -> None:
        validator.validate(value, (int, float), "carbohydrates")
        self.__carbohydrates = float(value)

    @property
    def coef(self) -> float:
        return self.__coef

    @coef.setter
    def coef(self, value: float) -> None:
        validator.validate(value, (int, float), "coef")
        self.__coef = float(value)

    def calculate_brutto(self, visited: set = None) -> float:
        return self.brutto

    def calculate_netto(self, visited: set = None) -> float:
        return self.brutto * self.coef

    def calculate_nutrient(self, nutrient: str, visited: set = None) -> float:
        if nutrient not in self.NUTRIENTS:
            raise arguments_exeption(
                "nutrient",
                f"Неизвестный нутриент: {nutrient!r}. "
                f"Ожидается один из {self.NUTRIENTS}"
            )
        return getattr(self, nutrient)
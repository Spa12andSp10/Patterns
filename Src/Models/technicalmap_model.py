from Src.Core.entity_model import entity_model
from Src.Models.ingredient_model import ingredient_model
from Src.Core.validator import validator
from Src.Core.cooking_coefs import resolve_cooking_coef
from Src.Core.exception import arguments_exeption
from Src.Core.ingredient_types import ingredient_type
from Src.Core.nutrition_component import nutrition_component


class technicalmap_model(entity_model, nutrition_component):
    """Модель технологической карты блюда."""

    __ingredients: list
    __preparation_method: dict
    __description: str
    __time: str
    __with_package: bool = False
    __with_pf: bool = False

    _fields = (
        ("name", "primitive", None, str),
        ("description", "primitive", None, str),
        ("time", "primitive", None, str),
        ("preparation_method", "dict", None, None, (), False, {}),
        ("ingredients", "list", None, None, (), True, None),
    )

    def __init__(self, ingredients: list, preparation_method: dict,
                 description: str, time: str, name: str = ""):
        super().__init__()
        self.name = name
        self.ingredients = ingredients
        self.preparation_method = preparation_method
        self.description = description
        self.time = time
        self.refresh_flags()

    @classmethod
    def create(cls, ingredients: list, preparation_method: dict,
               description: str, time: str,
               name: str = "") -> "technicalmap_model":
        return cls(
            ingredients=ingredients,
            preparation_method=preparation_method,
            description=description,
            time=time,
            name=name,
        )

    @property
    def full_name(self) -> str:
        return self.name

    @property
    def ingredients(self) -> list:
        return self.__ingredients

    @ingredients.setter
    def ingredients(self, value: list) -> None:
        if not isinstance(value, list):
            raise arguments_exeption("ingredients", "Должен быть списком")
        for item in value:
            if not isinstance(item, nutrition_component):
                raise arguments_exeption(
                    "ingredients[]",
                    "Компонент должен реализовывать nutrition_component"
                )
        self.__ingredients = value
        self.refresh_flags()

    @property
    def preparation_method(self) -> dict:
        return self.__preparation_method

    @preparation_method.setter
    def preparation_method(self, value: dict) -> None:
        if not isinstance(value, dict):
            raise arguments_exeption("preparation_method", "Должен быть словарём")
        for key, method in value.items():
            validator.validate(key, str, "preparation_method.key")
            validator.validate(method, str, "preparation_method.value")
        self.__preparation_method = value

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, value: str) -> None:
        validator.validate(value, str, "description")
        self.__description = value

    @property
    def time(self) -> str:
        return self.__time

    @time.setter
    def time(self, value: str) -> None:
        validator.validate(value, str, "time")
        self.__time = value

    @property
    def with_package(self) -> bool:
        return self.__with_package

    @with_package.setter
    def with_package(self, value: bool) -> None:
        validator.validate(value, bool, "with_package")
        self.__with_package = value

    @property
    def with_pf(self) -> bool:
        return self.__with_pf

    def refresh_flags(self) -> None:
        self.__with_package = any(
            isinstance(i, ingredient_model)
            and i.item_type == ingredient_type.PACKAGING
            for i in self.__ingredients
        )
        self.__with_pf = any(
            isinstance(i, ingredient_model)
            and i.item_type == ingredient_type.SEMI_FINISHED
            for i in self.__ingredients
        )

    def _iter_components(self):
        for item in self.__ingredients:
            if (isinstance(item, ingredient_model)
                    and item.item_type == ingredient_type.PACKAGING
                    and not self.__with_package):
                continue
            yield item

    def _enter(self, visited: set) -> None:
        if self.unique_code in visited:
            raise arguments_exeption(
                "ingredients",
                f"Циклическая ссылка в технологической карте '{self.name}'"
            )
        visited.add(self.unique_code)

    def _resolve_method_for(self, item) -> str:
        if isinstance(item, ingredient_model):
            return self.__preparation_method.get(item.full_name, "")
        return ""

    def calculate_brutto(self, visited: set = None) -> float:
        if visited is None:
            visited = set()
        self._enter(visited)
        total = 0.0
        for item in self._iter_components():
            total += item.calculate_brutto(visited)
        visited.discard(self.unique_code)
        return total

    def calculate_netto(self, visited: set = None) -> float:
        if visited is None:
            visited = set()
        self._enter(visited)
        total = 0.0
        for item in self._iter_components():
            if (isinstance(item, ingredient_model)
                    and item.item_type == ingredient_type.PACKAGING):
                continue
            total += item.calculate_netto(visited)
        visited.discard(self.unique_code)
        return total

    def calculate_nutrient(self, nutrient: str, visited: set = None) -> float:
        if nutrient not in self.NUTRIENTS:
            raise arguments_exeption(
                "nutrient",
                f"Неизвестный нутриент: {nutrient!r}. "
                f"Ожидается один из {self.NUTRIENTS}"
            )

        if visited is None:
            visited = set()
        self._enter(visited)

        total = 0.0
        for item in self._iter_components():
            if isinstance(item, ingredient_model):
                if item.item_type == ingredient_type.PACKAGING:
                    continue
                method = self._resolve_method_for(item)
                coef = resolve_cooking_coef(method)
                base = item.calculate_nutrient(nutrient)
                total += base * coef[nutrient]
            else:
                total += item.calculate_nutrient(nutrient, visited)

        visited.discard(self.unique_code)
        return total

    def calculate_nutrition(self) -> dict:
        proteins = self.calculate_nutrient("proteins")
        fats = self.calculate_nutrient("fats")
        carbohydrates = self.calculate_nutrient("carbohydrates")

        return {
            "proteins": round(proteins, 2),
            "fats": round(fats, 2),
            "carbohydrates": round(carbohydrates, 2),
            "calories": round(proteins * 4 + fats * 9 + carbohydrates * 4, 2),
        }

    def add_ingredient(self, ingredient) -> None:
        if not isinstance(ingredient, nutrition_component):
            raise arguments_exeption(
                "ingredient",
                "Компонент должен реализовывать nutrition_component"
            )
        self.__ingredients.append(ingredient)
        self.refresh_flags()

    def remove_ingredient(self, full_name: str) -> bool:
        before = len(self.__ingredients)
        self.__ingredients = [
            i for i in self.__ingredients if i.full_name != full_name
        ]
        self.refresh_flags()
        return len(self.__ingredients) != before
from Src.Core.entity_model import entity_model
from Src.Models.ingredient_model import ingredient_model
from Src.Core.validator import validator
from Src.Core.cooking_coefs import resolve_cooking_coef, DEFAULT_COOKING_COEF
from Src.Core.exception import arguments_exeption


class technicalmap_model(entity_model):
    """Модель технологической карты блюда.

    Содержит список ингредиентов, способ приготовления каждого
    ингредиента в виде словаря {наименование: способ}, текстовое
    описание (инструкцию для повара) и время приготовления.
    Позволяет рассчитать массу брутто/нетто и суммарные БЖУ
    с учётом тепловой обработки.
    """

    __ingredients: list[ingredient_model]
    __preparation_method: dict[str, str]
    __description: str
    __time: str
    __with_package: bool = False
    __with_pf: bool = False
    

    def __init__(self, ingredients: list, preparation_method: dict[str, str],
                 description: str, time: str, name: str = ""):
        """Инициализирует технологическую карту.

        :param ingredients: Список ингредиентов блюда.
        :param preparation_method: Словарь {наименование ингредиента: способ приготовления}.
        :param description: Текстовая инструкция для повара.
        :param time: Время приготовления.
        :param name: Краткое наименование блюда.
        """
        super().__init__()

        self.name = name
        self.ingredients = ingredients
        self.preparation_method = preparation_method
        self.description = description
        self.time = time
        self.refresh_flags()

    @property
    def ingredients(self) -> list[ingredient_model]:
        """Возвращает список ингредиентов блюда."""
        return self.__ingredients

    @ingredients.setter
    def ingredients(self, value: list[ingredient_model]) -> None:
        """Устанавливает список ингредиентов блюда.

        :param value: Список ингредиентов.
        :raises arguments_exeption: Если значение не список.
        :raises arguments_exeption: Если элемент списка не ingredient_model.
        """
        if not isinstance(value, list):
            raise arguments_exeption("ingredients", "Должен быть списком")
        for item in value:
            validator.validate(item, ingredient_model, "ingredients[]")
        self.__ingredients = value

    @property
    def preparation_method(self) -> dict[str, str]:
        """Возвращает словарь способов приготовления ингредиентов."""
        return self.__preparation_method

    @preparation_method.setter
    def preparation_method(self, value: dict[str, str]) -> None:
        """Устанавливает словарь способов приготовления ингредиентов.

        :param value: Словарь {наименование ингредиента: способ приготовления}.
        :raises arguments_exeption: Если значение не словарь.
        :raises arguments_exeption: Если ключ или значение не строка.
        """
        if not isinstance(value, dict):
            raise arguments_exeption("preparation_method", "Должен быть словарём")
        for key, method in value.items():
            validator.validate(key, str, "preparation_method.key")
            validator.validate(method, str, "preparation_method.value")
        self.__preparation_method = value

    @property
    def description(self) -> str:
        """Возвращает текстовую инструкцию для повара."""
        return self.__description

    @description.setter
    def description(self, value: str) -> None:
        """Устанавливает текстовую инструкцию для повара.

        :param value: Текстовая инструкция.
        :raises arguments_exeption: Если значение не строка или пустое.
        """
        validator.validate(value, str, "description")
        self.__description = value

    @property
    def time(self) -> str:
        """Возвращает время приготовления."""
        return self.__time

    @time.setter
    def time(self, value: str) -> None:
        """Устанавливает время приготовления.

        :param value: Время приготовления.
        :raises arguments_exeption: Если значение не строка или пустое.
        """
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
        """Пересчитывает флаги по составу ингредиентов.

        Устанавливает with_package = True, если среди ингредиентов
        есть упаковка (type == "packaging"), и with_pf = True, если
        есть полуфабрикат (type == "semi_finished").
        """
        self.__with_package = any(
            getattr(i, "type", "") == "packaging" for i in self.__ingredients
        )
        self.__with_pf = any(
            getattr(i, "type", "") == "semi_finished" for i in self.__ingredients
        )

    def calculate_brutto(self) -> float:
        """Рассчитывает суммарное брутто всех ингредиентов.

        Упаковка учитывается, если флаг with_package установлен.

        :return: Суммарная масса брутто.
        """
        total = 0.0
        for ing in self.__ingredients:
            ing_type = getattr(ing, "type", "")
            if ing_type == "packaging" and not self.__with_package:
                continue
            total += ing.brutto
        return total

    def calculate_netto(self) -> float:
        """Рассчитывает суммарное нетто всех ингредиентов.

        Упаковка не учитывается. Нетто каждого ингредиента —
        это брутто * коэффициент пересчёта.

        :return: Суммарная масса нетто.
        """
        total = 0.0
        for ing in self.__ingredients:
            ing_type = getattr(ing, "type", "")
            if ing_type == "packaging":
                continue
            total += ing.brutto * ing.coef
        return total

    def calculate_proteins(self) -> float:
        """Рассчитывает суммарные белки с учётом способа приготовления.

        :return: Суммарное количество белков.
        """
        total = 0.0
        for ing in self.__ingredients:
            method = self.__preparation_method.get(ing.full_name, "")
            coef = resolve_cooking_coef(method)
            total += ing.proteins * coef["proteins"]
        return total

    def calculate_fats(self) -> float:
        """Рассчитывает суммарные жиры с учётом способа приготовления.

        :return: Суммарное количество жиров.
        """
        total = 0.0
        for ing in self.__ingredients:
            method = self.__preparation_method.get(ing.full_name, "")
            coef = resolve_cooking_coef(method)
            total += ing.fats * coef["fats"]
        return total

    def calculate_carbohydrates(self) -> float:
        """Рассчитывает суммарные углеводы с учётом способа приготовления.

        :return: Суммарное количество углеводов.
        """
        total = 0.0
        for ing in self.__ingredients:
            method = self.__preparation_method.get(ing.full_name, "")
            coef = resolve_cooking_coef(method)
            total += ing.carbohydrates * coef["carbohydrates"]
        return total

    def calculate_nutrition(self) -> dict:
        """Рассчитывает суммарные БЖУ и калорийность блюда.

        :return: Словарь с ключами proteins/fats/carbohydrates/calories.
        """
        proteins = self.calculate_proteins()
        fats = self.calculate_fats()
        carbohydrates = self.calculate_carbohydrates()

        return {
            "proteins": round(proteins, 2),
            "fats": round(fats, 2),
            "carbohydrates": round(carbohydrates, 2),
            "calories": round(proteins * 4 + fats * 9 + carbohydrates * 4, 2),
        }


    def add_ingredient(self, ingredient: ingredient_model) -> None:
        """Добавляет ингредиент и обновляет флаги.

        :param ingredient: Добавляемый ингредиент.
        :raises arguments_exeption: Если значение не ingredient_model.
        """
        validator.validate(ingredient, ingredient_model, "ingredient")
        self.__ingredients.append(ingredient)
        self.refresh_flags()

    def remove_ingredient(self, full_name: str) -> bool:
        """Удаляет ингредиент по полному наименованию.

        :param full_name: Полное наименование ингредиента.
        :return: True, если что-то удалено, иначе False.
        """
        before = len(self.__ingredients)
        self.__ingredients = [
            i for i in self.__ingredients if i.full_name != full_name
        ]
        self.refresh_flags()
        return len(self.__ingredients) != before
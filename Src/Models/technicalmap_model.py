from Src.Core.entity_model import entity_model
from Src.Models.ingredient_model import ingredient_model
from Src.Core.validator import validator
from Src.Core.cooking_coefs import resolve_cooking_coef
from Src.Core.exception import arguments_exeption
from Src.Core.ingredient_types import ingredient_type
from Src.Core.nutrition_component import nutrition_component


class technicalmap_model(entity_model, nutrition_component):
    """Модель технологической карты блюда.

    Содержит список компонентов (ингредиентов и/или вложенных
    технологических карт — «блюдо в блюде»), способ приготовления
    каждого ингредиента в виде словаря {наименование: способ},
    текстовое описание (инструкцию для повара) и время приготовления.

    Реализует интерфейс nutrition_component: рекурсивно обходит
    состав, поддерживает вложенные блюда и защищается от циклов
    через множество visited (по unique_code).

    Создаётся через classmethod-конструктор create.
    """

    __ingredients: list
    __preparation_method: dict
    __description: str
    __time: str
    __with_package: bool = False
    __with_pf: bool = False

    def __init__(self, ingredients: list, preparation_method: dict,
                 description: str, time: str, name: str = ""):
        """Инициализирует технологическую карту.

        :param ingredients: Список компонентов (ingredient_model
            или вложенные technicalmap_model).
        :param preparation_method: Словарь {наименование ингредиента: способ}.
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

    @classmethod
    def create(cls, ingredients: list, preparation_method: dict,
               description: str, time: str,
               name: str = "") -> "technicalmap_model":
        """Создаёт технологическую карту по составу и параметрам.

        :param ingredients: Список компонентов (ингредиенты и/или
            вложенные технологические карты).
        :param preparation_method: Словарь {наименование: способ}.
        :param description: Текстовая инструкция.
        :param time: Время приготовления.
        :param name: Краткое наименование блюда.
        :return: Созданная технологическая карта.
        """
        return cls(
            ingredients=ingredients,
            preparation_method=preparation_method,
            description=description,
            time=time,
            name=name,
        )

    @property
    def full_name(self) -> str:
        """Возвращает полное наименование блюда.

        У технологической карты отдельного полного наименования нет —
        возвращаем краткое name, чтобы удовлетворить контракт
        nutrition_component.

        :return: Наименование блюда.
        """
        return self.name

    @property
    def ingredients(self) -> list:
        """Возвращает список компонентов блюда."""
        return self.__ingredients

    @ingredients.setter
    def ingredients(self, value: list) -> None:
        """Устанавливает список компонентов блюда.

        Каждый компонент должен реализовывать nutrition_component —
        это либо ingredient_model, либо technicalmap_model.

        :param value: Список компонентов.
        :raises arguments_exeption: Если значение не список.
        :raises arguments_exeption: Если элемент не nutrition_component.
        """
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
        """Возвращает словарь способов приготовления ингредиентов."""
        return self.__preparation_method

    @preparation_method.setter
    def preparation_method(self, value: dict) -> None:
        """Устанавливает словарь способов приготовления.

        Способы задаются только для непосредственных листовых
        ингредиентов этой карты. Вложенные блюда знают свои способы
        сами.

        :param value: Словарь {наименование ингредиента: способ}.
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
        """Возвращает флаг наличия упаковки в составе."""
        return self.__with_package

    @with_package.setter
    def with_package(self, value: bool) -> None:
        """Устанавливает флаг наличия упаковки.

        :param value: Значение флага.
        :raises arguments_exeption: Если значение не bool.
        """
        validator.validate(value, bool, "with_package")
        self.__with_package = value

    @property
    def with_pf(self) -> bool:
        """Возвращает флаг наличия полуфабрикатов в составе."""
        return self.__with_pf

    def refresh_flags(self) -> None:
        """Пересчитывает флаги по составу компонентов.

        Устанавливает with_package = True, если среди компонентов
        есть упаковка (item_type == ingredient_type.PACKAGING), и
        with_pf = True, если есть полуфабрикат
        (item_type == ingredient_type.SEMI_FINISHED).
        """
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
        """Итератор по компонентам с фильтрацией упаковки.

        Упаковка как самостоятельный компонент пропускается, если
        флаг with_package не установлен.

        :return: Итератор по компонентам.
        """
        for item in self.__ingredients:
            if (isinstance(item, ingredient_model)
                    and item.item_type == ingredient_type.PACKAGING
                    and not self.__with_package):
                continue
            yield item

    def _enter(self, visited: set) -> None:
        """Проверяет и регистрирует вход в карту при обходе.

        :param visited: Множество unique_code посещённых карт.
        :raises arguments_exeption: При обнаружении циклической ссылки.
        """
        if self.unique_code in visited:
            raise arguments_exeption(
                "ingredients",
                f"Циклическая ссылка в технологической карте '{self.name}'"
            )
        visited.add(self.unique_code)

    def _resolve_method_for(self, item) -> str:
        """Возвращает способ приготовления для компонента.

        :param item: Компонент состава.
        :return: Способ приготовления или пустая строка.
        """
        if isinstance(item, ingredient_model):
            return self.__preparation_method.get(item.full_name, "")
        return ""

    # --- Реализация контракта nutrition_component ---

    def calculate_brutto(self, visited: set = None) -> float:
        """Рекурсивно считает брутто блюда, включая вложенные блюда.

        :param visited: Множество unique_code посещённых карт.
        :return: Суммарное брутто.
        """
        if visited is None:
            visited = set()
        self._enter(visited)

        total = 0.0
        for item in self._iter_components():
            total += item.calculate_brutto(visited)

        visited.discard(self.unique_code)
        return total

    def calculate_netto(self, visited: set = None) -> float:
        """Рекурсивно считает нетто блюда, включая вложенные блюда.

        :param visited: Множество unique_code посещённых карт.
        :return: Суммарное нетто.
        """
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
        """Рекурсивно считает суммарное значение нутриента по составу.

        Единая точка входа для рекурсивного обхода. Для листовых
        ингредиентов учитывает способ приготовления через
        resolve_cooking_coef, для вложенных карт — делегирует
        рекурсивный вызов.

        :param nutrient: 'proteins' | 'fats' | 'carbohydrates'.
        :param visited: Множество unique_code посещённых карт.
        :return: Суммарное значение нутриента.
        :raises arguments_exeption: При неизвестном имени нутриента.
        :raises arguments_exeption: При обнаружении циклической ссылки.
        """
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
        """Рассчитывает суммарные БЖУ и калорийность блюда.

        :return: Словарь с ключами proteins/fats/carbohydrates/calories.
        """
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
        """Добавляет компонент и обновляет флаги.

        :param ingredient: Компонент состава.
        :raises arguments_exeption: Если элемент не nutrition_component.
        """
        if not isinstance(ingredient, nutrition_component):
            raise arguments_exeption(
                "ingredient",
                "Компонент должен реализовывать nutrition_component"
            )
        self.__ingredients.append(ingredient)
        self.refresh_flags()

    def remove_ingredient(self, full_name: str) -> bool:
        """Удаляет компонент по полному наименованию.

        :param full_name: Полное наименование компонента.
        :return: True, если компонент был удалён.
        """
        before = len(self.__ingredients)
        self.__ingredients = [
            i for i in self.__ingredients if i.full_name != full_name
        ]
        self.refresh_flags()
        return len(self.__ingredients) != before
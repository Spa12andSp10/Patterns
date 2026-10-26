import json

from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exeption
from Src.Core.ingredient_types import ingredient_type
from Src.Logics.convert_factory import convert_factory
from Src.Logics.settings_manager import settings_manager
from Src.Models.group_model import group_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.technicalmap_model import technicalmap_model
from Src.Models.warehouse_model import warehouse_model
from Src.Core.abstract_convertor import abstract_convertor


class storage_manager(abstract_manager):
    """Singleton-хранилище доменных справочников.

    Хранит группы номенклатуры, единицы измерения, номенклатуру,
    склады и технологические карты (рецепты). Эталонные данные
    формируются при первом старте из файла storage_data.json.

    Создание доменных моделей делегируется classmethod-конструкторам
    самих моделей (group_model.create, ingredient_model.create и т.д.).
    """

    __default_data_file = "storage_data.json"

    _groups: list = []
    _nomenclature: list = []
    _warehouse: list = []
    _ranges: list = []
    _recipes: list = []

    def __init__(self):
        """Инициализирует пустые списки справочников (однократно)."""
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._groups = []
            self._nomenclature = []
            self._warehouse = []
            self._ranges = []
            self._recipes = []
            self._is_loaded = False
            self._data = {}

    def __new__(cls):
        """Реализует шаблон Singleton.

        :return: Единственный экземпляр storage_manager.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(storage_manager, cls).__new__(cls)
        return cls.instance

    @staticmethod
    def _read_json(file_name: str) -> dict:
        """Читает JSON-файл и возвращает словарь.

        :param file_name: Путь к файлу.
        :return: Содержимое файла как словарь.
        :raises FileNotFoundError: Если файл не найден.
        :raises json.JSONDecodeError: Если JSON некорректен.
        """
        with open(file_name, "r", encoding="utf-8") as file:
            return json.load(file)

    def load(self, file_name: str = "") -> None:
        """Загружает справочники из эталонного JSON-файла.

        Если настройки ещё не загружены — сначала загружает их
        через settings_manager.

        :param file_name: Путь к файлу эталонных данных.
            Если пусто — используется storage_data.json.
        """
        manager = settings_manager()
        if not manager.is_loaded:
            manager.load()

        inner_file_name = file_name if file_name != "" else self.__default_data_file
        try:
            self._data = self._read_json(inner_file_name)
        except (FileNotFoundError, json.JSONDecodeError):
            self._is_loaded = False
            return

        self._is_loaded = self.convert()


    def save(self, file_name: str = "") -> bool:
        """Сохраняет «сырые» данные self._data обратно в JSON-файл.

        :param file_name: Путь к файлу. Если пусто — storage_data.json.
        :return: True, если запись прошла успешно, иначе False.
        """
        inner_file_name = file_name if file_name != "" else self.__default_data_file
        if not self._data:
            return False
        try:
            with open(inner_file_name, "w", encoding="utf-8") as file:
                json.dump(self._data, file, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False

    def save_models(self, file_name: str = "") -> bool:
        """Сохраняет текущие доменные модели в JSON-файл.

        Собирает секции groups/ranges/nomenclature/warehouse/recipes
        из списков моделей и сериализует через convert_factory.

        :param file_name: Путь к файлу. Если пусто — storage_data.json.
        :return: True, если запись прошла успешно, иначе False.
        """
        inner_file_name = file_name if file_name != "" else self.__default_data_file
        walker = convert_factory().create()

        payload = {
            "groups": [walker.convert(g) for g in self._groups],
            "ranges": [walker.convert(r) for r in self._ranges],
            "nomenclature": [walker.convert(n) for n in self._nomenclature],
            "warehouse": [walker.convert(w) for w in self._warehouse],
            "recipes": [walker.convert(r) for r in self._recipes],
        }

        try:
            data = json.loads(abstract_convertor.to_json(payload))

            with open(inner_file_name, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            self._data = data
            return True
        except OSError:
            return False

    def _convert_ranges(self, data: list) -> None:
        """Преобразует список единиц измерения из JSON.

        Сначала создаёт все единицы без базовой, затем вторым
        проходом связывает их по имени base.

        :param data: Список словарей с описанием единиц измерения.
        """
        by_name: dict = {}

        for item in data:
            param = range_model.create(
                name=item["name"],
                conversion_factor=item.get(
                    "conversion_factor",
                    item.get("conversation_factor", 1),
                ),
                base=None,
            )
            by_name[param.name] = param
            self._ranges.append(param)

        for item in data:
            base_name = item.get("base")
            if base_name and item["name"] in by_name and base_name in by_name:
                by_name[item["name"]].base = by_name[base_name]

    def _convert_groups(self, data: list) -> None:
        """Преобразует список групп номенклатуры из JSON.

        :param data: Список словарей с описанием групп.
        """
        for item in data:
            self._groups.append(group_model.create(name=item["name"]))

    def _find_nomeclature_name(self, name: str):
        """Ищет группу номенклатуры по наименованию.

        :param name: Наименование группы.
        :return: Найденная group_model или None.
        """
        for i in self._groups:
            if i.name == name:
                return i
        return None

    def _find_nomeclature_range(self, name: str):
        """Ищет единицу измерения по наименованию.

        :param name: Наименование единицы измерения.
        :return: Найденная range_model или None.
        """
        for i in self._ranges:
            if i.name == name:
                return i
        return None

    def _convert_nomenclature(self, data: list) -> None:
        """Преобразует список номенклатуры из JSON.

        :param data: Список словарей с описанием номенклатуры.
        :raises arguments_exeption: Если группа или единица не найдены.
        """
        for item in data:
            gr = self._find_nomeclature_name(item["group"])
            rn = self._find_nomeclature_range(item["range"])
            if gr is None or rn is None:
                raise arguments_exeption(
                    "nomenclature",
                    f"Не найдена группа/единица для '{item['name']}'"
                )
            self._nomenclature.append(
                nomenclature_model.create(
                    full_name=item["full_name"],
                    name=item["name"],
                    group=gr,
                    range=rn,
                    item_type=item.get("item_type", item.get("type", "")),
                )
            )

    def _convert_warehouse(self, data: list) -> None:
        """Преобразует список складов из JSON.

        :param data: Список словарей с описанием складов.
        """
        for item in data:
            self._warehouse.append(
                warehouse_model.create(
                    name=item["name"],
                    address=item["address"],
                )
            )

    def _convert_recipes(self, data: list) -> None:
        """Преобразует список рецептов из JSON.

        Каждый элемент — словарь с полями:
          - name: наименование блюда;
          - time: время приготовления;
          - description: инструкция;
          - ingredients: список ингредиентов;
          - preparation_method: {наименование: способ}.

        Ингредиенты создаются через ingredient_model.create,
        сама карта — через technicalmap_model.create.

        :param data: Список словарей с описанием рецептов.
        """
        for item in data:
            ingredients = [
                ingredient_model.create(
                    full_name=ing["full_name"],
                    brutto=ing["brutto"],
                    proteins=ing["proteins"],
                    fats=ing["fats"],
                    carbohydrates=ing["carbohydrates"],
                    coef=ing.get("coef", 1.0),
                    item_type=ing.get("item_type", ing.get("type", ingredient_type.PRODUCT)),
                )
                for ing in item.get("ingredients", [])
            ]

            self._recipes.append(
                technicalmap_model.create(
                    ingredients=ingredients,
                    preparation_method=item.get("preparation_method", {}),
                    description=item["description"],
                    time=item["time"],
                    name=item["name"],
                )
            )

    def convert(self) -> bool:
        """Преобразует «сырые» данные JSON в доменные модели.

        Очищает текущие списки и последовательно наполняет их
        из соответствующих секций self._data.

        :return: True, если преобразование прошло успешно.
        """
        self._groups = []
        self._nomenclature = []
        self._warehouse = []
        self._ranges = []
        self._recipes = []

        self._convert_ranges(self._data.get("ranges", []))
        self._convert_groups(self._data.get("groups", []))
        self._convert_nomenclature(self._data.get("nomenclature", []))
        self._convert_warehouse(self._data.get("warehouse", []))
        self._convert_recipes(self._data.get("recipes", []))

        return True

    def first_start(self, file_name: str = "") -> bool:
        """Формирует первичные данные при первом старте.

        Если флаг first_launch_flag установлен — загружает эталонные
        данные, дозаполняет справочники через конвертеры и сбрасывает
        флаг. Иначе ничего не делает.

        :param file_name: Путь к файлу эталонных данных.
        :return: True, если данные были сформированы, иначе False.
        """
        manager = settings_manager()
        if not manager.is_loaded:
            manager.load()

        if not manager.settings.first_launch_flag:
            return False

        inner_file_name = file_name if file_name != "" else self.__default_data_file
        try:
            self._data = self._read_json(inner_file_name)
        except (FileNotFoundError, json.JSONDecodeError):
            self._data = {}

        self._is_loaded = self.convert()

        manager.settings.first_launch_flag = False
        manager.save()

        return self._is_loaded


    @property
    def groups(self) -> list:
        """Возвращает список групп номенклатуры."""
        return self._groups

    @property
    def ranges(self) -> list:
        """Возвращает список единиц измерения."""
        return self._ranges

    @property
    def nomenclatures(self) -> list:
        """Возвращает список номенклатуры."""
        return self._nomenclature

    @property
    def warehouses(self) -> list:
        """Возвращает список складов."""
        return self._warehouse

    @property
    def recipes(self) -> list:
        """Возвращает список технологических карт (рецептов)."""
        return self._recipes


    @staticmethod
    def _is_unique(items: list, candidate) -> bool:
        """Проверяет уникальность элемента по имени.

        Если у candidate есть name — сравнивает по name,
        иначе — по равенству объектов.

        :param items: Список уже добавленных элементов.
        :param candidate: Проверяемый элемент.
        :return: True, если дубликата нет, иначе False.
        """
        name = getattr(candidate, "name", None)
        if name is not None:
            return all(getattr(item, "name", None) != name for item in items)
        return all(item != candidate for item in items)

    def add_group(self, value: group_model) -> bool:
        """Добавляет группу, если её ещё нет.

        :param value: Добавляемая группа.
        :return: True, если группа добавлена, иначе False.
        """
        if self._is_unique(self._groups, value):
            self._groups.append(value)
            return True
        return False

    def add_range(self, value: range_model) -> bool:
        """Добавляет единицу измерения, если её ещё нет.

        :param value: Добавляемая единица измерения.
        :return: True, если единица добавлена, иначе False.
        """
        if self._is_unique(self._ranges, value):
            self._ranges.append(value)
            return True
        return False

    def add_nomenclature(self, value: nomenclature_model) -> bool:
        """Добавляет номенклатуру, если её ещё нет.

        :param value: Добавляемая номенклатура.
        :return: True, если номенклатура добавлена, иначе False.
        """
        if self._is_unique(self._nomenclature, value):
            self._nomenclature.append(value)
            return True
        return False

    def add_warehouse(self, value: warehouse_model) -> bool:
        """Добавляет склад, если его ещё нет.

        :param value: Добавляемый склад.
        :return: True, если склад добавлен, иначе False.
        """
        if self._is_unique(self._warehouse, value):
            self._warehouse.append(value)
            return True
        return False

    def add_recipe(self, value) -> bool:
        """Добавляет рецепт, если его ещё нет (по имени).

        :param value: Добавляемая технологическая карта.
        :return: True, если рецепт добавлен, иначе False.
        """
        if self._is_unique(self._recipes, value):
            self._recipes.append(value)
            return True
        return False

    def load_default_ranges(self) -> None:
        """Наполняет справочник единиц эталонными значениями.

        Использует classmethod-конструкторы range_model:
        create_gram, create_kilogram, create_tonna.
        """
        gram = range_model.create_gram()
        self.add_range(gram)

        kilogram = range_model.create_kilogram(base=gram)
        self.add_range(kilogram)

        tonna = range_model.create_tonna(base=kilogram)
        self.add_range(tonna)
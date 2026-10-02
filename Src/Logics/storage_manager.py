from Src.Core.abstract_manager import abstract_manager
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model
from Src.Logics.settings_manager import settings_manager
from Src.Core.exception import arguments_exeption


class storage_manager(abstract_manager):
    """Singleton-хранилище доменных справочников.

    Хранит группы номенклатуры, единицы измерения, номенклатуру
    и склады. Данные загружаются из JSON через settings_manager.
    """

    _groups: list = []
    _nomenclature: list = []
    _warehouse: list = []
    _ranges: list = []

    def __init__(self):
        """Инициализирует пустые списки справочников (однократно)."""
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._groups = []
            self._nomenclature = []
            self._warehouse = []
            self._ranges = []
            self._is_loaded = False
            self._data = {}

    def __new__(cls):
        """Реализует шаблон Singleton.

        :return: Единственный экземпляр storage_manager.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(storage_manager, cls).__new__(cls)
        return cls.instance

    def load(self, file_name: str = "") -> None:
        """Загружает справочники из JSON-файла.

        Если настройки ещё не загружены — сначала загружает их
        через settings_manager.

        :param file_name: Путь к файлу настроек.
        """
        manager = settings_manager()
        if not manager._is_loaded:
            manager.load(file_name)
        self._data = manager.data
        self._is_loaded = self.convert()

    def _convert_ranges(self, data: list) -> None:
        """Преобразует список единиц измерения из JSON.

        Создаёт все range_model, затем связывает производные
        единицы с базовыми через поле base.

        :param data: Список словарей с описанием единиц измерения.
        """
        by_name: dict = {}

        for item in data:
            param = range_model(
                name=item["name"],
                conversion_factor=item.get("conversion_factor",
                                          item.get("conversation_factor", 1)),
                base=None
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
            self._groups.append(group_model(name=item["name"]))

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

        Для каждой записи ищет связанную группу и единицу измерения.
        Если связь не найдена — бросает arguments_exeption.

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
                nomenclature_model(
                    full_name=item["full_name"],
                    name=item["name"],
                    group=gr,
                    range=rn,
                )
            )

    def _convert_warehouse(self, data: list) -> None:
        """Преобразует список складов из JSON.

        :param data: Список словарей с описанием складов.
        """
        for item in data:
            self._warehouse.append(
                warehouse_model(name=item["name"], address=item["address"])
            )

    def convert(self) -> bool:
        """Преобразует «сырые» данные JSON в доменные модели.

        Обнуляет списки и последовательно вызывает конвертеры
        для диапазонов, групп, номенклатуры и складов.

        :return: True, если преобразование прошло успешно.
        """
        self._groups = []
        self._nomenclature = []
        self._warehouse = []
        self._ranges = []

        self._convert_ranges(self._data.get("ranges", []))
        self._convert_groups(self._data.get("groups", []))
        self._convert_nomenclature(self._data.get("nomenclature", []))
        self._convert_warehouse(self._data.get("warehouse", []))

        return True

    def first_start(self, file_name: str = "") -> bool:
        """Формирует первичные данные при первом старте.

        Если флаг first_launch_flag установлен — загружает данные
        и сбрасывает флаг. Иначе ничего не делает.

        :param file_name: Путь к файлу настроек.
        :return: True, если данные были сформированы, иначе False.
        """
        manager = settings_manager()
        if not manager._is_loaded:
            manager.load(file_name)

        if not manager.settings.first_launch_flag:
            return False

        self._data = manager.data
        self._is_loaded = self.convert()

        manager.settings.first_launch_flag = False
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
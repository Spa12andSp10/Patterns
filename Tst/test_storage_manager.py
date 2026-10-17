import pytest

from pathlib import Path
from Src.Logics.storage_manager import storage_manager
from Src.Logics.settings_manager import settings_manager
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.warehouse_model import warehouse_model


def _settings_path() -> str:
    """Путь к settings.json в папке Tst (рядом с тестом)."""
    return str(Path(__file__).resolve().parent / "settings.json")

def _storage_path() -> str:
    """Путь к storage_data.json (эталонные данные)."""
    return str(Path(__file__).resolve().parent / "storage_data.json")


@pytest.fixture(autouse=True)
def reset_storage():
    sm = storage_manager()
    sm._groups = []
    sm._ranges = []
    sm._nomenclature = []
    sm._warehouse = []
    sm._recipes = []
    sm._is_loaded = False
    sm._data = {}
    yield


def test_valid_result_storage_manager_singleton():
    """
    Проверяет работу шаблона Singleton для storage_manager.
    Ожидаемый результат: два вызова storage_manager() возвращают один и тот же объект.
    """
    # Подготовка
    s1 = storage_manager()

    # Действие
    s2 = storage_manager()

    # Проверки
    assert s1 is s2


def test_valid_result_storage_manager_load_success():
    """
    Проверяет успешную загрузку данных из settings.json.
    Ожидаемый результат: после вызова load() флаг is_loaded становится True.
    """
    # Подготовка
    sm = storage_manager()

    # Действие
    sm.load(_storage_path())

    # Проверки
    assert sm.is_loaded is True


def test_valid_result_storage_manager_groups_loaded():
    """
    Проверяет, что группы номенклатуры загружены из JSON.
    Ожидаемый результат: список groups содержит 5 элемента, включая
    «Молочная продукция» и «Мясная продукция».
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())

    # Действие
    names = [g.name for g in sm.groups]

    # Проверки
    assert len(sm.groups) == 5
    assert "Dairy products" in names
    assert "Meat products" in names


def test_valid_result_storage_manager_ranges_loaded():
    """
    Проверяет, что единицы измерения загружены из JSON.
    Ожидаемый результат: список ranges содержит 5 элемента, включая
    «грамм» и «килограмм».
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())

    # Действие
    names = [r.name for r in sm.ranges]

    # Проверки
    assert len(sm.ranges) == 4
    assert "gram" in names
    assert "kilogram" in names


def test_valid_result_storage_manager_range_base_linked():
    """
    Проверяет, что производная единица измерения ссылается на базовую.
    Ожидаемый результат: у «килограмм» base указывает на «грамм»,
    conversion_factor равен 1000.0.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())

    # Действие
    kg = next(r for r in sm.ranges if r.name == "kilogram")

    # Проверки
    assert kg.base is not None
    assert kg.base.name == "gram"
    assert kg.conversion_factor == 1000.0


def test_valid_result_storage_manager_nomenclatures_loaded():
    """
    Проверяет, что номенклатура загружена из JSON.
    Ожидаемый результат: список nomenclatures содержит 4 элемента, включая
    «Молоко» и «Яблоко».
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())

    # Действие
    names = [n.name for n in sm.nomenclatures]

    # Проверки
    assert len(sm.nomenclatures) == 5
    assert "Milk" in names
    assert "Apple" in names


def test_valid_result_storage_manager_nomenclature_links():
    """
    Проверяет, что номенклатура ссылается на существующие группы и единицы измерения.
    Ожидаемый результат: у «Молоко» group = «Молочная продукция», range = «литр»,
    full_name = «Молоко пастеризованное 3.2%».
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())

    # Действие
    milk = next(n for n in sm.nomenclatures if n.name == "Milk")

    # Проверки
    assert milk.group.name == "Dairy products"
    assert milk.range.name == "liter"
    assert milk.full_name == "Pasteurized milk 3.2%"


def test_valid_result_storage_manager_warehouses_loaded():
    """
    Проверяет, что склады загружены из JSON.
    Ожидаемый результат: список warehouses содержит 2 элемента: «Основной склад»
    и «Вспомогательный склад».
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())

    # Действие
    names = [w.name for w in sm.warehouses]

    # Проверки
    assert len(sm.warehouses) == 2
    assert "Main warehouse" in names
    assert "Auxiliary warehouse" in names


def test_invalid_result_storage_manager_unique_ranges():
    """
    Проверяет запрет добавления дубликата единицы измерения.
    Ожидаемый результат: повторное добавление того же объекта не увеличивает
    размер списка ranges.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    before = len(sm.ranges)
    existing = sm.ranges[0]

    # Действие
    sm.add_range(existing)

    # Проверки
    assert len(sm.ranges) == before


def test_invalid_result_storage_manager_unique_groups():
    """
    Проверяет запрет добавления дубликата группы.
    Ожидаемый результат: повторное добавление того же объекта не увеличивает
    размер списка groups.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    before = len(sm.groups)

    # Действие
    sm.add_group(sm.groups[0])

    # Проверки
    assert len(sm.groups) == before


def test_invalid_result_storage_manager_unique_nomenclatures():
    """
    Проверяет запрет добавления дубликата номенклатуры.
    Ожидаемый результат: повторное добавление того же объекта не увеличивает
    размер списка nomenclatures.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    before = len(sm.nomenclatures)

    # Действие
    sm.add_nomenclature(sm.nomenclatures[0])

    # Проверки
    assert len(sm.nomenclatures) == before


def test_invalid_result_storage_manager_unique_warehouses():
    """
    Проверяет запрет добавления дубликата склада.
    Ожидаемый результат: повторное добавление того же объекта не увеличивает
    размер списка warehouses.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    before = len(sm.warehouses)

    # Действие
    sm.add_warehouse(sm.warehouses[0])

    # Проверки
    assert len(sm.warehouses) == before


def test_valid_result_storage_manager_first_start_creates_data():
    """
    Проверяет, что при первом старте формируются данные.
    Ожидаемый результат: first_start() возвращает True, во всех четырёх списках
    появляются элементы.
    """
    # Подготовка
    sm = storage_manager()
    settings_manager().settings.first_launch_flag = True

    # Действие
    result = sm.first_start(_storage_path())

    # Проверки
    assert result is True
    assert len(sm.groups) > 0
    assert len(sm.ranges) > 0
    assert len(sm.nomenclatures) > 0
    assert len(sm.warehouses) > 0


def test_valid_result_storage_manager_first_start_resets_flag():
    """
    Проверяет сброс флага первого старта после его обработки.
    Ожидаемый результат: после вызова first_start() флаг first_launch_flag
    становится False.
    """
    # Подготовка
    sm = storage_manager()
    smg = settings_manager()
    smg.settings.first_launch_flag = True

    # Действие
    sm.first_start(_storage_path())

    # Проверки
    assert smg.settings.first_launch_flag is False


def test_valid_result_storage_manager_first_start_second_time_no_op():
    """
    Проверяет, что повторный вызов first_start() не пересоздаёт данные.
    Ожидаемый результат: второй вызов возвращает False, размеры списков
    не меняются.
    """
    # Подготовка
    sm = storage_manager()
    smg = settings_manager()
    smg.settings.first_launch_flag = True
    sm.first_start(_storage_path())
    before = len(sm.groups)

    # Действие
    result = sm.first_start(_storage_path())

    # Проверки
    assert result is False
    assert len(sm.groups) == before


def test_valid_name():
    # Подготовка
    s = settings_manager()
    m = storage_manager()

    # Действие
    try:
        m.load_default_ranges()

    # Проверки
        assert True
    except:
        assert False
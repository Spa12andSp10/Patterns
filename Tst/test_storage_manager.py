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


@pytest.fixture(autouse=True)
def reset_storage():
    """Сбрасывает состояние singleton-хранилища перед каждым тестом."""
    sm = storage_manager()
    sm._groups = []
    sm._ranges = []
    sm._nomenclatures = []
    sm._warehouses = []
    sm._is_loaded = False
    sm._data = {}
    yield


# ---------- Singleton ----------

def test_valid_result_storage_manager_singleton():
    """
    Проверяет работу шаблона Singleton для storage_manager.

    Ожидаемый результат:
    два вызова storage_manager() возвращают один и тот же объект.
    """
    s1 = storage_manager()
    s2 = storage_manager()
    assert s1 is s2


# ---------- Загрузка ----------

def test_valid_result_storage_manager_load_success():
    """
    Проверяет успешную загрузку данных из settings.json.

    Ожидаемый результат:
    после вызова load() флаг is_loaded становится True.
    """
    sm = storage_manager()
    sm.load(_settings_path())
    assert sm.is_loaded is True


def test_valid_result_storage_manager_groups_loaded():
    """
    Проверяет, что группы номенклатуры загружены из JSON.

    Ожидаемый результат:
    список groups содержит 4 элемента, включая
    «Молочная продукция» и «Мясная продукция».
    """
    sm = storage_manager()
    sm.load(_settings_path())
    assert len(sm.groups) == 4
    names = [g.name for g in sm.groups]
    assert "Молочная продукция" in names
    assert "Мясная продукция" in names


def test_valid_result_storage_manager_ranges_loaded():
    """
    Проверяет, что единицы измерения загружены из JSON.

    Ожидаемый результат:
    список ranges содержит 4 элемента, включая
    «грамм» и «килограмм».
    """
    sm = storage_manager()
    sm.load(_settings_path())
    assert len(sm.ranges) == 4
    names = [r.name for r in sm.ranges]
    assert "грамм" in names
    assert "килограмм" in names


def test_valid_result_storage_manager_range_base_linked():
    """
    Проверяет, что производная единица измерения ссылается
    на базовую.

    Ожидаемый результат:
    у «килограмм» base указывает на «грамм»,
    conversion_factor равен 1000.0.
    """
    sm = storage_manager()
    sm.load(_settings_path())
    kg = next(r for r in sm.ranges if r.name == "килограмм")
    assert kg.base is not None
    assert kg.base.name == "грамм"
    assert kg.conversion_factor == 1000.0


def test_valid_result_storage_manager_nomenclatures_loaded():
    """
    Проверяет, что номенклатура загружена из JSON.

    Ожидаемый результат:
    список nomenclatures содержит 4 элемента, включая
    «Молоко» и «Яблоко».
    """
    sm = storage_manager()
    sm.load(_settings_path())
    assert len(sm.nomenclatures) == 4
    names = [n.name for n in sm.nomenclatures]
    assert "Молоко" in names
    assert "Яблоко" in names


def test_valid_result_storage_manager_nomenclature_links():
    """
    Проверяет, что номенклатура ссылается на существующие
    группы и единицы измерения.

    Ожидаемый результат:
    у «Молоко» group = «Молочная продукция», range = «литр»,
    full_name = «Молоко пастеризованное 3.2%».
    """
    sm = storage_manager()
    sm.load(_settings_path())
    milk = next(n for n in sm.nomenclatures if n.name == "Молоко")
    assert milk.group.name == "Молочная продукция"
    assert milk.range.name == "литр"
    assert milk.full_name == "Молоко пастеризованное 3.2%"


def test_valid_result_storage_manager_warehouses_loaded():
    """
    Проверяет, что склады загружены из JSON.

    Ожидаемый результат:
    список warehouses содержит 2 элемента: «Основной склад»
    и «Вспомогательный склад».
    """
    sm = storage_manager()
    sm.load(_settings_path())
    assert len(sm.warehouses) == 2
    names = [w.name for w in sm.warehouses]
    assert "Основной склад" in names
    assert "Вспомогательный склад" in names


# ---------- Уникальность ----------

def test_invalid_result_storage_manager_unique_ranges():
    """
    Проверяет запрет добавления дубликата единицы измерения.

    Ожидаемый результат:
    повторное добавление того же объекта не увеличивает
    размер списка ranges.
    """
    sm = storage_manager()
    sm.load(_settings_path())
    before = len(sm.ranges)
    existing = sm.ranges[0]
    sm.add_range(existing)
    assert len(sm.ranges) == before


def test_invalid_result_storage_manager_unique_groups():
    """
    Проверяет запрет добавления дубликата группы.

    Ожидаемый результат:
    повторное добавление того же объекта не увеличивает
    размер списка groups.
    """
    sm = storage_manager()
    sm.load(_settings_path())
    before = len(sm.groups)
    sm.add_group(sm.groups[0])
    assert len(sm.groups) == before


def test_invalid_result_storage_manager_unique_nomenclatures():
    """
    Проверяет запрет добавления дубликата номенклатуры.

    Ожидаемый результат:
    повторное добавление того же объекта не увеличивает
    размер списка nomenclatures.
    """
    sm = storage_manager()
    sm.load(_settings_path())
    before = len(sm.nomenclatures)
    sm.add_nomenclature(sm.nomenclatures[0])
    assert len(sm.nomenclatures) == before


def test_invalid_result_storage_manager_unique_warehouses():
    """
    Проверяет запрет добавления дубликата склада.

    Ожидаемый результат:
    повторное добавление того же объекта не увеличивает
    размер списка warehouses.
    """
    sm = storage_manager()
    sm.load(_settings_path())
    before = len(sm.warehouses)
    sm.add_warehouse(sm.warehouses[0])
    assert len(sm.warehouses) == before


# ---------- Логика первого старта ----------

def test_valid_result_storage_manager_first_start_creates_data():
    """
    Проверяет, что при первом старте формируются данные.

    Ожидаемый результат:
    first_start() возвращает True, во всех четырёх списках
    появляются элементы.
    """
    sm = storage_manager()
    settings_manager().settings.first_launch_flag = True
    result = sm.first_start(_settings_path())
    assert result is True
    assert len(sm.groups) > 0
    assert len(sm.ranges) > 0
    assert len(sm.nomenclatures) > 0
    assert len(sm.warehouses) > 0


def test_valid_result_storage_manager_first_start_resets_flag():
    """
    Проверяет сброс флага первого старта после его обработки.

    Ожидаемый результат:
    после вызова first_start() флаг first_launch_flag
    становится False.
    """
    sm = storage_manager()
    smg = settings_manager()
    smg.settings.first_launch_flag = True
    sm.first_start(_settings_path())
    assert smg.settings.first_launch_flag is False


def test_valid_result_storage_manager_first_start_second_time_no_op():
    """
    Проверяет, что повторный вызов first_start() не пересоздаёт
    данные.

    Ожидаемый результат:
    второй вызов возвращает False, размеры списков
    не меняются.
    """
    sm = storage_manager()
    smg = settings_manager()
    smg.settings.first_launch_flag = True
    sm.first_start(_settings_path())
    before = len(sm.groups)

    result = sm.first_start(_settings_path())
    assert result is False
    assert len(sm.groups) == before
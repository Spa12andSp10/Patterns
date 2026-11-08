import pytest

from Src.Logics.storage_manager import storage_manager
from Src.Logics.settings_manager import settings_manager
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.warehouse_model import warehouse_model


@pytest.fixture(autouse=True)
def reset_storage():
    """Сбрасывает состояние singleton-хранилища перед каждым тестом."""
    sm = storage_manager()
    sm._groups = []
    sm._ranges = []
    sm._nomenclature = []
    sm._warehouse = []
    sm._recipes = []
    sm._ingredients = []
    sm._is_loaded = False
    yield


@pytest.fixture
def loaded_storage():
    """Хранилище, наполненное моделями напрямую (без JSON/десериализации)."""
    sm = storage_manager()

    gram = range_model.create_gram()
    kg = range_model.create_kilogram(base=gram)
    liter = range_model.create_liter()
    sm.add_range(gram)
    sm.add_range(kg)
    sm.add_range(liter)

    dairy = group_model.create("Dairy products")
    meat = group_model.create("Meat products")
    sm.add_group(dairy)
    sm.add_group(meat)

    sm.add_nomenclature(nomenclature_model.create(
        full_name="Pasteurized milk 3.2%",
        name="Milk",
        group=dairy,
        range=liter,
        item_type="product",
    ))
    sm.add_nomenclature(nomenclature_model.create(
        full_name="Apple",
        name="Apple",
        group=dairy,
        range=gram,
        item_type="product",
    ))

    sm.add_warehouse(warehouse_model.create("Main warehouse", "Lenina 1"))
    sm.add_warehouse(warehouse_model.create("Auxiliary warehouse", "Lenina 2"))

    return sm


def test_valid_result_storage_manager_singleton():
    """
    Проверяет работу шаблона Singleton для storage_manager.
    Ожидаемый результат: два вызова возвращают один и тот же объект.
    """
    # Подготовка
    s1 = storage_manager()

    # Действие
    s2 = storage_manager()

    # Проверки
    assert s1 is s2


def test_valid_result_storage_manager_groups_loaded(loaded_storage):
    """
    Проверяет, что группы доступны через свойство groups.
    Ожидаемый результат: 2 группы, включая «Dairy products» и «Meat products».
    """
    # Подготовка
    sm = loaded_storage

    # Действие
    names = [g.name for g in sm.groups]

    # Проверки
    assert len(sm.groups) == 2
    assert "Dairy products" in names
    assert "Meat products" in names


def test_valid_result_storage_manager_ranges_loaded(loaded_storage):
    """
    Проверяет, что единицы измерения доступны через свойство ranges.
    Ожидаемый результат: есть «gram» и «kilogram».
    """
    # Подготовка
    sm = loaded_storage

    # Действие
    names = [r.name for r in sm.ranges]

    # Проверки
    assert "Gram" in names
    assert "Kilogram" in names


def test_valid_result_storage_manager_range_base_linked(loaded_storage):
    """
    Проверяет связь производной единицы с базовой.
    Ожидаемый результат: у «Kilogram» base = «Gram», factor = 1000.
    """
    # Подготовка
    sm = loaded_storage

    # Действие
    kg = next(r for r in sm.ranges if r.name.lower() == "kilogram")

    # Проверки
    assert kg.base is not None
    assert kg.base.name.lower() == "gram"
    assert kg.conversion_factor == 1000.0


def test_valid_result_storage_manager_nomenclatures_loaded(loaded_storage):
    """
    Проверяет, что номенклатура доступна через свойство nomenclatures.
    Ожидаемый результат: 2 элемента, включая «Milk» и «Apple».
    """
    # Подготовка
    sm = loaded_storage

    # Действие
    names = [n.name for n in sm.nomenclatures]

    # Проверки
    assert len(sm.nomenclatures) == 2
    assert "Milk" in names
    assert "Apple" in names


def test_valid_result_storage_manager_nomenclature_links(loaded_storage):
    """
    Проверяет ссылки номенклатуры на группу и единицу измерения.
    Ожидаемый результат: у «Milk» group = «Dairy products», range = «Liter».
    """
    # Подготовка
    sm = loaded_storage

    # Действие
    milk = next(n for n in sm.nomenclatures if n.name == "Milk")

    # Проверки
    assert milk.group.name == "Dairy products"
    assert milk.range.name == "Liter"
    assert milk.full_name == "Pasteurized milk 3.2%"


def test_valid_result_storage_manager_warehouses_loaded(loaded_storage):
    """
    Проверяет, что склады доступны через свойство warehouses.
    Ожидаемый результат: 2 склада с ожидаемыми именами.
    """
    # Подготовка
    sm = loaded_storage

    # Действие
    names = [w.name for w in sm.warehouses]

    # Проверки
    assert len(sm.warehouses) == 2
    assert "Main warehouse" in names
    assert "Auxiliary warehouse" in names


def test_invalid_result_storage_manager_unique_ranges(loaded_storage):
    """
    Проверяет запрет дубликата единицы измерения.
    Ожидаемый результат: размер ranges не меняется.
    """
    # Подготовка
    sm = loaded_storage
    before = len(sm.ranges)

    # Действие
    sm.add_range(sm.ranges[0])

    # Проверки
    assert len(sm.ranges) == before


def test_invalid_result_storage_manager_unique_groups(loaded_storage):
    """
    Проверяет запрет дубликата группы.
    Ожидаемый результат: размер groups не меняется.
    """
    # Подготовка
    sm = loaded_storage
    before = len(sm.groups)

    # Действие
    sm.add_group(sm.groups[0])

    # Проверки
    assert len(sm.groups) == before


def test_invalid_result_storage_manager_unique_nomenclatures(loaded_storage):
    """
    Проверяет запрет дубликата номенклатуры.
    Ожидаемый результат: размер nomenclatures не меняется.
    """
    # Подготовка
    sm = loaded_storage
    before = len(sm.nomenclatures)

    # Действие
    sm.add_nomenclature(sm.nomenclatures[0])

    # Проверки
    assert len(sm.nomenclatures) == before


def test_invalid_result_storage_manager_unique_warehouses(loaded_storage):
    """
    Проверяет запрет дубликата склада.
    Ожидаемый результат: размер warehouses не меняется.
    """
    # Подготовка
    sm = loaded_storage
    before = len(sm.warehouses)

    # Действие
    sm.add_warehouse(sm.warehouses[0])

    # Проверки
    assert len(sm.warehouses) == before


def test_valid_name():
    """
    Проверяет, что load_default_ranges() наполняет справочник единиц
    без исключений.
    Ожидаемый результат: метод завершается без ошибок.
    """
    # Подготовка
    m = storage_manager()

    # Действие
    try:
        m.load_default_ranges()

    # Проверки
        assert True
    except Exception:
        assert False
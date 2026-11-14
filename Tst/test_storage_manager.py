from pathlib import Path

import pytest

from Src.Logics.storage_manager import storage_manager
from Src.Logics.settings_manager import settings_manager
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.warehouse_model import warehouse_model


def _tst_path(name: str) -> str:
    """Путь к файлу в Tst/."""
    return str(Path(__file__).resolve().parent / name)


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
def isolated_settings(tmp_path):
    """Загружает настройки из временной копии, чтобы не менять Tst/settings.json."""
    manager = settings_manager()
    saved = (manager._settings, manager._file_name, manager._is_loaded)

    source = Path(_tst_path("settings.json"))
    target = tmp_path / "settings.json"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    manager.load(str(target))

    yield manager, target

    manager._settings, manager._file_name, manager._is_loaded = saved


@pytest.fixture
def loaded_storage():
    """Хранилище, наполненное моделями напрямую."""
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


def test_valid_result_storage_manager_load_serialized():
    """
    Проверяет загрузку хранилища из serialized_storage.json.
    Ожидаемый результат: True, флаг is_loaded установлен, данные не пусты.
    """
    # Подготовка
    sm = storage_manager()

    # Действие
    result = sm.load(
        _tst_path("serialized_storage.json"),
        _tst_path("storage_data.json"),
    )

    # Проверки
    assert result is True
    assert sm.is_loaded is True
    assert len(sm.groups) > 0
    assert len(sm.ranges) > 0


def test_valid_result_storage_manager_load_first_start(isolated_settings):
    """
    Проверяет первый старт из storage_data.json при отсутствии слепка.
    Ожидаемый результат: True, данные загружены, флаг первого запуска снят.
    """
    # Подготовка
    manager, settings_path = isolated_settings
    sm = storage_manager()

    # Действие
    result = sm.load(
        _tst_path("missing_serialized_storage.json"),
        _tst_path("storage_data.json"),
    )

    # Проверки
    assert result is True
    assert sm.is_loaded is True
    assert len(sm.groups) > 0
    assert len(sm.nomenclatures) > 0
    assert manager.settings.first_launch_flag is False
    assert settings_path.exists()


def test_invalid_result_storage_manager_load_missing_files(tmp_path):
    """
    Проверяет загрузку при отсутствии обоих файлов.
    Ожидаемый результат: False, флаг is_loaded не установлен.
    """
    # Подготовка
    sm = storage_manager()

    # Действие
    result = sm.load(
        str(tmp_path / "missing_serialized_storage.json"),
        str(tmp_path / "missing_storage_data.json"),
    )

    # Проверки
    assert result is False
    assert sm.is_loaded is False
    assert sm.groups == []


def test_valid_result_storage_manager_load_is_idempotent():
    """
    Проверяет повторную загрузку уже заполненного хранилища.
    Ожидаемый результат: True и отсутствие дубликатов.
    """
    # Подготовка
    sm = storage_manager()
    assert sm.load(_tst_path("serialized_storage.json")) is True
    groups_before = len(sm.groups)
    ranges_before = len(sm.ranges)

    # Действие
    result = sm.load(_tst_path("serialized_storage.json"))

    # Проверки
    assert result is True
    assert len(sm.groups) == groups_before
    assert len(sm.ranges) == ranges_before
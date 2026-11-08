import json
from pathlib import Path

import pytest

from Src.Core.abstract_convertor import abstract_convertor
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialization import deserialization
from Src.Logics.storage_manager import storage_manager
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_bootstrap import storage_bootstrap


SERIALIZED_FILE = "serialized_storage.json"


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
def original_storage():
    """Хранилище с эталонными данными, загруженными из storage_data.json."""
    settings_manager().load(_tst_path("settings.json"))
    settings_manager().settings.first_launch_flag = True

    storage = storage_manager()
    storage_bootstrap(storage).first_start(_tst_path("storage_data.json"))
    return storage


@pytest.fixture
def serialized_json(original_storage):
    """Эталон JSON после сериализации моделей из хранилища.

    Дополнительно сохраняет результат в Tst/serialized_storage.json,
    чтобы эталон можно было посмотреть глазами и переиспользовать.
    """
    walker = convert_factory().create()
    payload = {
        "groups": [walker.convert(g) for g in original_storage.groups],
        "ranges": [walker.convert(r) for r in original_storage.ranges],
        "nomenclature": [walker.convert(n) for n in original_storage.nomenclatures],
        "warehouse": [walker.convert(w) for w in original_storage.warehouses],
        "recipes": [walker.convert(r) for r in original_storage.recipes],
    }
    data = json.loads(abstract_convertor.to_json(payload))

    with open(_tst_path(SERIALIZED_FILE), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


@pytest.fixture
def restored_storage(serialized_json):
    """Хранилище, восстановленное десериализацией эталонного JSON."""
    storage = storage_manager()
    storage._groups.clear()
    storage._nomenclature.clear()
    storage._warehouse.clear()
    storage._ranges.clear()
    storage._recipes.clear()
    storage._ingredients.clear()

    deserialization(storage).deserialized(serialized_json)
    return storage


def _pairs(models):
    """Множество пар (name, unique_code) для сравнения."""
    return {(m.name, m.unique_code) for m in models}


def test_valid_result_storage_groups(original_storage, restored_storage):
    """
    Проверяет, что группы после сериализации и десериализации
    совпадают с исходными по имени и уникальному коду.
    Ожидаемый результат: набор пар (name, unique_code) совпадает.
    """
    # Подготовка
    expected = _pairs(original_storage.groups)

    # Действие
    actual = _pairs(restored_storage.groups)

    # Проверки
    assert actual == expected


def test_valid_result_storage_ranges(original_storage, restored_storage):
    """
    Проверяет, что единицы измерения после сериализации и
    десериализации совпадают с исходными по имени и уникальному коду.
    Ожидаемый результат: набор пар (name, unique_code) совпадает.
    """
    # Подготовка
    expected = _pairs(original_storage.ranges)

    # Действие
    actual = _pairs(restored_storage.ranges)

    # Проверки
    assert actual == expected


def test_valid_result_storage_nomenclature(original_storage, restored_storage):
    """
    Проверяет, что номенклатура после сериализации и десериализации
    совпадает с исходной по имени и уникальному коду.
    Ожидаемый результат: набор пар (name, unique_code) совпадает.
    """
    # Подготовка
    expected = _pairs(original_storage.nomenclatures)

    # Действие
    actual = _pairs(restored_storage.nomenclatures)

    # Проверки
    assert actual == expected


def test_valid_result_storage_warehouse(original_storage, restored_storage):
    """
    Проверяет, что склады после сериализации и десериализации
    совпадают с исходными по имени и уникальному коду.
    Ожидаемый результат: набор пар (name, unique_code) совпадает.
    """
    # Подготовка
    expected = _pairs(original_storage.warehouses)

    # Действие
    actual = _pairs(restored_storage.warehouses)

    # Проверки
    assert actual == expected


def test_valid_result_storage_recipes(original_storage, restored_storage):
    """
    Проверяет, что рецепты после сериализации и десериализации
    совпадают с исходными по имени и уникальному коду.
    Ожидаемый результат: набор пар (name, unique_code) совпадает.
    """
    # Подготовка
    expected = _pairs(original_storage.recipes)

    # Действие
    actual = _pairs(restored_storage.recipes)

    # Проверки
    assert actual == expected


def test_valid_result_storage_group_model(original_storage, restored_storage):
    """
    Проверяет, что конкретная группа совпадает
    с исходной моделью по имени и уникальному коду.
    Ожидаемый результат: name и unique_code совпадают.
    """
    # Подготовка
    original = original_storage.groups[0]

    # Действие
    restored = next(
        g for g in restored_storage.groups if g.name == original.name
    )

    # Проверки
    assert restored.name == original.name
    assert restored.unique_code == original.unique_code


def test_valid_result_storage_range_model(original_storage, restored_storage):
    """
    Проверяет, что конкретная единица измерения
    совпадает с исходной моделью по имени и уникальному коду.
    Ожидаемый результат: name и unique_code совпадают.
    """
    # Подготовка
    original = original_storage.ranges[0]

    # Действие
    restored = next(
        r for r in restored_storage.ranges if r.name == original.name
    )

    # Проверки
    assert restored.name == original.name
    assert restored.unique_code == original.unique_code


def test_valid_result_storage_nomenclature_model(original_storage, restored_storage):
    """
    Проверяет, что конкретная номенклатура =
    совпадает с исходной моделью по имени и уникальному коду.
    Ожидаемый результат: name и unique_code совпадают.
    """
    # Подготовка
    original = original_storage.nomenclatures[0]

    # Действие
    restored = next(
        n for n in restored_storage.nomenclatures if n.name == original.name
    )

    # Проверки
    assert restored.name == original.name
    assert restored.unique_code == original.unique_code


def test_valid_result_storage_warehouse_model(original_storage, restored_storage):
    """
    Проверяет, что конкретный склад совпадает
    с исходной моделью по имени и уникальному коду.
    Ожидаемый результат: name и unique_code совпадают.
    """
    # Подготовка
    original = original_storage.warehouses[0]

    # Действие
    restored = next(
        w for w in restored_storage.warehouses if w.name == original.name
    )

    # Проверки
    assert restored.name == original.name
    assert restored.unique_code == original.unique_code


def test_valid_result_storage_recipe_model(original_storage, restored_storage):
    """
    Проверяет, что конкретный рецепт после round-trip совпадает
    с исходной моделью по имени и уникальному коду.
    Ожидаемый результат: name и unique_code совпадают.
    """
    # Подготовка
    original = original_storage.recipes[0]

    # Действие
    restored = next(
        r for r in restored_storage.recipes if r.name == original.name
    )

    # Проверки
    assert restored.name == original.name
    assert restored.unique_code == original.unique_code


def test_valid_result_storage_serialized_file_created(serialized_json):
    """
    Проверяет, что эталонный JSON после сериализации сохранён в файл
    в папке тестов и является валидным JSON.
    Ожидаемый результат: файл существует, читается, содержит
    те же секции, что и in-memory словарь.
    """
    # Подготовка
    path = Path(_tst_path(SERIALIZED_FILE))

    # Действие
    exists = path.exists()
    with open(path, encoding="utf-8") as f:
        on_disk = json.load(f)

    # Проверки
    assert exists
    assert path.parent.name == "Tst"
    assert set(on_disk) == {"groups", "ranges", "nomenclature", "warehouse", "recipes"}
    assert on_disk == serialized_json
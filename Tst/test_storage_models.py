import json
import copy
from pathlib import Path

import pytest

from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.entity_type import entity_type
from Src.Core.exception import arguments_exeption
from Src.Logics.convert_factory import convert_factory
from Src.Logics.storage_deserializer import storage_deserializer
from Src.Logics.settings_deserializer import settings_deserializer
from Src.Logics.storage_manager import storage_manager
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_bootstrap import storage_bootstrap


SETTINGS_FILE = "settings.json"
STORAGE_RAW_FILE = "storage_data.json"
SERIALIZED_FILE = "serialized_storage.json"
SERIALIZED_SETTINGS_FILE = "serialized_settings.json"


def _tst_path(name: str) -> str:
    """Путь к файлу в Tst/."""
    return str(Path(__file__).resolve().parent / name)


def _pairs(models) -> set:
    """Множество пар (name, unique_code)."""
    return {(m.name, m.unique_code) for m in models}


def _serialize_storage(storage) -> dict:
    """Сериализует хранилище тем же путём, что и продакшн save_models."""
    walker = convert_factory().create()
    payload = {
        "groups":       [walker.convert(g) for g in storage.groups],
        "ranges":       [walker.convert(r) for r in storage.ranges],
        "nomenclature": [walker.convert(n) for n in storage.nomenclatures],
        "warehouse":    [walker.convert(w) for w in storage.warehouses],
        "recipes":      [walker.convert(r) for r in storage.recipes],
    }
    return json.loads(abstract_convertor.to_json(payload))


def _serialize_settings(model) -> dict:
    """Сериализует settings_model тем же путём, что и storage:
    через convert_factory/walker."""
    walker = convert_factory().create()
    return json.loads(abstract_convertor.to_json(walker.convert(model)))


def _reset_storage() -> storage_manager:
    """Полный сброс singleton-хранилища (storage-секции, без organizations)."""
    sm = storage_manager()
    for attr in (
        "_groups", "_ranges", "_nomenclature",
        "_warehouse", "_recipes", "_ingredients",
    ):
        getattr(sm, attr, []).clear()
    sm._is_loaded = False
    return sm



@pytest.fixture(autouse=True)
def reset_storage_fixture():
    """Сбрасывает состояние singleton-хранилища перед каждым тестом."""
    _reset_storage()
    yield


@pytest.fixture
def original_storage():
    """Эталонное хранилище, загруженное из «сырого» storage_data.json."""
    settings_manager().load(_tst_path(SETTINGS_FILE))
    settings_manager().settings.first_launch_flag = True

    storage = _reset_storage()
    storage_bootstrap(storage).first_start(_tst_path(STORAGE_RAW_FILE))
    return storage


@pytest.fixture
def serialized_json(original_storage):
    """Эталон JSON — получается сериализацией."""
    data = _serialize_storage(original_storage)

    with open(_tst_path(SERIALIZED_FILE), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


@pytest.fixture
def restored_storage(original_storage, serialized_json):
    """Хранилище, восстановленное новой десериализацией"""
    storage = _reset_storage()
    storage_deserializer(storage).deserialized(serialized_json)
    return storage


@pytest.fixture
def serialized_settings():
    """Дамп сериализованных настроек"""
    path = Path(_tst_path(SETTINGS_FILE))
    if not path.exists():
        pytest.skip(f"{SETTINGS_FILE} не найден в Tst/")

    model = settings_deserializer.load(str(path))
    assert model is not None

    data = _serialize_settings(model)

    with open(_tst_path(SERIALIZED_SETTINGS_FILE), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data



def test_groups_roundtrip(original_storage, restored_storage):
    """
    Проверяет round-trip групп.
    Ожидаемый результат: набор пар (name, unique_code) совпадает.
    """
    # Подготовка
    expected = _pairs(original_storage.groups)

    # Действие
    actual = _pairs(restored_storage.groups)

    # Проверки
    assert actual == expected


def test_ranges_roundtrip(original_storage, restored_storage):
    """
    Проверяет round-trip единиц измерения.
    Ожидаемый результат: набор пар (name, unique_code) совпадает.
    """
    # Подготовка
    expected = _pairs(original_storage.ranges)

    # Действие
    actual = _pairs(restored_storage.ranges)

    # Проверки
    assert actual == expected


def test_nomenclature_roundtrip(original_storage, restored_storage):
    """
    Проверяет round-trip номенклатуры.
    Ожидаемый результат: набор пар (name, unique_code) совпадает.
    """
    # Подготовка
    expected = _pairs(original_storage.nomenclatures)

    # Действие
    actual = _pairs(restored_storage.nomenclatures)

    # Проверки
    assert actual == expected


def test_warehouse_roundtrip(original_storage, restored_storage):
    """
    Проверяет round-trip складов.
    Ожидаемый результат: набор пар (name, unique_code) совпадает.
    """
    # Подготовка
    expected = _pairs(original_storage.warehouses)

    # Действие
    actual = _pairs(restored_storage.warehouses)

    # Проверки
    assert actual == expected


def test_recipes_roundtrip(original_storage, restored_storage):
    """
    Проверяет round-trip рецептов.
    Ожидаемый результат: набор пар (name, unique_code) совпадает.
    """
    # Подготовка
    expected = _pairs(original_storage.recipes)

    # Действие
    actual = _pairs(restored_storage.recipes)

    # Проверки
    assert actual == expected


def test_group_model_content(original_storage, restored_storage):
    """
    Проверяет содержимое конкретной группы после round-trip.
    Ожидаемый результат: name и unique_code совпадают.
    """
    # Подготовка
    original = original_storage.groups[0]

    # Действие
    restored = next(g for g in restored_storage.groups if g.name == original.name)

    # Проверки
    assert restored.name == original.name
    assert restored.unique_code == original.unique_code


def test_range_model_content(original_storage, restored_storage):
    """
    Проверяет range после round-trip: name, unique_code,
    conversion_factor и рекурсивный base (kilogram -> gram).
    Ожидаемый результат: base — ТОТ ЖЕ объект из storage.ranges,
    а не копия (кэш resolver по unique_code).
    """
    # Подготовка
    original = original_storage.ranges[1]

    # Действие
    restored = next(r for r in restored_storage.ranges if r.name == original.name)

    # Проверки
    assert restored.name == original.name
    assert restored.unique_code == original.unique_code
    assert restored.conversion_factor == original.conversion_factor
    assert restored.base is not None
    assert restored.base.unique_code == original.base.unique_code
    assert any(r is restored.base for r in restored_storage.ranges)


def test_nomenclature_model_content(original_storage, restored_storage):
    """
    Проверяет nomenclature после round-trip: full_name, name,
    unique_code, item_type и ссылки group/range.
    Ожидаемый результат: ссылки указывают на объекты
    из соответствующих секций restored_storage, а не на копии.
    """
    # Подготовка
    original = original_storage.nomenclatures[0]

    # Действие
    restored = next(n for n in restored_storage.nomenclatures if n.name == original.name)

    # Проверки
    assert restored.full_name == original.full_name
    assert restored.name == original.name
    assert restored.unique_code == original.unique_code
    assert restored.item_type == original.item_type
    assert any(g is restored.group for g in restored_storage.groups)
    assert any(r is restored.range for r in restored_storage.ranges)


def test_warehouse_model_content(original_storage, restored_storage):
    """
    Проверяет warehouse после round-trip: name, address, unique_code.
    Ожидаемый результат: поля совпадают.
    """
    # Подготовка
    original = original_storage.warehouses[0]

    # Действие
    restored = next(w for w in restored_storage.warehouses if w.name == original.name)

    # Проверки
    assert restored.name == original.name
    assert restored.address == original.address
    assert restored.unique_code == original.unique_code


def test_recipe_model_content(original_storage, restored_storage):
    """
    Проверяет recipe после round-trip: name, description, time,
    состав (все поля ингредиентов), preparation_method и БЖУ-расчёт.
    Ожидаемый результат: всё совпадает с оригиналом.
    """
    # Подготовка
    original = original_storage.recipes[0]

    # Действие
    restored = next(r for r in restored_storage.recipes if r.name == original.name)

    # Проверки
    assert restored.unique_code == original.unique_code
    assert restored.description == original.description
    assert restored.time == original.time
    assert len(restored.ingredients) == len(original.ingredients)

    by_name = {i.full_name: i for i in restored.ingredients}
    for src in original.ingredients:
        dst = by_name[src.full_name]
        assert dst.unique_code == src.unique_code
        assert dst.brutto == src.brutto
        assert dst.proteins == src.proteins
        assert dst.fats == src.fats
        assert dst.carbohydrates == src.carbohydrates
        assert dst.coef == src.coef
        assert dst.item_type == src.item_type

    assert restored.preparation_method == original.preparation_method
    assert restored.calculate_nutrition() == original.calculate_nutrition()


def test_short_reference_resolved_from_cache(original_storage, serialized_json):
    """
    Проверяет resolve краткой ссылки {unique_code, type, name}
    """
    # Подготовка
    target = original_storage.groups[0]
    short_ref = {
        "unique_code": target.unique_code,
        "type": entity_type.GROUP.value,
        "name": target.name,
    }

    nested = {
        "group": short_ref,
        "name": "Holder",
        "full_name": "Holder",
        "item_type": "product",
    }

    # Действие и проверки: пустой кэш -> ошибка
    fresh = storage_deserializer(_reset_storage())
    with pytest.raises(arguments_exeption):
        fresh.factory.deserialize(nested)

    # Действие: наполняем кэш и повторяем
    deserializer = storage_deserializer(_reset_storage())
    deserializer.deserialized(serialized_json)
    resolved = deserializer.factory.deserialize(nested)

    assert resolved.group is not None
    assert resolved.group.unique_code == target.unique_code


def test_cyclic_self_reference_raises(original_storage, serialized_json):
    """
    Проверяет защиту от цикла: рецепт, ссылающийся сам на себя.
    Ожидаемый результат: arguments_exeption (не RecursionError).
    """
    # Подготовка
    deserializer = storage_deserializer(_reset_storage())
    deserializer.deserialized(serialized_json)

    recipe = copy.deepcopy(serialized_json["recipes"][0])
    recipe["ingredients"] = {
        "0": {
            "time": recipe["time"],
            "description": recipe["description"],
            "preparation_method": recipe["preparation_method"],
            "ingredients": {},
            "name": recipe["name"],
            "unique_code": recipe["unique_code"],   # тот же код — цикл
        }
    }

    # Действие и проверки
    with pytest.raises(arguments_exeption):
        storage_deserializer(_reset_storage()).factory.deserialize(recipe)


def test_settings_roundtrip():
    """
    Проверяет, что settings_deserializer.load(settings.json)
    собирает settings_model с organization, симметрично
    сериализации через walker.
    Ожидаемый результат: все поля, включая organization, совпадают.
    """
    # Подготовка
    path = Path(_tst_path(SETTINGS_FILE))
    if not path.exists():
        pytest.skip(f"{SETTINGS_FILE} не найден в Tst/")
    raw = json.loads(path.read_text(encoding="utf-8"))

    # Действие
    model = settings_deserializer.load(str(path))

    # Проверки
    assert model is not None
    assert model.organization is not None
    assert model.response_format in ("TXT", "CSV", "MARKDOWN", "XML", "HTML", "PNG")

    org_raw = raw["organization"]
    assert model.organization.name == org_raw["name"]
    assert model.organization.inn == org_raw["inn"]
    assert model.organization.bic == org_raw["bic"]
    assert model.organization.account == org_raw["account"]
    assert model.organization.owner == org_raw["owner"]
    if "unique_code" in org_raw:
        assert model.organization.unique_code == org_raw["unique_code"]

    assert model.boss_name == raw["boss_name"]
    assert model.account_name == raw["account_name"]
    assert model.first_launch_flag == raw["first_launch_flag"]
    assert model.response_format == raw["response_format"]


def test_settings_roundtrip_via_serialized(serialized_settings):
    """
    Проверяет симметрию: settings_model -> walker -> dict ->
    settings_deserializer -> settings_model.
    Ожидаемый результат: все поля восстановились, включая organization.
    """
    # Подготовка
    raw = serialized_settings

    # Действие
    restored = settings_deserializer.from_dict(raw)

    # Проверки
    assert restored.boss_name == raw["boss_name"]
    assert restored.account_name == raw["account_name"]
    assert restored.first_launch_flag == raw["first_launch_flag"]
    assert restored.response_format == raw["response_format"]
    assert restored.unique_code == raw["unique_code"]

    org_raw = raw["organization"]
    assert restored.organization is not None
    assert restored.organization.name == org_raw["name"]
    assert restored.organization.inn == org_raw["inn"]
    assert restored.organization.bic == org_raw["bic"]
    assert restored.organization.account == org_raw["account"]
    assert restored.organization.owner == org_raw["owner"]
    assert restored.organization.unique_code == org_raw["unique_code"]


def test_settings_deserializer_does_not_touch_storage():
    """
    Проверяет изоляцию: settings_deserializer не трогает storage_manager.
    Ожидаемый результат: до и после load storage не изменился,
    поля organizations у storage нет.
    """
    # Подготовка
    path = Path(_tst_path(SETTINGS_FILE))
    if not path.exists():
        pytest.skip(f"{SETTINGS_FILE} не найден в Tst/")

    sm = _reset_storage()
    before = (
        list(sm.groups), list(sm.ranges), list(sm.nomenclatures),
        list(sm.warehouses), list(sm.recipes), list(sm.ingredients),
    )

    # Действие
    model = settings_deserializer.load(str(path))

    # Проверки
    assert model.organization is not None
    after = (
        list(sm.groups), list(sm.ranges), list(sm.nomenclatures),
        list(sm.warehouses), list(sm.recipes), list(sm.ingredients),
    )
    assert before == after
    assert not hasattr(sm, "organizations")
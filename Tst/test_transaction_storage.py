import json
from datetime import datetime

import pytest

from Src.Logics.convert_factory import convert_factory
from Src.Logics.storage_bootstrap import storage_bootstrap
from Src.Logics.storage_deserializer import storage_deserializer
from Src.Logics.storage_manager import storage_manager
from Src.Logics.storage_persistence import storage_persistence
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.transaction_model import transaction_model
from Src.Models.warehouse_model import warehouse_model


def _reset_storage() -> storage_manager:
    """Полностью сбрасывает singleton-хранилище."""
    storage = storage_manager()
    for attr in (
        "_groups", "_ranges", "_nomenclature", "_warehouse",
        "_recipes", "_ingredients", "_transactions",
    ):
        setattr(storage, attr, [])
    storage._is_loaded = False
    return storage


@pytest.fixture(autouse=True)
def reset_storage_fixture():
    """Сбрасывает хранилище перед каждым тестом."""
    _reset_storage()
    yield
    _reset_storage()


def _filled_storage() -> storage_manager:
    """Возвращает хранилище со справочниками и двумя транзакциями."""
    storage = _reset_storage()

    group = group_model.create("Dairy products")
    unit = range_model.create("liter", 1.0, None)
    milk = nomenclature_model.create(
        "Pasteurized milk 3.2%", "Milk", group, unit, "product",
    )
    warehouse = warehouse_model.create("Main warehouse", "29 Lermontova St.")

    storage.add_group(group)
    storage.add_range(unit)
    storage.add_nomenclature(milk)
    storage.add_warehouse(warehouse)
    storage.add_transaction(transaction_model.create(
        milk, warehouse, unit, 10, datetime(2026, 1, 15),
    ))
    storage.add_transaction(transaction_model.create(
        milk, warehouse, unit, -4, datetime(2026, 1, 16),
    ))
    return storage


def test_save_models_writes_transactions_section(tmp_path):
    """save_models сохраняет транзакции в ключе ``transactions``."""

    # Подготовка
    storage = _filled_storage()
    path = tmp_path / "storage.json"

    # Действие
    saved = storage_persistence(storage).save_models(str(path))

    # Проверки
    assert saved is True

    data = json.loads(path.read_text(encoding="utf-8"))
    assert "transactions" in data
    assert len(data["transactions"]) == 2
    assert "transaction" not in data


def test_save_models_serializes_transaction_fields(tmp_path):
    """Сериализация сохраняет поля транзакции и ссылки на справочники."""

    # Подготовка
    storage = _filled_storage()
    path = tmp_path / "storage.json"

    # Действие
    saved = storage_persistence(storage).save_models(str(path))

    # Проверки
    assert saved is True

    data = json.loads(path.read_text(encoding="utf-8"))
    serialized = data["transactions"]
    assert len(serialized) == 2

    for raw, original in zip(serialized, storage.transactions):
        assert raw["unique_code"] == original.unique_code
        assert raw["value"] == original.value
        assert raw["period"] == original.period.isoformat()
        for field, model in (
            ("nomenclatures", original.nomenclatures),
            ("warehouses", original.warehouses),
            ("ranges", original.ranges),
        ):
            assert isinstance(raw[field], dict)
            assert raw[field]["name"] == model.name
            assert raw[field]["unique_code"] == model.unique_code


def test_transaction_roundtrip_preserves_fields_and_references(tmp_path):
    """Полный цикл save -> load сохраняет значения и идентичность ссылок."""

    # Подготовка
    storage = _filled_storage()
    originals = list(storage.transactions)
    path = tmp_path / "storage.json"
    storage_persistence(storage).save_models(str(path))

    # Действие
    restored = _reset_storage()

    # Проверки
    assert storage_deserializer(restored).load(str(path)) is True

    assert len(restored.transactions) == len(originals)
    for original, item in zip(originals, restored.transactions):
        assert item.unique_code == original.unique_code
        assert item.value == original.value
        assert item.period == original.period
        assert item.nomenclatures is next(
            model for model in restored.nomenclatures
            if model.unique_code == original.nomenclatures.unique_code
        )
        assert item.warehouses is next(
            model for model in restored.warehouses
            if model.unique_code == original.warehouses.unique_code
        )
        assert item.ranges is next(
            model for model in restored.ranges
            if model.unique_code == original.ranges.unique_code
        )


def test_deserializer_transactions_from_indexed_dict(tmp_path):
    """Транзакции принимаются и в виде словаря с числовыми ключами."""

    # Подготовка
    storage = _filled_storage()
    path = tmp_path / "storage.json"
    storage_persistence(storage).save_models(str(path))
    data = json.loads(path.read_text(encoding="utf-8"))
    data["transactions"] = dict(enumerate(data["transactions"]))

    # Действие
    restored = _reset_storage()

    # Проверки
    assert storage_deserializer(restored).deserialized(data) is True

    assert len(restored.transactions) == 2
    assert {item.value for item in restored.transactions} == {10.0, -4.0}


def test_deserializer_malformed_transactions_returns_false(tmp_path):
    """Некорректная секция транзакций отклоняется при загрузке."""

    # Подготовка
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"transactions": 42}), encoding="utf-8")

    # Действие
    storage = _reset_storage()

    # Проверки
    assert storage_deserializer(storage).load(str(path)) is False
    assert storage.transactions == []


def test_storage_manager_load_restores_transactions_from_snapshot(tmp_path):
    """Производственный load() поднимает транзакции из слепка."""

    # Подготовка
    storage = _filled_storage()
    path = tmp_path / "storage.json"
    storage_persistence(storage).save_models(str(path))

    # Действие
    restored = _reset_storage()

    # Проверки
    assert restored.load(str(path)) is True

    assert len(restored.transactions) == 2
    assert {item.value for item in restored.transactions} == {10.0, -4.0}
    assert all(isinstance(item, transaction_model) for item in restored.transactions)


def test_deserializer_restores_transactions(tmp_path):
    """Десериализатор восстанавливает транзакции и их ссылки."""

    # Подготовка
    storage = _filled_storage()
    path = tmp_path / "storage.json"
    storage_persistence(storage).save_models(str(path))

    # Действие
    restored = _reset_storage()

    # Проверки
    assert storage_deserializer(restored).load(str(path)) is True

    assert len(restored.transactions) == 2
    first, second = restored.transactions
    assert isinstance(first, transaction_model)
    assert first.value == 10.0
    assert first.period == datetime(2026, 1, 15)
    assert isinstance(first.nomenclatures, nomenclature_model)
    assert first.nomenclatures.name == "Milk"
    assert isinstance(first.warehouses, warehouse_model)
    assert first.warehouses.name == "Main warehouse"
    assert isinstance(first.ranges, range_model)
    assert first.ranges.name == "liter"
    assert second.value == -4.0


def test_deserializer_transactions_are_registered_after_ranges():
    """Транзакции загружаются после ranges и находят свои ссылки."""

    # Подготовка
    storage = _reset_storage()

    group = group_model.create("Dairy products")
    unit = range_model.create("liter", 1.0, None)
    milk = nomenclature_model.create(
        "Pasteurized milk 3.2%", "Milk", group, unit, "product",
    )
    warehouse = warehouse_model.create(
        "Main warehouse", "29 Lermontova St.",
    )
    walker = convert_factory().create()

    # Действие
    data = {
        "groups": [walker.convert(group)],
        "ranges": [walker.convert(unit)],
        "nomenclature": [walker.convert(milk)],
        "warehouse": [walker.convert(warehouse)],
        "transactions": [{
            "nomenclatures": "Milk",
            "warehouses": "Main warehouse",
            "ranges": "liter",
            "value": 10,
            "period": "2026-01-15",
        }],
    }

    # Проверки
    assert storage_deserializer(storage).deserialized(data) is True

    assert len(storage.transactions) == 1
    transaction = storage.transactions[0]
    assert transaction.nomenclatures.name == "Milk"
    assert transaction.warehouses.name == "Main warehouse"
    assert transaction.ranges.name == "liter"


def test_deserializer_without_transactions_section_is_valid():
    """Отсутствие секции transactions не считается ошибкой."""

    # Подготовка
    # Действие
    storage = _reset_storage()

    # Проверки
    assert storage_deserializer(storage).deserialized({
        "groups": [{"name": "Dairy products"}],
    }) is True
    assert storage.transactions == []


def test_bootstrap_loads_transactions():
    """Bootstrap загружает транзакции после справочников."""

    # Подготовка
    storage = _reset_storage()

    # Действие
    data = {
        "groups": [{"name": "Dairy products"}],
        "ranges": [{"name": "liter", "conversion_factor": 1, "base": None}],
        "nomenclature": [{
            "name": "Milk",
            "full_name": "Pasteurized milk 3.2%",
            "group": "Dairy products",
            "range": "liter",
            "item_type": "product",
        }],
        "warehouse": [{
            "name": "Main warehouse",
            "address": "29 Lermontova St.",
        }],
        "transactions": [{
            "nomenclatures": "Milk",
            "warehouses": "Main warehouse",
            "ranges": "liter",
            "value": -4,
            "period": "2026-01-16",
        }],
        "recipes": [],
    }

    # Проверки
    assert storage_bootstrap(storage)._load(data) is True

    assert len(storage.transactions) == 1
    transaction = storage.transactions[0]
    assert transaction.value == -4.0
    assert transaction.period == datetime(2026, 1, 16)
    assert transaction.nomenclatures.name == "Milk"
    assert transaction.warehouses.name == "Main warehouse"
    assert transaction.ranges.name == "liter"

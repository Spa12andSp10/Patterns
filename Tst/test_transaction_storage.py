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
    storage = _filled_storage()
    path = tmp_path / "storage.json"

    assert storage_persistence(storage).save_models(str(path)) is True

    data = json.loads(path.read_text(encoding="utf-8"))
    assert "transactions" in data
    assert len(data["transactions"]) == 2
    assert "transaction" not in data


def test_deserializer_restores_transactions(tmp_path):
    """Десериализатор восстанавливает транзакции и их ссылки."""
    storage = _filled_storage()
    path = tmp_path / "storage.json"
    storage_persistence(storage).save_models(str(path))

    restored = _reset_storage()
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

    assert storage_deserializer(storage).deserialized(data) is True

    assert len(storage.transactions) == 1
    transaction = storage.transactions[0]
    assert transaction.nomenclatures.name == "Milk"
    assert transaction.warehouses.name == "Main warehouse"
    assert transaction.ranges.name == "liter"


def test_deserializer_without_transactions_section_is_valid():
    """Отсутствие секции transactions не считается ошибкой."""
    storage = _reset_storage()

    assert storage_deserializer(storage).deserialized({
        "groups": [{"name": "Dairy products"}],
    }) is True
    assert storage.transactions == []


def test_bootstrap_loads_transactions():
    """Bootstrap загружает транзакции после справочников."""
    storage = _reset_storage()
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

    assert storage_bootstrap(storage)._load(data) is True

    assert len(storage.transactions) == 1
    transaction = storage.transactions[0]
    assert transaction.value == -4.0
    assert transaction.period == datetime(2026, 1, 16)
    assert transaction.nomenclatures.name == "Milk"
    assert transaction.warehouses.name == "Main warehouse"
    assert transaction.ranges.name == "liter"

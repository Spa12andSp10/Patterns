from datetime import datetime

import pytest

from main import api
from Src.Logics.storage_manager import storage_manager
from Src.Logics.turnover_prototype import turnover_prototype
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.transaction_model import transaction_model
from Src.Models.warehouse_model import warehouse_model


@pytest.fixture(scope="module")
def client():
    """Тестовый клиент Flask."""
    with api.app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_storage():
    """Очищает все коллекции singleton-хранилища перед тестом."""
    storage = storage_manager()
    for attr in (
        "_groups", "_ranges", "_nomenclature", "_warehouse",
        "_recipes", "_ingredients", "_transactions",
    ):
        setattr(storage, attr, [])
    yield


def _fill_storage():
    """Добавляет в хранилище два склада и три транзакции."""
    storage = storage_manager()

    group = group_model.create("Dairy products")
    unit = range_model.create("liter", 1.0, None)
    milk = nomenclature_model.create(
        "Pasteurized milk 3.2%", "Milk", group, unit, "product",
    )
    apple = nomenclature_model.create(
        "Astrakhan apple", "Apple", group, unit, "product",
    )
    main = warehouse_model.create("Main warehouse", "29 Lermontova St.")
    auxiliary = warehouse_model.create(
        "Auxiliary warehouse", "52 Krasnoarmeyskaya St.",
    )

    for model, add in (
        (group, storage.add_group),
        (unit, storage.add_range),
        (milk, storage.add_nomenclature),
        (apple, storage.add_nomenclature),
        (main, storage.add_warehouse),
        (auxiliary, storage.add_warehouse),
    ):
        add(model)

    storage.add_transaction(transaction_model.create(
        milk, main, unit, 10, datetime(2026, 1, 15),
    ))
    storage.add_transaction(transaction_model.create(
        milk, main, unit, -4, datetime(2026, 1, 16),
    ))
    storage.add_transaction(transaction_model.create(
        apple, auxiliary, unit, 7, datetime(2026, 1, 17),
    ))
    return storage


def test_osv_empty_storage_returns_header(client):
    """Без транзакций возвращается только заголовок."""
    response = client.post("/api/osv", json={})

    assert response.status_code == 200
    data = response.get_json()
    assert data["header"] == turnover_prototype.HEADER
    assert data["rows"] == []


def test_osv_returns_report_data(client):
    """Endpoint возвращает строки ОСВ и итоговую строку."""
    _fill_storage()

    response = client.post("/api/osv", json={})

    assert response.status_code == 200
    data = response.get_json()
    assert data["header"] == turnover_prototype.HEADER
    assert data["rows"] == [
        ["Milk", "Main warehouse", "liter", 0.0, 10.0, 4.0, 6.0],
        ["Apple", "Auxiliary warehouse", "liter", 0.0, 7.0, 0.0, 7.0],
        ["ИТОГО", "", "", 0.0, 17.0, 4.0, 13.0],
    ]


def test_osv_filters_by_nomenclature_name(client):
    """Фильтр по ``nomenclatures.name`` оставляет только нужную строку."""
    _fill_storage()

    response = client.post("/api/osv", json={
        "filters": [{
            "filter_name": "nomenclatures.name",
            "filter_value": "milk",
            "filter_type": "equals",
        }],
    })

    assert response.status_code == 200
    rows = response.get_json()["rows"]
    assert [row[0] for row in rows] == ["Milk", "ИТОГО"]
    assert rows[0][4:] == [10.0, 4.0, 6.0]


def test_osv_filters_by_warehouse_name(client):
    """Фильтр по ``warehouses.name`` оставляет только нужный склад."""
    _fill_storage()

    response = client.post("/api/osv", json={
        "filters": [{
            "filter_name": "warehouses.name",
            "filter_value": "auxiliary",
            "filter_type": "like",
        }],
    })

    assert response.status_code == 200
    rows = response.get_json()["rows"]
    assert len(rows) == 2
    assert rows[0][:3] == ["Apple", "Auxiliary warehouse", "liter"]


def test_osv_filters_by_unique_code(client):
    """Фильтр по коду номенклатуры поддерживается."""
    storage = _fill_storage()
    code = next(
        item.unique_code for item in storage.nomenclatures
        if item.name == "Apple"
    )

    response = client.post("/api/osv", json={
        "filters": [{
            "filter_name": "nomenclatures.unique_code",
            "filter_value": code,
            "filter_type": "equals",
        }],
    })

    assert response.status_code == 200
    rows = response.get_json()["rows"]
    assert [row[0] for row in rows] == ["Apple", "ИТОГО"]


def test_osv_filter_not_matched_returns_empty_rows(client):
    """Неподходящий фильтр возвращает пустой список строк."""
    _fill_storage()

    response = client.post("/api/osv", json={
        "filters": [{
            "filter_name": "nomenclatures.name",
            "filter_value": "nonexistent",
            "filter_type": "equals",
        }],
    })

    assert response.status_code == 200
    assert response.get_json()["rows"] == []


def test_osv_invalid_filters_type_returns_400(client):
    """``filters`` должен быть списком."""
    response = client.post("/api/osv", json={"filters": "bad"})

    assert response.status_code == 400


def test_osv_missing_filter_name_returns_400(client):
    """Условие без ``filter_name`` отклоняется."""
    response = client.post("/api/osv", json={
        "filters": [{"filter_value": "milk"}],
    })

    assert response.status_code == 400


def test_osv_unknown_filter_type_returns_400(client):
    """Неизвестный ``filter_type`` отклоняется."""
    response = client.post("/api/osv", json={
        "filters": [{
            "filter_name": "nomenclatures.name",
            "filter_value": "milk",
            "filter_type": "starts_with",
        }],
    })

    assert response.status_code == 400


def test_osv_invalid_json_type_returns_400(client):
    """Тело запроса должно быть JSON-объектом."""
    response = client.post(
        "/api/osv",
        data="[]",
        content_type="application/json",
    )

    assert response.status_code == 400

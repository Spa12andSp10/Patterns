import pytest

from main import api
from Src.Logics.storage_manager import storage_manager
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


@pytest.fixture(scope="module")
def client():
    """Тестовый клиент Flask."""
    with api.app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_storage():
    """Очищает коллекции singleton-хранилища перед тестом."""
    storage = storage_manager()
    for attr in (
        "_groups", "_ranges", "_nomenclature", "_warehouse",
        "_recipes", "_ingredients", "_transactions",
    ):
        setattr(storage, attr, [])
    storage._is_loaded = False
    yield


def _seed_nomenclatures() -> storage_manager:
    """Добавляет три номенклатуры в произвольном порядке."""
    storage = storage_manager()
    group = group_model.create("Dairy products")
    unit = range_model.create("liter", 1.0, None)
    storage.add_group(group)
    storage.add_range(unit)

    for full_name, name in (
        ("Pasteurized milk", "Milk"),
        ("Astrakhan apple", "Apple"),
        ("Banana", "Banana"),
    ):
        storage.add_nomenclature(nomenclature_model.create(
            full_name, name, group, unit, "product",
        ))

    return storage


def _seed_ranges() -> storage_manager:
    """Добавляет единицы измерения с разными коэффициентами."""
    storage = storage_manager()
    for name, factor in (
        ("Gram", 1.0),
        ("Kilogram", 1000.0),
        ("Ton", 1000000.0),
    ):
        storage.add_range(range_model.create(name, factor, None))
    return storage


def _post(client, entity_type: str, filters: list):
    """Отправляет запрос фильтрации."""
    return client.post(
        f"/api/filter/{entity_type}",
        json={"filters": filters},
    )


def _names(response) -> list:
    """Возвращает имена сущностей из ответа фильтрации."""
    return [item["name"] for item in response.get_json()["items"]]


def test_filter_between_numeric(client):
    """BETWEEN по числовому полю оставляет значения в диапазоне."""
    # Подготовка
    _seed_ranges()
    filters = [{
        "filter_name": "conversion_factor",
        "filter_value": "100..2000",
        "filter_type": "between",
    }]

    # Действие
    response = _post(client, "range", filters)

    # Проверки
    assert response.status_code == 200
    assert _names(response) == ["Kilogram"]


def test_filter_between_strings(client):
    """BETWEEN по строковому полю сравнивает без учёта регистра."""
    # Подготовка
    _seed_nomenclatures()
    filters = [{
        "filter_name": "name",
        "filter_value": "apple..banana",
        "filter_type": "between",
    }]

    # Действие
    response = _post(client, "nomenclature", filters)

    # Проверки
    assert response.status_code == 200
    assert _names(response) == ["Apple", "Banana"]


def test_filter_alphabet_sorts_ascending(client):
    """ALPHABET сортирует результат по возрастанию."""
    # Подготовка
    _seed_nomenclatures()
    filters = [{
        "filter_name": "name",
        "filter_type": "alphabet",
    }]

    # Действие
    response = _post(client, "nomenclature", filters)

    # Проверки
    assert response.status_code == 200
    assert _names(response) == ["Apple", "Banana", "Milk"]


def test_filter_reverse_alphabet_sorts_descending(client):
    """Обратный ALPHABET сортирует результат по убыванию."""
    # Подготовка
    _seed_nomenclatures()
    filters = [{
        "filter_name": "name",
        "filter_type": "reverse_alphabet",
    }]

    # Действие
    response = _post(client, "nomenclature", filters)

    # Проверки
    assert response.status_code == 200
    assert _names(response) == ["Milk", "Banana", "Apple"]


def test_filter_alphabet_desc_sorts_descending(client):
    """Канонический тип alphabet_desc работает."""
    # Подготовка
    _seed_nomenclatures()
    filters = [{
        "filter_name": "name",
        "filter_type": "alphabet_desc",
    }]

    # Действие
    response = _post(client, "nomenclature", filters)

    # Проверки
    assert response.status_code == 200
    assert _names(response) == ["Milk", "Banana", "Apple"]


def test_filter_combines_between_and_alphabet(client):
    # Подготовка
    _seed_nomenclatures()
    filters = [
        {
            "filter_name": "name",
            "filter_value": "a..m",
            "filter_type": "between",
        },
        {
            "filter_name": "name",
            "filter_type": "alphabet_desc",
        },
    ]

    # Действие
    response = _post(client, "nomenclature", filters)

    # Проверки
    assert response.status_code == 200
    assert _names(response) == ["Banana", "Apple"]


def test_filter_invalid_between_returns_400(client):
    """Некорректный диапазон возвращает 400 даже без данных."""
    # Подготовка
    filters = [{
        "filter_name": "name",
        "filter_value": "not-a-range",
        "filter_type": "between",
    }]

    # Действие
    response = _post(client, "nomenclature", filters)

    # Проверки
    assert response.status_code == 400


def test_filter_unknown_type_returns_400(client):
    """Неизвестный filter_type отклоняется Connexion."""
    # Подготовка
    filters = [{
        "filter_name": "name",
        "filter_value": "milk",
        "filter_type": "unknown",
    }]

    # Действие
    response = _post(client, "nomenclature", filters)

    # Проверки
    assert response.status_code == 400

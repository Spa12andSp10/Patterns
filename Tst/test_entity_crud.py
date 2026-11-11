import pytest
from flask import Flask

from main import api

from Src.Logics.storage_manager import storage_manager
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model


@pytest.fixture(scope="module")
def client():
    """Возвращает тестовый клиент Flask для отправки HTTP-запросов."""
    with api.app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def clean_storage():
    """Очищает хранилище перед каждым тестом, чтобы тесты не влияли друг на друга."""
    storage = storage_manager()
    storage._groups.clear()
    storage._ranges.clear()
    storage._nomenclature.clear()
    storage._warehouse.clear()
    storage._recipes.clear()
    storage._ingredients.clear()
    yield

def test_create_group_success(client):
    """
    Проверяет успешное создание группы через POST.
    Ожидаемый результат: статус 201, сущность появляется в хранилище.
    """
    # Подготовка
    payload = {"entity_type": "group", "name": "Dairy Products"}

    # Действие
    response = client.post("/api/group", json=payload)

    # Проверки
    assert response.status_code == 201
    assert "Location" in response.headers
    assert len(storage_manager().groups) == 1
    assert storage_manager().groups[0].name == "Dairy Products"


def test_create_group_fail_missing_name(client):
    """
    Проверяет провальное создание группы (отсутствует обязательное поле).
    Ожидаемый результат: статус 400 (ошибка валидации).
    """
    # Подготовка
    payload = {"entity_type": "group"}  # нет поля name

    # Действие
    response = client.post("/api/group", json=payload)

    # Проверки
    assert response.status_code == 400
    assert len(storage_manager().groups) == 0


def test_read_entity_success(client):
    """
    Проверяет получение списка кодов созданной сущности.
    Ожидаемый результат: статус 200, код присутствует в списке.
    """
    # Подготовка
    group = group_model.create("Dairy")
    storage_manager().add_group(group)
    code = group.unique_code

    # Действие
    response = client.get("/api/get_codes?type=group")

    # Проверки
    assert response.status_code == 200
    data = response.get_json()
    assert data["type"] == "group"
    assert any(item["code"] == code for item in data["items"])


def test_read_entity_fail_not_found(client):
    """
    Проверяет провальное чтение несуществующей сущности по коду.
    Ожидаемый результат: статус 404.
    """
    # Подготовка
    fake_code = "nonexistent-code-1234"

    # Действие
    response = client.get(f"/api/get_report_with_type_and_code?type=group&code={fake_code}")

    # Проверки
    assert response.status_code == 404


def test_update_entity_success(client):
    """
    Проверяет успешное обновление (PATCH) имени группы.
    Ожидаемый результат: статус 200, имя изменилось в хранилище.
    """
    # Подготовка
    group = group_model.create("Old Name")
    storage_manager().add_group(group)
    code = group.unique_code
    payload = {"name": "New Name"}

    # Действие
    response = client.patch(f"/api/update/{code}", json=payload)

    # Проверки
    assert response.status_code == 200
    updated = storage_manager().groups[0]
    assert updated.name == "New Name"


def test_update_entity_fail_unique_code(client):
    """
    Проверяет провальное обновление (попытка изменить unique_code).
    Ожидаемый результат: статус 400, имя не изменилось.
    """
    # Подготовка
    group = group_model.create("Old Name")
    storage_manager().add_group(group)
    code = group.unique_code
    payload = {"unique_code": "hacker-code"}  # Запрещено менять

    # Действие
    response = client.patch(f"/api/update/{code}", json=payload)

    # Проверки
    assert response.status_code == 400
    assert storage_manager().groups[0].unique_code == code


def test_delete_entity_success(client):
    """
    Проверяет успешное удаление несвязанной группы.
    Ожидаемый результат: статус 204, группа исчезла из хранилища.
    """
    # Подготовка
    group = group_model.create("To Be Deleted")
    storage_manager().add_group(group)
    code = group.unique_code

    # Действие
    response = client.delete(f"/api/delete/{code}")

    # Проверки
    assert response.status_code == 204
    assert len(storage_manager().groups) == 0


def test_delete_entity_fail_referenced(client):
    """
    Проверяет провальное удаление группы, на которую ссылается номенклатура.
    Ожидаемый результат: статус 409 (Conflict), группа осталась в хранилище.
    """
    # Подготовка
    group = group_model.create("Dairy")
    storage_manager().add_group(group)

    gram = range_model.create_gram()
    storage_manager().add_range(gram)

    from Src.Models.nomenclature_model import nomenclature_model
    nom = nomenclature_model.create(
        full_name="Milk",
        name="Milk",
        group=group,
        range=gram,
        item_type="product",
    )
    storage_manager().add_nomenclature(nom)
    code = group.unique_code

    # Действие
    response = client.delete(f"/api/delete/{code}")

    # Проверки
    assert response.status_code == 409
    assert "Нельзя удалить" in response.data.decode("utf-8")
    assert len(storage_manager().groups) == 1
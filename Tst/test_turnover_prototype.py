from datetime import datetime

from Src.Dtos.filter_dto import filter_dto
from Src.Logics.turnover_prototype import turnover_prototype
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.transaction_model import transaction_model
from Src.Models.warehouse_model import warehouse_model


def _references():
    """Создаёт справочники для тестовых транзакций."""
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
    return milk, apple, main, auxiliary, unit


def _transaction(nomenclature, warehouse, unit, value, day=1):
    """Создаёт транзакцию за январь 2026 года."""
    return transaction_model.create(
        nomenclature, warehouse, unit, value, datetime(2026, 1, day),
    )


def test_clone_filters_by_nomenclature_name():
    """clone фильтрует транзакции по вложенному пути номенклатуры."""
    # Подготовка
    milk, apple, main, _, unit = _references()
    data = [
        _transaction(milk, main, unit, 10, 1),
        _transaction(apple, main, unit, 7, 2),
    ]
    filters = filter_dto.path_filter("nomenclatures.name", "milk")

    # Действие
    result = turnover_prototype(data).clone(filters)

    # Проверки
    assert len(result.data) == 1
    assert result.data[0].nomenclatures.name == "Milk"


def test_clone_filters_by_warehouse_name():
    """clone фильтрует транзакции по вложенному пути склада."""
    # Подготовка
    milk, _, main, auxiliary, unit = _references()
    data = [
        _transaction(milk, main, unit, 10, 1),
        _transaction(milk, auxiliary, unit, 5, 2),
    ]
    filters = filter_dto.path_filter("warehouses.name", "auxiliary")

    # Действие
    result = turnover_prototype(data).clone(filters)

    # Проверки
    assert [item.warehouses.name for item in result.data] == [
        "Auxiliary warehouse",
    ]
    assert result.data[0].value == 5.0


def test_clone_does_not_mutate_source():
    """clone не меняет исходный прототип."""
    # Подготовка
    milk, apple, main, _, unit = _references()
    data = [
        _transaction(milk, main, unit, 10, 1),
        _transaction(apple, main, unit, 7, 2),
    ]
    source = turnover_prototype(data)

    # Действие
    source.clone(filter_dto.name_filter("milk"))

    # Проверки
    assert len(source.data) == 2


def test_clone_without_filters_copies_data():
    """clone без фильтров возвращает копию данных."""
    # Подготовка
    milk, _, main, _, unit = _references()
    source = turnover_prototype([_transaction(milk, main, unit, 1)])

    # Действие
    copy = source.clone()

    # Проверки
    assert copy is not source
    assert copy.data == source.data

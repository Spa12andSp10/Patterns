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


def test_build_empty_returns_only_header():
    """Без транзакций возвращается пустая таблица с заголовком."""
    report = turnover_prototype([]).build()

    assert report.header == turnover_prototype.HEADER
    assert report.rows == []


def test_build_groups_debit_and_credit():
    """Приход и расход группируются в одну строку."""
    milk, _, main, _, unit = _references()
    data = [
        _transaction(milk, main, unit, 10, 1),
        _transaction(milk, main, unit, -4, 2),
    ]

    report = turnover_prototype(data).build()

    assert report.rows == [
        ["Milk", "Main warehouse", "liter", 0.0, 10.0, 4.0, 6.0],
        ["ИТОГО", "", "", 0.0, 10.0, 4.0, 6.0],
    ]


def test_build_separates_groups_by_warehouse():
    """Одинаковая номенклатура на разных складах даёт разные строки."""
    milk, _, main, auxiliary, unit = _references()
    data = [
        _transaction(milk, main, unit, 10, 1),
        _transaction(milk, auxiliary, unit, -3, 2),
    ]

    report = turnover_prototype(data).build()

    assert len(report.rows) == 3
    assert report.rows[0] == [
        "Milk", "Main warehouse", "liter", 0.0, 10.0, 0.0, 10.0,
    ]
    assert report.rows[1] == [
        "Milk", "Auxiliary warehouse", "liter", 0.0, 0.0, 3.0, -3.0,
    ]
    assert report.rows[2] == [
        "ИТОГО", "", "", 0.0, 10.0, 3.0, 7.0,
    ]


def test_build_separates_groups_by_nomenclature():
    """Разная номенклатура на одном складе даёт разные строки."""
    milk, apple, main, _, unit = _references()
    data = [
        _transaction(milk, main, unit, 4, 1),
        _transaction(apple, main, unit, 7, 2),
    ]

    report = turnover_prototype(data).build()

    assert [row[0] for row in report.rows] == ["Milk", "Apple", "ИТОГО"]


def test_build_rounds_values_to_two_digits():
    """Дробные значения округляются до двух знаков."""
    milk, _, main, _, unit = _references()
    data = [
        _transaction(milk, main, unit, 1.005, 1),
        _transaction(milk, main, unit, 0.004, 2),
    ]

    report = turnover_prototype(data).build()

    assert report.rows[0][4] == 1.01
    assert report.rows[0][6] == 1.01


def test_clone_filters_by_nomenclature_name():
    """clone фильтрует транзакции по вложенному пути номенклатуры."""
    milk, apple, main, _, unit = _references()
    data = [
        _transaction(milk, main, unit, 10, 1),
        _transaction(apple, main, unit, 7, 2),
    ]
    filters = filter_dto.path_filter("nomenclatures.name", "milk")

    report = turnover_prototype(data).clone(filters).build()

    assert [row[0] for row in report.rows] == ["Milk", "ИТОГО"]
    assert report.rows[0][4] == 10.0


def test_clone_filters_by_warehouse_name():
    """clone фильтрует транзакции по вложенному пути склада."""
    milk, _, main, auxiliary, unit = _references()
    data = [
        _transaction(milk, main, unit, 10, 1),
        _transaction(milk, auxiliary, unit, 5, 2),
    ]
    filters = filter_dto.path_filter("warehouses.name", "auxiliary")

    report = turnover_prototype(data).clone(filters).build()

    assert len(report.rows) == 2
    assert report.rows[0][1] == "Auxiliary warehouse"
    assert report.rows[0][4] == 5.0


def test_clone_does_not_mutate_source():
    """clone не меняет исходный прототип."""
    milk, apple, main, _, unit = _references()
    data = [
        _transaction(milk, main, unit, 10, 1),
        _transaction(apple, main, unit, 7, 2),
    ]
    source = turnover_prototype(data)

    source.clone(filter_dto.name_filter("milk"))

    assert len(source.data) == 2


def test_clone_without_filters_copies_data():
    """clone без фильтров возвращает копию данных."""
    milk, _, main, _, unit = _references()
    source = turnover_prototype([_transaction(milk, main, unit, 1)])

    copy = source.clone()

    assert copy is not source
    assert copy.data == source.data

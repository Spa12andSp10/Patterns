from datetime import datetime

import pytest

from Src.Dtos.report_data_dto import report_data_dto
from Src.Logics.report_data_extractor import report_data_extractor
from Src.Models.technicalmap_model import technicalmap_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.transaction_model import transaction_model
from Src.Models.warehouse_model import warehouse_model
from Src.Core.exception import arguments_exeption


def _make_recipe() -> technicalmap_model:
    """Собирает тестовый рецепт напрямую."""
    return technicalmap_model.create(
        ingredients=[
            ingredient_model("Durum wheat pasta", 400.0, 10.4, 1.1, 69.7, 1.0, "product"),
            ingredient_model("Beef",              500.0, 18.0, 14.0, 0.0, 0.7, "product"),
            ingredient_model("Milk",              300.0,  2.9,  3.2, 4.7, 1.0, "product"),
            ingredient_model("Apple",             200.0,  0.4,  0.4, 9.8, 0.9, "product"),
            ingredient_model("Onion",             100.0,  1.4,  0.0, 10.4, 0.9, "product"),
            ingredient_model("Sunflower oil",      30.0,  0.0, 99.9, 0.0, 1.0, "product"),
            ingredient_model("Salt",                5.0,  0.0,  0.0, 0.0, 1.0, "product"),
            ingredient_model("Pepper",              2.0,  0.0,  0.0, 0.0, 1.0, "product"),
        ],
        preparation_method={},
        description="Тестовый рецепт",
        time="60",
        name="Test recipe",
    )


def _extract(source):
    """Возвращает (header, rows) из DTO."""
    dto = report_data_extractor.extract(source)
    return dto.header, dto.rows


def test_valid_extract_recipe_headers():
    """
    Проверяет заголовки рецепта.
    Ожидаемый результат: 7 колонок с полями ингредиентов и способом приготовления.
    """
    # Подготовка
    recipe = _make_recipe()

    # Действие
    header, data = _extract(recipe)

    # Проверки
    expected_header = ["ingredient", "brutto", "proteins", "fats",
                       "carbohydrates", "coef", "method"]
    assert header == expected_header
    assert len(header) == 7


def test_valid_extract_recipe_row_count():
    """
    Проверяет количество строк рецепта.
    Ожидаемый результат: 8 строк по числу ингредиентов.
    """
    # Подготовка
    recipe = _make_recipe()

    # Действие
    header, data = _extract(recipe)

    # Проверки
    assert len(data) == 8


def test_valid_extract_recipe_first_row_values():
    """
    Проверяет значения первой строки рецепта.
    Ожидаемый результат: наименование, бруто, БЖУ, коэффициент и способ
    приготовления «Durum wheat pasta».
    """
    # Подготовка
    recipe = _make_recipe()

    # Действие
    header, data = _extract(recipe)
    first_row = data[0]

    # Проверки
    assert first_row[0] == "Durum wheat pasta"
    assert first_row[1] == 400.0
    assert first_row[2] == 10.4
    assert first_row[3] == 1.1
    assert first_row[4] == 69.7
    assert first_row[5] == 1.0
    assert first_row[6] == ""


def test_valid_extract_nomenclature_headers():
    """
    Проверяет заголовки номенклатуры.
    Ожидаемый результат: 6 колонок.
    """
    # Подготовка
    milk = nomenclature_model.create(
        full_name="Pasteurized milk 3.2%",
        name="Milk",
        group=group_model.create("Dairy products"),
        range=range_model.create_liter(),
        item_type="product",
    )

    # Действие
    header, data = _extract(milk)

    # Проверки
    expected_header = ["name", "full_name", "group", "range",
                       "item_type", "unique_code"]
    assert header == expected_header
    assert len(header) == 6


def test_valid_extract_nomenclature_data_values():
    """
    Проверяет данные номенклатуры (Milk).
    Ожидаемый результат: наименование, полное имя, группа и единица соответствуют.
    """
    # Подготовка
    milk = nomenclature_model.create(
        full_name="Pasteurized milk 3.2%",
        name="Milk",
        group=group_model.create("Dairy products"),
        range=range_model.create_liter(),
        item_type="product",
    )

    # Действие
    header, data = _extract(milk)
    row = data[0]

    # Проверки
    assert len(data) == 1
    assert row[0] == "Milk"
    assert row[1] == "Pasteurized milk 3.2%"
    assert row[2] == "Dairy products"
    assert row[3] == "Liter"
    assert row[4] == "product"
    assert row[5] == milk.unique_code


def test_valid_extract_nomenclature_no_group_and_range():
    """
    Проверяет обработку номенклатуры без группы и единицы.
    Ожидаемый результат: в колонках group и range выводятся пустые строки.
    """
    # Подготовка
    empty_nom = nomenclature_model.create(
        full_name="Test Full Name",
        name="Test",
        group=None,
        range=None,
        item_type="product",
    )

    # Действие
    header, data = _extract(empty_nom)
    row = data[0]

    # Проверки
    assert row[2] == ""
    assert row[3] == ""
    assert row[4] == "product"
    assert row[5] == empty_nom.unique_code


def test_valid_extract_range_headers():
    """
    Проверяет заголовки единицы измерения.
    Ожидаемый результат: 4 колонки.
    """
    # Подготовка
    kg = range_model.create_kilogram()

    # Действие
    header, data = _extract(kg)

    # Проверки
    expected_header = ["name", "conversion_factor", "base", "unique_code"]
    assert header == expected_header
    assert len(header) == 4


def test_valid_extract_range_data_values():
    """
    Проверяет данные единицы измерения (Kilogram).
    Ожидаемый результат: коэффициент 1000 и база 'Gram'.
    """
    # Подготовка
    kg = range_model.create_kilogram()

    # Действие
    header, data = _extract(kg)
    row = data[0]

    # Проверки
    assert len(data) == 1
    assert row[0] == "Kilogram"
    assert row[1] == 1000.0
    assert row[2] == "Gram"
    assert row[3] == kg.unique_code


def test_valid_extract_range_no_base():
    """
    Проверяет обработку единицы измерения без базы.
    Ожидаемый результат: в колонке base выводится пустая строка.
    """
    # Подготовка
    gram = range_model.create_gram()

    # Действие
    header, data = _extract(gram)
    row = data[0]

    # Проверки
    assert row[2] == ""
    assert row[3] == gram.unique_code


def test_invalid_extract_unsupported_type_raises_error():
    """
    Проверяет реакцию на неподдерживаемый тип.
    Ожидаемый результат: возникает arguments_exeption.
    """
    # Подготовка
    class FakeModel:
        pass

    fake = FakeModel()

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        report_data_extractor.extract(fake)

    # Проверки
    assert "Неверный тип формирования отчета" in str(exc_info.value)


def _transaction_references():
    """Создаёт номенклатуры, склады и единицу для тестов ОСВ."""
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


def test_extract_accepts_ready_report_data_dto():
    """Уже готовый report_data_dto возвращается без пересборки."""
    # Подготовка
    table = report_data_dto.create(header=["name"], rows=[["Milk"]])

    # Действие
    result = report_data_extractor.extract(table)

    # Проверки
    assert result is table


def test_extract_transactions_empty_returns_only_header():
    """Без транзакций возвращается пустая таблица с заголовком."""
    # Подготовка
    transactions = []

    # Действие
    header, rows = _extract(transactions)

    # Проверки
    assert header == report_data_extractor.TRANSACTION_HEADER
    assert rows == []


def test_extract_transactions_groups_debit_and_credit():
    """Приход и расход группируются в одну строку."""
    # Подготовка
    milk, _, main, _, unit = _transaction_references()
    transactions = [
        _transaction(milk, main, unit, 10, 1),
        _transaction(milk, main, unit, -4, 2),
    ]

    # Действие
    header, rows = _extract(transactions)

    # Проверки
    assert header == report_data_extractor.TRANSACTION_HEADER
    assert rows == [
        ["Milk", "Main warehouse", "liter", 0.0, 10.0, 4.0, 6.0],
        ["ИТОГО", "", "", 0.0, 10.0, 4.0, 6.0],
    ]


def test_extract_transactions_separates_warehouses():
    """Одинаковая номенклатура на разных складах даёт разные строки."""
    # Подготовка
    milk, _, main, auxiliary, unit = _transaction_references()
    transactions = [
        _transaction(milk, main, unit, 10, 1),
        _transaction(milk, auxiliary, unit, -3, 2),
    ]

    # Действие
    header, rows = _extract(transactions)

    # Проверки
    assert len(rows) == 3
    assert rows[0] == [
        "Milk", "Main warehouse", "liter", 0.0, 10.0, 0.0, 10.0,
    ]
    assert rows[1] == [
        "Milk", "Auxiliary warehouse", "liter", 0.0, 0.0, 3.0, -3.0,
    ]
    assert rows[2] == ["ИТОГО", "", "", 0.0, 10.0, 3.0, 7.0]


def test_extract_transactions_separates_nomenclatures():
    """Разная номенклатура на одном складе даёт разные строки."""
    # Подготовка
    milk, apple, main, _, unit = _transaction_references()
    transactions = [
        _transaction(milk, main, unit, 4, 1),
        _transaction(apple, main, unit, 7, 2),
    ]

    # Действие
    header, rows = _extract(transactions)

    # Проверки
    assert [row[0] for row in rows] == ["Milk", "Apple", "ИТОГО"]


def test_extract_transactions_rounds_values_to_two_digits():
    """Дробные значения округляются до двух знаков."""
    # Подготовка
    milk, _, main, _, unit = _transaction_references()
    transactions = [
        _transaction(milk, main, unit, 1.005, 1),
        _transaction(milk, main, unit, 0.004, 2),
    ]

    # Действие
    header, rows = _extract(transactions)

    # Проверки
    assert rows[0][4] == 1.01
    assert rows[0][6] == 1.01

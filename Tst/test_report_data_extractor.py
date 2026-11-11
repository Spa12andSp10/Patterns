import pytest

from Src.Logics.report_data_extractor import report_data_extractor
from Src.Models.technicalmap_model import technicalmap_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
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
    """Хелпер: возвращает (header, rows) из DTO."""
    dto = report_data_extractor.extract(source)
    return dto.header, dto.rows


def test_valid_extract_recipe_headers():
    """
    Проверяет заголовки рецепта.
    Ожидаемый результат: 7 колонок, соответствующих рецепту.
    """
    # Подготовка
    recipe = _make_recipe()

    # Действие
    header, data = _extract(recipe)

    # Проверки
    expected_header = ["Code", "Name", "Brutto", "Netto",
                       "Proteins", "Fats", "Carbohydrates"]
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
    Ожидаемый результат: наименование, брутто, нетто и БЖУ «Durum wheat pasta».
    """
    # Подготовка
    recipe = _make_recipe()

    # Действие
    header, data = _extract(recipe)
    first_row = data[0]

    # Проверки
    assert isinstance(first_row[0], str)
    assert len(first_row[0]) > 0
    assert first_row[1] == "Durum wheat pasta"
    assert first_row[2] == 400.0
    assert first_row[3] == 400.0
    assert first_row[4] == 10.4
    assert first_row[5] == 1.1
    assert first_row[6] == 69.7


def test_valid_extract_nomenclature_headers():
    """
    Проверяет заголовки номенклатуры.
    Ожидаемый результат: 5 колонок.
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
    expected_header = ["Code", "Name", "Full name", "Group", "Range"]
    assert header == expected_header
    assert len(header) == 5


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
    assert row[0] == milk.unique_code
    assert row[1] == "Milk"
    assert row[2] == "Pasteurized milk 3.2%"
    assert row[3] == "Dairy products"
    assert row[4] == "Liter"


def test_valid_extract_nomenclature_no_group_and_range():
    """
    Проверяет обработку номенклатуры без группы и единицы.
    Ожидаемый результат: в колонках Group и Range выводится 'Not found'.
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
    assert row[3] == "Not found"
    assert row[4] == "Not found"


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
    expected_header = ["Code", "Name", "Coef", "Base"]
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
    assert row[0] == kg.unique_code
    assert row[1] == "Kilogram"
    assert row[2] == 1000.0
    assert row[3] == "Gram"


def test_valid_extract_range_no_base():
    """
    Проверяет обработку базовой единицы.
    Ожидаемый результат: в колонке Base выводится 'Not found'.
    """
    # Подготовка
    gram = range_model.create_gram()

    # Действие
    header, data = _extract(gram)
    row = data[0]

    # Проверки
    assert row[3] == "Not found"


def test_invalid_extract_unsupported_type_raises_error():
    """
    Проверяет реакцию на неподдерживаемый тип.
    Ожидаемый результат: возникает arguments_exeption.
    """
    # Подготовка
    class FakeModel:
        pass

    fake = FakeModel()

    # Действие и проверки
    with pytest.raises(arguments_exeption) as exc_info:
        report_data_extractor.extract(fake)

    assert "Неверный тип формирования отчета" in str(exc_info.value)
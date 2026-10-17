import pytest

from pathlib import Path

from Src.Logics.report_data_extractor import report_data_extractor
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.exception import arguments_exeption


def _storage_path() -> str:
    """Путь к storage_data.json (эталонные данные)."""
    return str(Path(__file__).resolve().parent / "storage_data.json")


@pytest.fixture(autouse=True)
def reset_storage():
    """Сбрасывает состояние singleton-хранилища перед каждым тестом."""
    sm = storage_manager()
    sm._groups = []
    sm._ranges = []
    sm._nomenclature = []
    sm._warehouse = []
    sm._recipes = []
    sm._is_loaded = False
    sm._data = {}
    yield


def test_valid_extract_recipe_headers():
    """
    Проверяет, что заголовки для рецепта сформированы корректно.
    Ожидаемый результат: заголовки соответствуют 7 колонкам рецепта.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]

    # Действие
    header, data = report_data_extractor.extract(recipe)

    # Проверки
    expected_header = ["Code", "Name", "Brutto", "Netto", "Proteins", "Fats", "Carbohydrates"]
    assert header == expected_header
    assert len(header) == 7


def test_valid_extract_recipe_row_count():
    """
    Проверяет, что количество строк данных совпадает с количеством ингредиентов.
    Ожидаемый результат: количество строк равно 8 (по числу ингредиентов в JSON).
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]

    # Действие
    header, data = report_data_extractor.extract(recipe)

    # Проверки
    assert len(data) == 8


def test_valid_extract_recipe_first_row_values():
    """
    Проверяет, что значения в первой строке данных корректны (Durum wheat pasta).
    Ожидаемый результат: наименование, брутто, нетто и БЖУ соответствуют JSON.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]

    # Действие
    header, data = report_data_extractor.extract(recipe)
    first_row = data[0]

    # Проверки
    assert isinstance(first_row[0], str)  # Уникальный код
    assert len(first_row[0]) > 0
    assert first_row[1] == "Durum wheat pasta"
    assert first_row[2] == 400.0  # Брутто
    assert first_row[3] == 400.0  # Нетто (400 * 1.0)
    assert first_row[4] == 10.4   # Белки
    assert first_row[5] == 1.1    # Жиры
    assert first_row[6] == 69.7   # Углеводы


def test_valid_extract_nomenclature_headers():
    """
    Проверяет, что заголовки для номенклатуры сформированы корректно.
    Ожидаемый результат: заголовки соответствуют 5 колонкам номенклатуры.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    milk = next(n for n in sm.nomenclatures if n.name == "Milk")

    # Действие
    header, data = report_data_extractor.extract(milk)

    # Проверки
    expected_header = ["Code", "Name", "Full name", "Group", "Range"]
    assert header == expected_header
    assert len(header) == 5


def test_valid_extract_nomenclature_data_values():
    """
    Проверяет, что данные номенклатуры (Milk) извлечены верно.
    Ожидаемый результат: наименование, полное имя, группа и единица измерения
    соответствуют JSON.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    milk = next(n for n in sm.nomenclatures if n.name == "Milk")

    # Действие
    header, data = report_data_extractor.extract(milk)
    row = data[0]

    # Проверки
    assert len(data) == 1  # Для номенклатуры всегда одна строка
    assert row[0] == milk.unique_code
    assert row[1] == "Milk"
    assert row[2] == "Pasteurized milk 3.2%"
    assert row[3] == "Dairy products"
    assert row[4] == "liter"


def test_valid_extract_nomenclature_no_group_and_range():
    """
    Проверяет обработку номенклатуры без группы и единицы измерения.
    Ожидаемый результат: в колонках Group и Range выводится 'Not found'.
    """
    # Подготовка
    empty_nom = nomenclature_model.create(
        full_name="Test Full Name",
        name="Test",
        group=None,
        range=None,
    )

    # Действие
    header, data = report_data_extractor.extract(empty_nom)
    row = data[0]

    # Проверки
    assert row[3] == "Not found"
    assert row[4] == "Not found"


def test_valid_extract_range_headers():
    """
    Проверяет, что заголовки для единицы измерения сформированы корректно.
    Ожидаемый результат: заголовки соответствуют 4 колонкам единицы измерения.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    kg = next(r for r in sm.ranges if r.name == "kilogram")

    # Действие
    header, data = report_data_extractor.extract(kg)

    # Проверки
    expected_header = ["Code", "Name", "Coef", "Base"]
    assert header == expected_header
    assert len(header) == 4


def test_valid_extract_range_data_values():
    """
    Проверяет, что данные единицы измерения (Kilogram) извлечены верно.
    Ожидаемый результат: коэффициент 1000 и базовая единица 'gram'
    соответствуют JSON.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    kg = next(r for r in sm.ranges if r.name == "kilogram")

    # Действие
    header, data = report_data_extractor.extract(kg)
    row = data[0]

    # Проверки
    assert len(data) == 1
    assert row[0] == kg.unique_code
    assert row[1] == "kilogram"
    assert row[2] == 1000.0
    assert row[3] == "gram"


def test_valid_extract_range_no_base():
    """
    Проверяет обработку базовой единицы измерения (без базы).
    Ожидаемый результат: в колонке Base выводится 'Not found'.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    gram = next(r for r in sm.ranges if r.name == "gram")

    # Действие
    header, data = report_data_extractor.extract(gram)
    row = data[0]

    # Проверки
    assert row[3] == "Not found"

def test_invalid_extract_unsupported_type_raises_error():
    """
    Проверяет, что при передаче объекта неподдерживаемого типа бросается исключение.
    Ожидаемый результат: возникает arguments_exeption с сообщением о неверном типе.
    """
    # Подготовка
    class FakeModel:
        pass

    fake = FakeModel()

    # Действие и проверки
    with pytest.raises(arguments_exeption) as exc_info:
        report_data_extractor.extract(fake)

    assert "Неверный тип формирования отчета" in str(exc_info.value)
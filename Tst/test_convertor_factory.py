import json
from datetime import date, datetime

import pytest

from Src.Logics.convert_factory import convert_factory
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


def _make_composite():
    """Создаёт тестовую модель со всеми тремя видами полей."""

    class Composite:
        @property
        def name(self):
            return "composite"

        @property
        def count(self):
            return 7

        @property
        def created_at(self):
            return datetime(2024, 5, 17, 10, 0)

        @property
        def expires_on(self):
            return date(2025, 1, 1)

        @property
        def group(self):
            return group_model.create(name="Dairy")

        @property
        def range(self):
            return range_model.create_liter()

    return Composite()


def test_valid_result_factory_basic_primitive():
    """
    Проверяет разбор примитива фабрикой.
    Ожидаемый результат: словарь {"value": <число>}.
    """
    # Подготовка
    factory = convert_factory.create_default()
    value = 42

    # Действие
    result = factory.convert(value)

    # Проверки
    assert result == {"value": 42}


def test_valid_result_factory_string_primitive():
    """
    Проверяет разбор строкового примитива фабрикой.
    Ожидаемый результат: словарь {"value": <строка>}.
    """
    # Подготовка
    factory = convert_factory.create_default()
    value = "hello"

    # Действие
    result = factory.convert(value)

    # Проверки
    assert result == {"value": "hello"}


def test_valid_result_factory_datetime_primitive():
    """
    Проверяет разбор одиночной даты фабрикой.
    Ожидаемый результат: словарь {"value": "<ISO-строка>"}.
    """
    # Подготовка
    factory = convert_factory.create_default()
    value = datetime(2024, 5, 17, 12, 30)

    # Действие
    result = factory.convert(value)

    # Проверки
    assert result == {"value": "2024-05-17T12:30:00"}


def test_valid_result_factory_date_primitive():
    """
    Проверяет разбор одиночного date фабрикой.
    Ожидаемый результат: словарь {"value": "<ISO-строка>"}.
    """
    # Подготовка
    factory = convert_factory.create_default()
    value = date(2024, 5, 17)

    # Действие
    result = factory.convert(value)

    # Проверки
    assert result == {"value": "2024-05-17"}


def test_valid_result_factory_reference_model():
    """
    Проверяет разбор одиночной ссылочной модели фабрикой.
    Ожидаемый результат: компактное описание {unique_code, type, name}.
    """
    # Подготовка
    factory = convert_factory.create_default()
    group = group_model.create(name="Dairy products")

    # Действие
    result = factory.convert(group)

    # Проверки
    assert result["name"] == "Dairy products"
    assert result["unique_code"] == group.unique_code
    assert result["item_type"] == ""
    assert "max_lenght" in result


def test_valid_result_factory_nomenclature():
    """
    Проверяет разбор номенклатуры фабрикой: простые поля + ссылки.
    Ожидаемый результат: name/full_name/item_type — значения,
    group/range — компактные описания.
    """
    # Подготовка
    factory = convert_factory.create_default()
    nom = nomenclature_model.create(
        full_name="Pasteurized milk 3.2%",
        name="Milk",
        group=group_model.create(name="Dairy products"),
        range=range_model.create_liter(),
        item_type="product",
    )

    # Действие
    result = factory.convert(nom)

    # Проверки
    assert result["name"] == "Milk"
    assert result["full_name"] == "Pasteurized milk 3.2%"
    assert result["item_type"] == "product"
    assert result["group"]["name"] == "Dairy products"
    assert result["range"]["name"] == "Liter"

    assert isinstance(result["range"]["base"], dict)
    assert result["range"]["base"]["name"] == "Milliliter"
    assert "base" not in result["range"]["base"]

def test_valid_result_factory_skips_none():
    """
    Проверяет, что поля со значением None не попадают в результат.
    Ожидаемый результат: у грамма нет ключа "base".
    """
    # Подготовка
    factory = convert_factory.create_default()
    gram = range_model.create_gram()

    # Действие
    result = factory.convert(gram)

    # Проверки
    assert "base" not in result
    assert result["name"] == "Gram"


def test_valid_result_factory_list():
    """
    Проверяет разбор списка примитивов фабрикой.
    Ожидаемый результат: ключи-индексы "0", "1", "2".
    """
    # Подготовка
    factory = convert_factory.create_default()
    source = [10, "two", 3.0]

    # Действие
    result = factory.convert(source)

    # Проверки
    assert result == {
        "0": {"value": 10},
        "1": {"value": "two"},
        "2": {"value": 3.0},
    }


def test_valid_result_factory_dict():
    """
    Проверяет разбор словаря фабрикой.
    Ожидаемый результат: ключи сохранены, значения разобраны.
    """
    # Подготовка
    factory = convert_factory.create_default()
    source = {"a": 1, "b": "x"}

    # Действие
    result = factory.convert(source)

    # Проверки
    assert result == {"a": {"value": 1}, "b": {"value": "x"}}


def test_valid_result_factory_list_of_models():
    """
    Проверяет разбор списка моделей фабрикой.
    Ожидаемый результат: каждый элемент — компактное описание.
    """
    # Подготовка
    factory = convert_factory.create_default()
    source = [
        group_model.create(name="Dairy"),
        group_model.create(name="Meat"),
    ]

    # Действие
    result = factory.convert(source)

    # Проверки
    assert result["0"]["name"] == "Dairy"
    assert result["1"]["name"] == "Meat"


def test_valid_result_factory_composite():
    """
    Проверяет разбор составного объекта (простые + даты + ссылки).
    Ожидаемый результат: все три вида полей в одном словаре.
    """
    # Подготовка
    factory = convert_factory.create_default()
    source = _make_composite()

    # Действие
    result = factory.convert(source)

    # Проверки
    assert result["name"] == "composite"
    assert result["count"] == 7
    assert result["created_at"] == "2024-05-17T10:00:00"
    assert result["expires_on"] == "2025-01-01"
    assert result["group"]["name"] == "Dairy"
    assert result["range"]["name"] == "Liter"


def test_valid_result_factory_nested_list_of_models():
    """
    Проверяет вложенный список моделей внутри модели.
    Ожидаемый результат: список сохранён по индексам,
    каждый элемент — компактное описание.
    """
    # Подготовка
    factory = convert_factory.create_default()

    class WithList:
        @property
        def items(self):
            return [
                group_model.create(name="A"),
                group_model.create(name="B"),
            ]

    source = WithList()

    # Действие
    result = factory.convert(source)

    # Проверки
    assert result["items"]["0"]["name"] == "A"
    assert result["items"]["1"]["name"] == "B"


def test_valid_result_factory_cycle_protection():
    """
    Проверяет защиту от циклических ссылок.
    Ожидаемый результат: вызов не уходит в бесконечную рекурсию,
    повторная модель отдаётся компактным описанием.
    """
    # Подготовка
    factory = convert_factory.create_default()
    gram = range_model.create_gram()
    gram.base = gram   # патологический цикл: base → сам себя

    # Действие
    result = factory.convert(gram)

    # Проверки
    # Главное — не зависли. base описан компактно.
    assert result["name"] == "Gram"
    assert "base" in result


def test_valid_result_factory_chain_not_cycle():
    """
    Проверяет цепочку range_model (tonna → kilogram → gram) без цикла.
    Ожидаемый результат: цепочка раскрывается, base — компактное описание.
    """
    # Подготовка
    factory = convert_factory.create_default()
    gram = range_model.create_gram()
    kg = range_model.create_kilogram(base=gram)
    tonna = range_model.create_tonna(base=kg)

    # Действие
    result = factory.convert(tonna)

    # Проверки
    assert result["name"] == "Tonna"
    # base — ссылка, отдаётся компактным описанием, не раскрывается.
    assert result["base"]["name"] == "Kilogram"


def test_valid_result_factory_to_json_roundtrip():
    """
    Проверяет JSON-сериализацию результата фабрики.
    Ожидаемый результат: json.loads(to_json(data)) == data.
    """
    # Подготовка
    factory = convert_factory.create_default()
    data = factory.convert(_make_composite())

    # Действие
    text = factory.to_json(data)
    parsed = json.loads(text)

    # Проверки
    assert parsed["name"] == "composite"
    assert parsed["created_at"] == "2024-05-17T10:00:00"
    assert parsed["group"]["name"] == "Dairy"


def test_valid_result_factory_to_json_nomenclature():
    """
    Проверяет, что номенклатура сериализуется в валидный JSON.
    Ожидаемый результат: json.loads не падает, ссылки сохранены.
    """
    # Подготовка
    factory = convert_factory.create_default()
    nom = nomenclature_model.create(
        full_name="Milk",
        name="Milk",
        group=group_model.create(name="Dairy"),
        range=range_model.create_liter(),
        item_type="product",
    )

    # Действие
    text = factory.to_json(factory.convert(nom))
    parsed = json.loads(text)

    # Проверки
    assert parsed["name"] == "Milk"
    assert parsed["group"]["name"] == "Dairy"
    assert parsed["range"]["name"] == "Liter"


def test_valid_result_factory_to_json_list():
    """
    Проверяет JSON-сериализацию списка.
    Ожидаемый результат: JSON-объект с ключами-индексами.
    """
    # Подготовка
    factory = convert_factory.create_default()
    data = factory.convert([1, "two", datetime(2024, 1, 1)])

    # Действие
    text = factory.to_json(data)
    parsed = json.loads(text)

    # Проверки
    assert parsed["0"] == {"value": 1}
    assert parsed["1"] == {"value": "two"}
    assert parsed["2"] == {"value": "2024-01-01T00:00:00"}
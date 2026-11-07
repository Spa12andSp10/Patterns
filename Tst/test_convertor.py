import json
from datetime import date, datetime, time, timedelta

import pytest

from Src.Core.exception import arguments_exeption
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
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


# --- basic_convertor ---

def test_valid_result_basic_string():
    """
    Проверяет конвертацию строкового примитива.
    Ожидаемый результат: словарь {"value": <строка>}.
    """
    # Подготовка
    conv = basic_convertor()
    value = "hello"

    # Действие
    result = conv.convert(value)

    # Проверки
    assert result == {"value": "hello"}


def test_valid_result_basic_int():
    """
    Проверяет конвертацию целочисленного примитива.
    Ожидаемый результат: словарь {"value": <число>}.
    """
    # Подготовка
    conv = basic_convertor()
    value = 42

    # Действие
    result = conv.convert(value)

    # Проверки
    assert result == {"value": 42}


def test_valid_result_basic_float():
    """
    Проверяет конвертацию вещественного примитива.
    Ожидаемый результат: словарь {"value": <число>}.
    """
    # Подготовка
    conv = basic_convertor()
    value = 3.14

    # Действие
    result = conv.convert(value)

    # Проверки
    assert result == {"value": 3.14}


def test_valid_result_basic_zero():
    """
    Проверяет, что ноль считается валидным простым значением.
    Ожидаемый результат: словарь {"value": 0}.
    """
    # Подготовка
    conv = basic_convertor()
    value = 0

    # Действие
    result = conv.convert(value)

    # Проверки
    assert result == {"value": 0}


def test_valid_result_basic_empty_string():
    """
    Проверяет, что пустая строка-примитив — это значение, а не ошибка.
    Ожидаемый результат: словарь {"value": ""}.
    """
    # Подготовка
    conv = basic_convertor()
    value = ""

    # Действие
    result = conv.convert(value)

    # Проверки
    assert result == {"value": ""}


def test_invalid_result_basic_none():
    """
    Проверяет реакцию конвертера на None.
    Ожидаемый результат: возникает arguments_exeption.
    """
    # Подготовка
    conv = basic_convertor()

    # Действие и проверки
    with pytest.raises(arguments_exeption):
        conv.convert(None)


def test_valid_result_basic_model_fields():
    """
    Проверяет обход публичных полей доменной модели.
    Ожидаемый результат: в словарь попадают простые поля (name),
    ссылочные поля (group, range) отсутствуют.
    """
    # Подготовка
    conv = basic_convertor()
    nom = nomenclature_model.create(
        full_name="Pasteurized milk 3.2%",
        name="Milk",
        group=group_model.create(name="Dairy products"),
        range=range_model.create_liter(),
        item_type="product",
    )

    # Действие
    result = conv.convert(nom)

    # Проверки
    assert result["name"] == "Milk"
    assert result["full_name"] == "Pasteurized milk 3.2%"
    assert result["item_type"] == "product"
    assert "group" not in result
    assert "range" not in result


def test_invalid_result_basic_bool_excluded():
    """
    Проверяет, что булевы значения не попадают в numeric-конвертер.
    Ожидаемый результат: поле с bool отсутствует, поле с int присутствует.
    """
    # Подготовка
    conv = basic_convertor()

    class WithFlag:
        @property
        def enabled(self):
            return True

        @property
        def count(self):
            return 5

    source = WithFlag()

    # Действие
    result = conv.convert(source)

    # Проверки
    assert "enabled" not in result
    assert result["count"] == 5


def test_valid_result_basic_broken_getter_skipped():
    """
    Проверяет устойчивость к исключениям в геттерах полей.
    Ожидаемый результат: «битое» поле пропущено, остальные поля есть.
    """
    # Подготовка
    conv = basic_convertor()

    class Broken:
        @property
        def bad(self):
            raise RuntimeError("boom")

        @property
        def good(self):
            return "ok"

    source = Broken()

    # Действие
    result = conv.convert(source)

    # Проверки
    assert "bad" not in result
    assert result["good"] == "ok"


def test_valid_result_basic_no_simple_fields():
    """
    Проверяет модель без простых полей.
    Ожидаемый результат: возвращается пустой словарь.
    """
    # Подготовка
    conv = basic_convertor()

    class OnlyRef:
        @property
        def ref(self):
            return group_model.create(name="x")

    source = OnlyRef()

    # Действие
    result = conv.convert(source)

    # Проверки
    assert result == {}


# --- datetime_convertor ---

def test_valid_result_datetime_primitive():
    """
    Проверяет конвертацию одиночного datetime.
    Ожидаемый результат: словарь {"value": "<ISO-строка>"}.
    """
    # Подготовка
    conv = datetime_convertor()
    value = datetime(2024, 5, 17, 12, 30, 0)

    # Действие
    result = conv.convert(value)

    # Проверки
    assert result == {"value": "2024-05-17T12:30:00"}


def test_valid_result_date_primitive():
    """
    Проверяет конвертацию одиночного date.
    Ожидаемый результат: словарь {"value": "<ISO-строка>"}.
    """
    # Подготовка
    conv = datetime_convertor()
    value = date(2024, 5, 17)

    # Действие
    result = conv.convert(value)

    # Проверки
    assert result == {"value": "2024-05-17"}


def test_invalid_result_datetime_none():
    """
    Проверяет реакцию конвертера дат на None.
    Ожидаемый результат: возникает arguments_exeption.
    """
    # Подготовка
    conv = datetime_convertor()

    # Действие и проверки
    with pytest.raises(arguments_exeption):
        conv.convert(None)


def test_invalid_result_time_and_timedelta_are_not_dates():
    """
    Проверяет, что time и timedelta не трактуются как даты.
    Ожидаемый результат: возвращается пустой словарь.
    """
    # Подготовка
    conv = datetime_convertor()

    class Holder:
        @property
        def t(self):
            return time(12, 0)

        @property
        def delta(self):
            return timedelta(hours=1)

    source = Holder()

    # Действие
    result = conv.convert(source)

    # Проверки
    assert result == {}


def test_valid_result_datetime_model_all_dates():
    """
    Проверяет, что в результат попадают ВСЕ даты модели, а не первая.
    Ожидаемый результат: словарь с двумя полями-датами в ISO-формате.
    """
    # Подготовка
    conv = datetime_convertor()

    class Event:
        @property
        def created_at(self):
            return datetime(2024, 1, 1, 9, 0)

        @property
        def updated_at(self):
            return date(2024, 2, 2)

        @property
        def name(self):
            return "event"

    source = Event()

    # Действие
    result = conv.convert(source)

    # Проверки
    assert result == {
        "created_at": "2024-01-01T09:00:00",
        "updated_at": "2024-02-02",
    }


def test_valid_result_datetime_model_no_dates():
    """
    Проверяет модель без полей-дат.
    Ожидаемый результат: возвращается пустой словарь.
    """
    # Подготовка
    conv = datetime_convertor()

    class NoDates:
        @property
        def name(self):
            return "x"

        @property
        def count(self):
            return 1

    source = NoDates()

    # Действие
    result = conv.convert(source)

    # Проверки
    assert result == {}


def test_valid_result_datetime_broken_getter_skipped():
    """
    Проверяет устойчивость к исключениям в геттерах.
    Ожидаемый результат: «битое» поле пропущено, дата сохранена.
    """
    # Подготовка
    conv = datetime_convertor()

    class Broken:
        @property
        def bad(self):
            raise RuntimeError("boom")

        @property
        def good(self):
            return date(2024, 3, 3)

    source = Broken()

    # Действие
    result = conv.convert(source)

    # Проверки
    assert "bad" not in result
    assert result["good"] == "2024-03-03"


# --- reference_convertor ---

def test_valid_result_reference_group_model():
    """
    Проверяет конвертацию одиночной ссылочной модели.
    Ожидаемый результат: словарь {"value": {unique_code, type, name}}.
    """
    # Подготовка
    conv = reference_convertor()
    group = group_model.create(name="Dairy products")

    # Действие
    result = conv.convert(group)

    # Проверки
    assert set(result.keys()) == {"value"}
    desc = result["value"]
    assert desc["name"] == "Dairy products"
    assert desc["unique_code"] == group.unique_code
    assert "type" in desc


def test_invalid_result_reference_none():
    """
    Проверяет реакцию конвертера ссылок на None.
    Ожидаемый результат: возникает arguments_exeption.
    """
    # Подготовка
    conv = reference_convertor()

    # Действие и проверки
    with pytest.raises(arguments_exeption):
        conv.convert(None)


def test_invalid_result_reference_plain_string():
    """
    Проверяет, что строка не считается ссылочной моделью.
    Ожидаемый результат: возвращается пустой словарь.
    """
    # Подготовка
    conv = reference_convertor()
    value = "hello"

    # Действие
    result = conv.convert(value)

    # Проверки
    assert result == {}


def test_valid_result_reference_desc_key_without_space():
    """
    Проверяет, что ключ описания — "unique_code" (без пробела).
    Ожидаемый результат: ключ "unique_code" присутствует,
    ключ "unique code" отсутствует.
    """
    # Подготовка
    conv = reference_convertor()
    group = group_model.create(name="x")

    # Действие
    result = conv.convert(group)

    # Проверки
    assert "unique_code" in result["value"]
    assert "unique code" not in result["value"]


def test_valid_result_reference_model_fields():
    """
    Проверяет обход ссылочных полей модели.
    Ожидаемый результат: в словаре только поля group и range,
    каждое — компактное описание.
    """
    # Подготовка
    conv = reference_convertor()
    group = group_model.create(name="Dairy products")
    rng = range_model.create_liter()

    class Holder:
        @property
        def group(self):
            return group

        @property
        def range(self):
            return rng

    # Действие
    result = conv.convert(Holder())

    # Проверки
    assert set(result.keys()) == {"group", "range"}
    assert result["group"]["name"] == "Dairy products"
    assert result["range"]["name"] == "Liter"


def test_valid_result_reference_nested_not_expanded():
    """
    Проверяет, что описание ссылки компактно и не раскрывает вложенные поля.
    Ожидаемый результат: описание содержит ровно {unique_code, type, name}.
    """
    # Подготовка
    conv = reference_convertor()
    nom = nomenclature_model.create(
        full_name="Milk",
        name="Milk",
        group=group_model.create(name="Dairy products"),
        range=range_model.create_liter(),
        item_type="product",
    )

    # Действие
    result = json.loads(conv.to_json(conv.convert(nom)))

    # Проверки
    assert set(result.keys()) == {"value"}
    assert set(result["value"].keys()) == {"unique_code", "type", "name"}


def test_valid_result_reference_broken_getter_skipped():
    """
    Проверяет устойчивость к исключениям в геттерах.
    Ожидаемый результат: «битое» поле пропущено, ссылка сохранена.
    """
    # Подготовка
    conv = reference_convertor()

    class Broken:
        @property
        def bad(self):
            raise RuntimeError("boom")

        @property
        def good(self):
            return group_model.create(name="ok")

    source = Broken()

    # Действие
    result = conv.convert(source)

    # Проверки
    assert "bad" not in result
    assert result["good"]["name"] == "ok"


# --- JSON-сериализация отдельных конвертеров ---

def test_valid_result_basic_to_json_roundtrip():
    """
    Проверяет сериализацию результата basic_convertor в JSON.
    Ожидаемый результат: json.loads(to_json(data)) == data.
    """
    # Подготовка
    conv = basic_convertor()
    data = conv.convert(42)

    # Действие
    text = conv.to_json(data)

    # Проверки
    assert json.loads(text) == {"value": 42}


def test_valid_result_basic_to_json_unicode_not_escaped():
    """
    Проверяет, что кириллица в JSON не экранируется в \\uXXXX.
    Ожидаемый результат: строка "Молоко" присутствует в тексте как есть.
    """
    # Подготовка
    conv = basic_convertor()

    # Действие
    text = conv.to_json({"name": "Молоко"})

    # Проверки
    assert "Молоко" in text


def test_valid_result_datetime_to_json_roundtrip():
    """
    Проверяет JSON-сериализацию результата datetime_convertor.
    Ожидаемый результат: в JSON дата представлена ISO-строкой.
    """
    # Подготовка
    conv = datetime_convertor()
    data = conv.convert(datetime(2024, 5, 17, 12, 30))

    # Действие
    text = conv.to_json(data)

    # Проверки
    assert json.loads(text) == {"value": "2024-05-17T12:30:00"}


def test_valid_result_datetime_to_json_raw_datetime():
    """
    Проверяет, что _to_json приводит «сырой» datetime к строке.
    Ожидаемый результат: json.loads возвращает ISO-строку.
    """
    # Подготовка
    conv = datetime_convertor()
    data = {"raw": datetime(2024, 1, 1)}

    # Действие
    text = conv.to_json(data)

    # Проверки
    assert json.loads(text) == {"raw": "2024-01-01T00:00:00"}


def test_valid_result_reference_to_json_roundtrip():
    """
    Проверяет JSON-сериализацию результата reference_convertor.
    Ожидаемый результат: json.dumps не падает, описание сохраняется.
    """
    # Подготовка
    conv = reference_convertor()
    group = group_model.create(name="Dairy products")
    data = conv.convert(group)

    # Действие
    text = conv.to_json(data)
    parsed = json.loads(text)

    # Проверки
    assert parsed["value"]["name"] == "Dairy products"
    assert parsed["value"]["unique_code"] == group.unique_code


def test_valid_result_reference_nomenclature_json():
    """
    Проверяет JSON-сериализацию номенклатуры как ссылочной модели.
    Ожидаемый результат: {"value": {unique_code, type, name}} в JSON.
    """
    # Подготовка
    conv = reference_convertor()
    nom = nomenclature_model.create(
        full_name="Milk",
        name="Milk",
        group=group_model.create(name="Dairy"),
        range=range_model.create_liter(),
        item_type="product",
    )

    # Действие
    parsed = json.loads(conv.to_json(conv.convert(nom)))

    # Проверки
    assert set(parsed.keys()) == {"value"}
    assert parsed["value"]["name"] == "Milk"
    assert parsed["value"]["unique_code"] == nom.unique_code
    assert parsed["value"]["type"] == "product"


# --- Совместная работа трёх конвертеров ---

def test_valid_result_composite_basic_part():
    """
    Проверяет, что basic_convertor видит только простые поля составного объекта.
    Ожидаемый результат: словарь {name, count}.
    """
    # Подготовка
    conv = basic_convertor()
    source = _make_composite()

    # Действие
    result = conv.convert(source)

    # Проверки
    assert result == {"name": "composite", "count": 7}


def test_valid_result_composite_datetime_part():
    """
    Проверяет, что datetime_convertor видит только даты составного объекта.
    Ожидаемый результат: словарь {created_at, expires_on}.
    """
    # Подготовка
    conv = datetime_convertor()
    source = _make_composite()

    # Действие
    result = conv.convert(source)

    # Проверки
    assert result == {
        "created_at": "2024-05-17T10:00:00",
        "expires_on": "2025-01-01",
    }


def test_valid_result_composite_reference_part():
    """
    Проверяет, что reference_convertor видит только ссылки составного объекта.
    Ожидаемый результат: словарь {group, range}.
    """
    # Подготовка
    conv = reference_convertor()
    source = _make_composite()

    # Действие
    result = conv.convert(source)

    # Проверки
    assert set(result.keys()) == {"group", "range"}
    assert result["group"]["name"] == "Dairy"
    assert result["range"]["name"] == "Liter"


def test_valid_result_composite_no_overlap():
    """
    Проверяет, что результаты трёх конвертеров не пересекаются по ключам.
    Ожидаемый результат: попарные пересечения множеств ключей пусты.
    """
    # Подготовка
    source = _make_composite()

    # Действие
    basic_keys = set(basic_convertor().convert(source).keys())
    dt_keys = set(datetime_convertor().convert(source).keys())
    ref_keys = set(reference_convertor().convert(source).keys())

    # Проверки
    assert basic_keys & dt_keys == set()
    assert basic_keys & ref_keys == set()
    assert dt_keys & ref_keys == set()


def test_valid_result_composite_merge_to_json():
    """
    Проверяет склейку результатов трёх конвертеров в один валидный JSON.
    Ожидаемый результат: объединённый словарь содержит все поля,
    json.loads возвращает корректные значения.
    """
    # Подготовка
    source = _make_composite()

    # Действие
    merged = {}
    merged.update(basic_convertor().convert(source))
    merged.update(datetime_convertor().convert(source))
    merged.update(reference_convertor().convert(source))
    text = basic_convertor.to_json(merged)
    parsed = json.loads(text)

    # Проверки
    assert set(merged.keys()) == {
        "name", "count", "created_at", "expires_on", "group", "range",
    }
    assert parsed["name"] == "composite"
    assert parsed["created_at"] == "2024-05-17T10:00:00"
    assert parsed["group"]["name"] == "Dairy"
    assert parsed["range"]["name"] == "Liter"


def test_valid_result_nomenclature_full_pipeline():
    """
    Проверяет полный проход по реальной доменной модели.
    Ожидаемый результат: merged содержит простые поля и ссылку
    в виде {"value": ...}; дат нет, итог сериализуется в валидный JSON.
    """
    # Подготовка
    nom = nomenclature_model.create(
        full_name="Pasteurized milk 3.2%",
        name="Milk",
        group=group_model.create(name="Dairy products"),
        range=range_model.create_liter(),
        item_type="product",
    )

    # Действие
    merged = {}
    merged.update(basic_convertor().convert(nom))
    merged.update(datetime_convertor().convert(nom))
    merged.update(reference_convertor().convert(nom))
    parsed = json.loads(basic_convertor.to_json(merged))

    # Проверки
    assert merged["name"] == "Milk"
    assert merged["full_name"] == "Pasteurized milk 3.2%"
    assert merged["item_type"] == "product"
    assert merged["value"]["name"] == "Milk"
    assert merged["value"]["type"] == "product"
    assert merged["value"]["unique_code"] == nom.unique_code

    assert "created_at" not in merged
    assert "updated_at" not in merged
    assert parsed["value"]["name"] == "Milk"
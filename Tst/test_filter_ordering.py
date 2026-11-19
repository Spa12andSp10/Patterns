import pytest

from Src.Core.filters_type import filters_type
from Src.Core.exception import arguments_exeption
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_item_dto import filter_item_dto
from Src.Logics.prototype import prototype
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


def _make_models():
    """Создаёт номенклатуру в произвольном порядке для сортировки."""
    dairy = group_model.create("Dairy products")
    meat = group_model.create("Meat products")
    unit = range_model.create("liter", 1.0, None)

    milk = nomenclature_model.create(
        "Pasteurized milk", "Milk", dairy, unit, "product",
    )
    apple = nomenclature_model.create(
        "Astrakhan apple", "Apple", dairy, unit, "product",
    )
    banana = nomenclature_model.create(
        "Banana", "Banana", dairy, unit, "product",
    )
    beef = nomenclature_model.create(
        "Beef", "Beef", meat, unit, "product",
    )
    return [milk, apple, banana, beef]


def _sort_filter(path: str, filter_type: filters_type) -> filter_dto:
    """Создаёт DTO с одним условием сортировки."""
    return filter_dto(domain="nomenclature").add_path(path, "", filter_type)


def test_alphabet_sorts_ascending():
    """ALPHABET сортирует результат по возрастанию."""
    # Подготовка
    models = _make_models()
    filters = _sort_filter("name", filters_type.ALPHABET)

    # Действие
    result = prototype(models).clone(filters)

    # Проверки
    assert [item.name for item in result.data] == [
        "Apple", "Banana", "Beef", "Milk",
    ]


def test_alphabet_desc_sorts_descending():
    """ALPHABET_DESC сортирует результат по убыванию."""
    # Подготовка
    models = _make_models()
    filters = _sort_filter("name", filters_type.ALPHABET_DESC)

    # Действие
    result = prototype(models).clone(filters)

    # Проверки
    assert [item.name for item in result.data] == [
        "Milk", "Beef", "Banana", "Apple",
    ]


def test_alphabet_does_not_drop_items():
    """Сортировка не отбрасывает записи, даже если путь пустой."""
    # Подготовка
    models = _make_models()
    filters = _sort_filter("name", filters_type.ALPHABET)

    # Действие
    result = prototype(models).clone(filters)

    # Проверки
    assert len(result.data) == len(models)


def test_sorting_by_nested_path():
    """Сортировать можно по вложенному пути, например group.name."""
    # Подготовка
    models = _make_models()
    filters = _sort_filter("group.name", filters_type.ALPHABET)

    # Действие
    result = prototype(models).clone(filters)

    # Проверки
    assert [item.group.name for item in result.data] == [
        "Dairy products", "Dairy products", "Dairy products",
        "Meat products",
    ]


def test_multiple_sort_conditions_use_first_as_primary():
    """Первое условие сортировки главное, второе уточняет порядок."""
    # Подготовка
    models = _make_models()
    filters = filter_dto(domain="nomenclature")
    filters.add_path("group.name", "", filters_type.ALPHABET)
    filters.add_path("name", "", filters_type.ALPHABET_DESC)

    # Действие
    result = prototype(models).clone(filters)

    # Проверки
    assert [(item.group.name, item.name) for item in result.data] == [
        ("Dairy products", "Milk"),
        ("Dairy products", "Banana"),
        ("Dairy products", "Apple"),
        ("Meat products", "Beef"),
    ]


def test_sorting_is_combined_with_between_filter():
    """BETWEEN отбирает записи, ALPHABET сортирует результат."""
    # Подготовка
    models = _make_models()
    filters = filter_dto(domain="nomenclature")
    filters.add(filter_item_dto.create(
        "name", "a..m", filters_type.BETWEEN,
    ))
    filters.add_path("name", "", filters_type.ALPHABET)

    # Действие
    result = prototype(models).clone(filters)

    # Проверки
    assert [item.name for item in result.data] == ["Apple", "Banana", "Beef"]


def test_invalid_between_raises_before_filtering():
    """Некорректный диапазон проверяется даже на пустых данных."""
    # Подготовка
    filters = filter_dto(domain="nomenclature")
    filters.add(filter_item_dto.create(
        "name", "not-a-range", filters_type.BETWEEN,
    ))
    empty = prototype([])

    # Действие и проверки
    with pytest.raises(arguments_exeption):
        empty.clone(filters)

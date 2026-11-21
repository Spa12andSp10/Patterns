import pytest

from Src.Core.entity_type import entity_type
from Src.Core.exception import arguments_exeption
from Src.Core.filters_type import filters_type
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_item_dto import filter_item_dto
from Src.Logics.field_path import field_path
from Src.Logics.prototype import prototype
from Src.Models.group_model import group_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.technicalmap_model import technicalmap_model


def _make_nomenclatures():
    """Собирает тестовый справочник номенклатуры."""
    dairy = group_model.create("Dairy products")
    meat = group_model.create("Meat products")
    grocery = group_model.create("Grocery")

    gram = range_model.create("gram", 1.0, None)
    kilogram = range_model.create("kilogram", 1000.0, gram)
    liter = range_model.create("liter", 1.0, None)

    milk = nomenclature_model.create(
        "Pasteurized milk", "Milk", dairy, liter, "product",
    )
    beef = nomenclature_model.create(
        "Beef top grade", "Beef", meat, kilogram, "product",
    )
    pasta = nomenclature_model.create(
        "Durum pasta", "Pasta", grocery, gram, "product",
    )
    return [milk, beef, pasta], gram, kilogram


def _make_recipe() -> technicalmap_model:
    """Собирает тестовый рецепт."""
    return technicalmap_model.create(
        ingredients=[
            ingredient_model.create_product("Milk", 300.0, 2.9, 3.2, 4.7, 1.0),
            ingredient_model.create_product("Salt", 5.0, 0.0, 0.0, 0.0, 1.0),
        ],
        preparation_method={},
        description="Milk soup",
        time="30 min",
        name="Milk soup",
    )


def _names(models) -> list:
    """Возвращает наименования моделей."""
    return [model.name for model in models]


def test_filter_by_name_like():

    # Подготовка
    models, _, _ = _make_nomenclatures()

    # Действие
    result = prototype(models).clone(filter_dto.name_filter("milk"))

    # Проверки
    assert _names(result.data) == ["Milk"]


def test_filter_by_unique_code():

    # Подготовка
    models, _, _ = _make_nomenclatures()
    milk = models[0]

    # Действие
    result = prototype(models).clone(
        filter_dto.unique_code_filter(milk.unique_code)
    )

    # Проверки
    assert result.data == [milk]


def test_filter_by_nested_group_name():

    # Подготовка
    models, _, _ = _make_nomenclatures()

    # Действие
    result = prototype(models).clone(
        filter_dto.path_filter(
            "group.name",
            "dairy",
            filters_type.LIKE,
        )
    )

    # Проверки
    assert _names(result.data) == ["Milk"]


def test_filter_by_nested_range_base_name():

    # Подготовка
    models, _, _ = _make_nomenclatures()

    # Действие
    result = prototype(models).clone(
        filter_dto.path_filter(
            "range.base.name",
            "gram",
            filters_type.EQUALS,
        )
    )

    # Проверки
    assert _names(result.data) == ["Beef"]


def test_filter_range_by_base_name():

    # Подготовка
    _, gram, kilogram = _make_nomenclatures()

    # Действие
    result = prototype([gram, kilogram]).clone(
        filter_dto.path_filter(
            "base.name",
            "gram",
            filters_type.EQUALS,
        )
    )

    # Проверки
    assert _names(result.data) == ["kilogram"]


def test_filter_recipe_by_ingredient_name():

    # Подготовка
    recipe = _make_recipe()

    # Действие
    result = prototype([recipe]).clone(
        filter_dto.path_filter(
            "ingredients[].name",
            "milk",
            filters_type.EQUALS,
        )
    )

    # Проверки
    assert result.data == [recipe]


def test_filter_by_domain_without_conditions():

    # Подготовка
    models, gram, _ = _make_nomenclatures()
    recipe = _make_recipe()

    # Действие
    result = prototype(models + [gram, recipe]).clone(
        filter_dto(domain=entity_type.RANGE)
    )

    # Проверки
    assert result.data == [gram]


def test_empty_domain_accepts_all_models():

    # Подготовка
    models, _, _ = _make_nomenclatures()
    recipe = _make_recipe()

    # Действие
    result = prototype(models + [recipe]).clone(
        filter_dto.name_filter("milk")
    )

    # Проверки
    assert sorted(_names(result.data)) == ["Milk", "Milk soup"]


def test_domain_and_conditions_are_combined():

    # Подготовка
    models, _, _ = _make_nomenclatures()
    recipe = _make_recipe()

    # Действие
    result = prototype(models + [recipe]).clone(
        filter_dto.path_filter(
            "name",
            "beef",
            filters_type.LIKE,
            domain=entity_type.NOMENCLATURE,
        )
    )

    # Проверки
    assert _names(result.data) == ["Beef"]


def test_all_conditions_are_combined_with_and():

    # Подготовка
    models, _, _ = _make_nomenclatures()

    filters = filter_dto(domain=entity_type.NOMENCLATURE)
    filters.add_path("name", "milk", filters_type.EQUALS)
    filters.add_path(
        "group.name", "Dairy products", filters_type.EQUALS
    )

    # Действие
    result = prototype(models).clone(filters)

    # Проверки
    assert _names(result.data) == ["Milk"]


def test_clone_does_not_change_source_and_keeps_previous_filter():

    # Подготовка
    models, _, _ = _make_nomenclatures()
    original = prototype(models)

    # Действие
    filtered = original.clone(
        filter_dto.name_filter("milk", filters_type.EQUALS)
    )

    # Проверки
    assert len(original.data) == 3
    assert _names(filtered.data) == ["Milk"]

    result = filtered.clone(
        filter_dto.path_filter(
            "group.name",
            "meat",
            filters_type.EQUALS,
        )
    )

    assert result.data == []
    assert _names(filtered.data) == ["Milk"]


def test_clone_without_filters_returns_independent_copy():

    # Подготовка
    models, _, _ = _make_nomenclatures()
    original = prototype(models)

    # Действие
    copy = original.clone()

    # Проверки
    assert copy is not original
    assert copy.data == original.data
    assert copy.data is not original.data


def test_field_path_resolve_nested_values():

    # Подготовка
    models, _, _ = _make_nomenclatures()
    milk, beef, _ = models

    # Действие
    recipe = _make_recipe()

    # Проверки
    assert field_path.resolve(milk, "range.base.name") == []
    assert field_path.resolve(beef, "range.base.name") == ["gram"]
    assert field_path.resolve(recipe, "ingredients[].name") == ["Milk", "Salt"]


def test_invalid_filter_name_is_rejected():
    # Подготовка
    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        filter_item_dto.create("group.owner", "value")

    with pytest.raises(arguments_exeption) as exc_info:
        filter_item_dto.create("range..name", "value")

    # Проверки
    assert exc_info.value is not None


def test_invalid_domain_is_rejected():
    # Подготовка
    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        filter_dto(domain="unknown")

    # Проверки
    assert exc_info.value is not None

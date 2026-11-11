import pytest

from Src.Models.technicalmap_model import technicalmap_model
from Src.Models.ingredient_model import ingredient_model


def _make_recipe() -> technicalmap_model:
    """Собирает тестовый рецепт напрямую, без JSON/десериализации."""
    ingredients = [
        ingredient_model("Durum wheat pasta", 400.0, 10.4, 1.1, 69.7, 1.0, "product"),
        ingredient_model("Beef",                  500.0, 18.0, 14.0, 0.0,  0.7, "product"),
        ingredient_model("Milk",                  300.0,  2.9,  3.2, 4.7,  1.0, "product"),
        ingredient_model("Apple",                 200.0,  0.4,  0.4, 9.8,  0.9, "product"),
        ingredient_model("Onion",                 100.0,  1.4,  0.0, 10.4, 0.9, "product"),
        ingredient_model("Sunflower oil",          30.0,  0.0, 99.9, 0.0,  1.0, "product"),
        ingredient_model("Salt",                    5.0,  0.0,  0.0, 0.0,  1.0, "product"),
        ingredient_model("Pepper",                  2.0,  0.0,  0.0, 0.0,  1.0, "product"),
    ]
    return technicalmap_model.create(
        ingredients=ingredients,
        preparation_method={},
        description="Тестовый рецепт",
        time="60",
        name="Pasta with beef in milk-apple sauce",
    )


def test_valid_storage_recipe_name():
    """
    Проверяет наименование рецепта.
    Ожидаемый результат: name совпадает с ожидаемым.
    """
    # Подготовка
    recipe = _make_recipe()

    # Действие и проверки
    assert recipe.name == "Pasta with beef in milk-apple sauce"


def test_valid_storage_recipe_has_ingredients():
    """
    Проверяет количество ингредиентов.
    Ожидаемый результат: 8 ингредиентов.
    """
    # Подготовка
    recipe = _make_recipe()

    # Действие и проверки
    assert len(recipe.ingredients) == 8


def test_valid_storage_recipe_has_no_pf_and_no_package():
    """
    Проверяет отсутствие полуфабрикатов и упаковки.
    Ожидаемый результат: with_pf = False, with_package = False.
    """
    # Подготовка
    recipe = _make_recipe()

    # Действие и проверки
    assert recipe.with_pf is False
    assert recipe.with_package is False


def test_valid_brutto_from_json():
    """
    Проверяет расчёт брутто.
    Ожидаемый результат: 400+500+300+200+100+30+5+2 = 1537.
    """
    # Подготовка
    recipe = _make_recipe()

    # Действие
    result = recipe.calculate_brutto()

    # Проверки
    assert result == pytest.approx(1537.0)


def test_valid_netto_from_json():
    """
    Проверяет расчёт нетто с учётом coef.
    Ожидаемый результат: сумма (brutto * coef).
    """
    # Подготовка
    recipe = _make_recipe()
    expected = (400 * 1.0 + 500 * 0.7 + 300 * 1.0 + 200 * 0.9 +
                100 * 0.9 + 30 * 1.0 + 5 * 1.0 + 2 * 1.0)

    # Действие
    result = recipe.calculate_netto()

    # Проверки
    assert result == pytest.approx(expected, abs=1e-4)


def test_valid_brutto_not_less_than_netto():
    """
    Проверяет инвариант: брутто >= нетто.
    Ожидаемый результат: условие выполнено.
    """
    # Подготовка
    recipe = _make_recipe()

    # Действие
    brutto = recipe.calculate_brutto()
    netto = recipe.calculate_netto()

    # Проверки
    assert brutto >= netto


def test_valid_add_ingredient_increases_brutto_and_netto():
    """
    Проверяет, что добавление ингредиента увеличивает брутто и нетто.
    Ожидаемый результат: брутто +50.0, нетто +50.0*0.95.
    """
    # Подготовка
    recipe = _make_recipe()
    b0, n0 = recipe.calculate_brutto(), recipe.calculate_netto()

    # Действие
    recipe.add_ingredient(
        ingredient_model("Помидор", 50.0, 1.1, 0.2, 3.8, 0.95, "product")
    )

    # Проверки
    assert recipe.calculate_brutto() == pytest.approx(b0 + 50.0)
    assert recipe.calculate_netto() == pytest.approx(n0 + 50.0 * 0.95)


def test_valid_remove_ingredient_decreases_brutto_and_netto():
    """
    Проверяет, что удаление «Salt» уменьшает брутто и нетто на 5.0.
    Ожидаемый результат: брутто -5.0, нетто -5.0.
    """
    # Подготовка
    recipe = _make_recipe()
    b0, n0 = recipe.calculate_brutto(), recipe.calculate_netto()

    # Действие
    removed = recipe.remove_ingredient("Salt")

    # Проверки
    assert removed is True
    assert recipe.calculate_brutto() == pytest.approx(b0 - 5.0)
    assert recipe.calculate_netto() == pytest.approx(n0 - 5.0)


def test_invalid_remove_missing_ingredient_returns_false():
    """
    Проверяет удаление несуществующего ингредиента.
    Ожидаемый результат: возвращается False.
    """
    # Подготовка
    recipe = _make_recipe()

    # Действие
    result = recipe.remove_ingredient("No that ingredient")

    # Проверки
    assert result is False
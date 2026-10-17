import pytest

from pathlib import Path

from Src.Models.ingredient_model import ingredient_model
from Src.Logics.storage_manager import storage_manager
from Src.Logics.settings_manager import settings_manager


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


def test_valid_storage_recipe_loaded_from_json():
    """
    Проверяет, что рецепт загружается из storage_data.json.
    Ожидаемый результат: список recipes содержит хотя бы один элемент.
    """
    # Подготовка
    sm = storage_manager()

    # Действие
    sm.load(_storage_path())

    # Проверки
    assert len(sm.recipes) >= 1


def test_valid_storage_recipe_name():
    """
    Проверяет, что наименование рецепта соответствует JSON.
    Ожидаемый результат: name совпадает с "Pasta with beef in milk-apple sauce".
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())

    # Действие
    recipe = sm.recipes[0]

    # Проверки
    assert recipe.name == "Pasta with beef in milk-apple sauce"


def test_valid_storage_recipe_has_ingredients():
    """
    Проверяет, что в рецепте присутствуют все ингредиенты из JSON.
    Ожидаемый результат: количество ингредиентов равно 8.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())

    # Действие
    recipe = sm.recipes[0]

    # Проверки
    assert len(recipe.ingredients) == 8


def test_valid_storage_recipe_has_no_pf_and_no_package():
    """
    Проверяет, что в рецепте нет полуфабрикатов и упаковки.
    Ожидаемый результат: with_pf = False и with_package = False.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())

    # Действие
    recipe = sm.recipes[0]

    # Проверки
    assert recipe.with_pf is False
    assert recipe.with_package is False
from Src.Logics.storage_manager import storage_manager
from Src.Logics.settings_manager import settings_manager

def test_valid_brutto_from_json():
    """
    Проверяет расчёт брутто по данным из JSON.
    Ожидаемый результат: 400+500+300+200+100+30+5+2 = 1537.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]

    # Действие
    result = recipe.calculate_brutto()

    # Проверки
    assert result == pytest.approx(1537.0)


def test_valid_netto_from_json():
    """
    Проверяет расчёт нетто с учётом coef каждого ингредиента.
    Ожидаемый результат: сумма (brutto * coef) равна эталонному значению.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]
    expected = (400 * 1.0 + 500 * 0.7 + 300 * 1.0 + 200 * 0.9 +
                100 * 0.9 + 30 * 1.0 + 5 * 1.0 + 2 * 1.0)

    # Действие
    result = recipe.calculate_netto()

    # Проверки
    assert result == pytest.approx(expected, abs=1e-4)


def test_valid_brutto_not_less_than_netto():
    """
    Проверяет инвариант: брутто не меньше нетто.
    Ожидаемый результат: calculate_brutto() >= calculate_netto().
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]

    # Действие
    brutto = recipe.calculate_brutto()
    netto = recipe.calculate_netto()

    # Проверки
    assert brutto >= netto


def test_valid_add_ingredient_increases_brutto_and_netto():
    """
    Проверяет, что добавление ингредиента увеличивает брутто и нетто.
    Ожидаемый результат: брутто растёт на 50.0, нетто — на 50.0 * 0.95.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]
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
    Проверяет, что удаление ингредиента уменьшает брутто и нетто.
    Ожидаемый результат: после удаления "Salt" брутто уменьшается на 5.0, нетто — на 5.0.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]
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
    Ожидаемый результат: метод возвращает False.
    """
    # Подготовка
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]

    # Действие
    result = recipe.remove_ingredient("No that ingredient")

    # Проверки
    assert result is False


def test_valid_first_start_loads_recipe():
    """
    Проверяет, что после первого старта рецепт из JSON попадает в хранилище.
    Ожидаемый результат: is_loaded = True, recipes содержит хотя бы один элемент
    с ожидаемым наименованием.
    """
    # Подготовка
    sm = storage_manager()
    smg = settings_manager()
    smg.settings.first_launch_flag = True

    # Действие
    sm.first_start(_storage_path())

    # Проверки
    assert sm.is_loaded is True
    assert len(sm.recipes) >= 1
    assert sm.recipes[0].name == "Pasta with beef in milk-apple sauce"
import pytest

from pathlib import Path

from Src.Models.ingredient_model import ingredient_model
from Src.Models.technicalmap_model import technicalmap_model
from Src.Logics.technicalmap_factory import technicalmap_factory
from Src.Logics.storage_manager import storage_manager
from Src.Logics.settings_manager import settings_manager


def _storage_path() -> str:
    """Путь к storage_data.json (эталонные данные)."""
    return str(Path(__file__).resolve().parent / "storage_data.json")


@pytest.fixture(autouse=True)
def reset_storage():
    """Сбрасывает состояние singleton-хранилища перед каждым тестом.

    Очищает все списки справочников и сбрасывает флаг загрузки,
    чтобы тесты не влияли друг на друга.
    """
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

    Ожидаемый результат:
    список recipes содержит хотя бы один элемент.
    """
    sm = storage_manager()
    sm.load(_storage_path())
    assert len(sm.recipes) >= 1


def test_valid_storage_recipe_name():
    """
    Проверяет, что наименование рецепта соответствует JSON.

    Ожидаемый результат:
    name совпадает с "Pasta with beef in milk-apple sauce".
    """
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]
    assert recipe.name == "Pasta with beef in milk-apple sauce"


def test_valid_storage_recipe_has_ingredients():
    """
    Проверяет, что в рецепте присутствуют все ингредиенты из JSON.

    Ожидаемый результат:
    количество ингредиентов равно 8.
    """
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]
    assert len(recipe.ingredients) == 8


def test_valid_storage_recipe_has_no_pf_and_no_package():
    """
    Проверяет, что в рецепте нет полуфабрикатов и упаковки.

    Ожидаемый результат:
    with_pf = False и with_package = False.
    """
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]
    assert recipe.with_pf is False
    assert recipe.with_package is False


def test_valid_brutto_from_json():
    """
    Проверяет расчёт брутто по данным из JSON.

    Ожидаемый результат:
    400+500+300+200+100+30+5+2 = 1537.
    """
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]
    assert recipe.calculate_brutto() == pytest.approx(1537.0)


def test_valid_netto_from_json():
    """
    Проверяет расчёт нетто с учётом coef каждого ингредиента.

    Ожидаемый результат:
    сумма (brutto * coef) равна эталонному значению.
    """
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]
    expected = (400 * 1.0 + 500 * 0.7 + 300 * 1.0 + 200 * 0.9 +
                100 * 0.9 + 30 * 1.0 + 5 * 1.0 + 2 * 1.0)
    assert recipe.calculate_netto() == pytest.approx(expected, abs=1e-4)


def test_valid_brutto_not_less_than_netto():
    """
    Проверяет инвариант: брутто не меньше нетто.

    Ожидаемый результат:
    calculate_brutto() >= calculate_netto().
    """
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]
    assert recipe.calculate_brutto() >= recipe.calculate_netto()


def test_valid_add_ingredient_increases_brutto_and_netto():
    """
    Проверяет, что добавление ингредиента увеличивает брутто и нетто.

    Ожидаемый результат:
    брутто растёт на 50.0, нетто — на 50.0 * 0.95.
    """
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]
    b0, n0 = recipe.calculate_brutto(), recipe.calculate_netto()

    recipe.add_ingredient(
        ingredient_model("Помидор", 50.0, 1.1, 0.2, 3.8, 0.95, "product")
    )

    assert recipe.calculate_brutto() == pytest.approx(b0 + 50.0)
    assert recipe.calculate_netto() == pytest.approx(n0 + 50.0 * 0.95)


def test_valid_remove_ingredient_decreases_brutto_and_netto():
    """
    Проверяет, что удаление ингредиента уменьшает брутто и нетто.

    Ожидаемый результат:
    после удаления "Salt" брутто уменьшается на 5.0, нетто — на 5.0.
    """
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]
    b0, n0 = recipe.calculate_brutto(), recipe.calculate_netto()

    assert recipe.remove_ingredient("Salt") is True
    assert recipe.calculate_brutto() == pytest.approx(b0 - 5.0)
    assert recipe.calculate_netto() == pytest.approx(n0 - 5.0)


def test_invalid_remove_missing_ingredient_returns_false():
    """
    Проверяет удаление несуществующего ингредиента.

    Ожидаемый результат:
    метод возвращает False.
    """
    sm = storage_manager()
    sm.load(_storage_path())
    recipe = sm.recipes[0]
    assert recipe.remove_ingredient("No that ingredient") is False


def test_valid_add_packaging_updates_flag():
    """
    Проверяет обновление флага with_package при добавлении упаковки.

    Ожидаемый результат:
    до добавления with_package = False, после — True.
    """
    r = technicalmap_model(
        ingredients=[ingredient_model("Flour", 100.0, 10.3, 1.1, 70.6, 1.0, "product")],
        preparation_method={},
        description="Test",
        time="1 min",
        name="Test dish",
    )
    assert r.with_package is False
    r.add_ingredient(
        ingredient_model("Packet", 3.0, 0.0, 0.0, 0.0, 1.0, "packaging")
    )
    assert r.with_package is True


def test_valid_add_semi_finished_updates_flag():
    """
    Проверяет обновление флага with_pf при добавлении полуфабриката.

    Ожидаемый результат:
    до добавления with_pf = False, после — True.
    """
    r = technicalmap_model(
        ingredients=[ingredient_model("Flour", 100.0, 10.3, 1.1, 70.6, 1.0, "product")],
        preparation_method={},
        description="Test",
        time="1 min",
        name="Test dish",
    )
    assert r.with_pf is False
    r.add_ingredient(
        ingredient_model("Bouillon", 200.0, 1.0, 0.5, 2.0, 1.0, "semi_finished")
    )
    assert r.with_pf is True


def test_valid_factory_creates_recipe():
    """
    Проверяет, что technicalmap_factory.create создаёт рецепт.

    Ожидаемый результат:
    рецепт содержит заданные поля, брутто и нетто равны 100.0.
    """
    ing = ingredient_model("test", 100.0, 1.0, 1.0, 1.0, 1.0, "product")
    r = technicalmap_factory.create(
        ingredients=[ing],
        preparation_method={"test": "boil"},
        description="description",
        time="10 min",
        name="Factory recipe",
    )
    assert r.name == "Factory recipe"
    assert len(r.ingredients) == 1
    assert r.calculate_brutto() == pytest.approx(100.0)
    assert r.calculate_netto() == pytest.approx(100.0)


def test_valid_first_start_loads_recipe():
    """
    Проверяет, что после первого старта рецепт из JSON
    попадает в хранилище.

    Ожидаемый результат:
    is_loaded = True, recipes содержит хотя бы один элемент
    с ожидаемым наименованием.
    """
    sm = storage_manager()
    smg = settings_manager()
    smg.settings.first_launch_flag = True
    sm.first_start(_storage_path())

    assert sm.is_loaded is True
    assert len(sm.recipes) >= 1
    assert sm.recipes[0].name == "Pasta with beef in milk-apple sauce"
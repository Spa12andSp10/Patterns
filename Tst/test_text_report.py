import pytest
from Src.Logics.text_report import text_report
from Src.Logics.report_factory import report_factory
from Src.Dtos.report_type_enum import report_type_enum
from Src.Models.technicalmap_model import technicalmap_model
from Src.Models.ingredient_model import ingredient_model


def _make_recipe() -> technicalmap_model:
    """Собирает тестовый рецепт напрямую, без JSON/десериализации."""
    return technicalmap_model.create(
        ingredients=[
            ingredient_model("Durum wheat pasta", 400.0, 10.4, 1.1, 69.7, 1.0, "product"),
            ingredient_model("Beef",              500.0, 18.0, 14.0, 0.0, 0.7, "product"),
        ],
        preparation_method={},
        description="Тестовый рецепт",
        time="60",
        name="Test recipe",
    )


def test_valid_result_name():
    """
    Проверяет, что text_report формирует непустой текст по рецепту.
    Ожидаемый результат: result.text != "".
    """
    # Подготовка
    tr = text_report()
    recipe = _make_recipe()

    # Действие
    result = tr.build(recipe)

    # Проверки
    assert result.text != ""


def test_valid_result_name2():
    """
    Проверяет, что фабрика создаёт text_report для TXT.
    Ожидаемый результат: isinstance(result, text_report).
    """
    # Подготовка
    rf = report_factory()

    # Действие
    result = rf.create(report_type_enum.TXT)

    # Проверки
    assert isinstance(result, text_report)


@pytest.mark.xfail(reason="CSV ещё не поддержан")
def test_invalid_result_name3():
    """
    Проверяет, что создание CSV-отчёта пока не поддержано.
    Ожидаемый результат: тест помечен как xfail.
    """
    # Подготовка
    rf = report_factory()

    # Действие
    rf.create(report_type_enum.CSV)


def test_valud_result_name4():
    """
    Проверяет, что фабрика возвращает непустой отчёт для TXT.
    Ожидаемый результат: result не пустой.
    """
    # Подготовка
    rf = report_factory()

    # Действие
    result = rf.create(report_type_enum.TXT)

    # Проверки
    assert result
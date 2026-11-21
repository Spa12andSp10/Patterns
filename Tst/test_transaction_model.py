from datetime import date, datetime

import pytest

from Src.Core.exception import arguments_exeption
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.transaction_model import transaction_model
from Src.Models.warehouse_model import warehouse_model


def _references():
    """Создаёт справочники, необходимые для транзакции."""
    group = group_model.create("Dairy products")
    unit = range_model.create("liter", 1.0, None)
    nomenclature = nomenclature_model.create(
        "Pasteurized milk 3.2%", "Milk", group, unit, "product",
    )
    warehouse = warehouse_model.create("Main warehouse", "29 Lermontova St.")
    return nomenclature, warehouse, unit


def test_create_accepts_int_and_converts_to_float():
    """Целое количество сохраняется как float."""

    # Подготовка
    nomenclature, warehouse, unit = _references()

    # Действие
    transaction = transaction_model.create(
        nomenclature, warehouse, unit, 10, datetime(2026, 1, 15),
    )

    # Проверки
    assert transaction.value == 10.0
    assert isinstance(transaction.value, float)


def test_create_accepts_negative_value():
    """Отрицательное значение означает расход и сохраняется как есть."""

    # Подготовка
    nomenclature, warehouse, unit = _references()

    # Действие
    transaction = transaction_model.create(
        nomenclature, warehouse, unit, -2.5, datetime(2026, 1, 15),
    )

    # Проверки
    assert transaction.value == -2.5


def test_period_accepts_datetime():
    """Период сохраняется как datetime."""

    # Подготовка
    nomenclature, warehouse, unit = _references()
    period = datetime(2026, 1, 15, 12, 30)

    # Действие
    transaction = transaction_model.create(
        nomenclature, warehouse, unit, 1, period,
    )

    # Проверки
    assert transaction.period == period


def test_period_accepts_date():
    """date приводится к datetime на начало дня."""

    # Подготовка
    nomenclature, warehouse, unit = _references()

    # Действие
    transaction = transaction_model.create(
        nomenclature, warehouse, unit, 1, date(2026, 1, 15),
    )

    # Проверки
    assert transaction.period == datetime(2026, 1, 15, 0, 0)


def test_period_accepts_iso_string():
    """ISO-строка приводится к datetime."""

    # Подготовка
    nomenclature, warehouse, unit = _references()

    # Действие
    transaction = transaction_model.create(
        nomenclature, warehouse, unit, 1, "2026-01-15T10:20:30",
    )

    # Проверки
    assert transaction.period == datetime(2026, 1, 15, 10, 20, 30)


def test_period_accepts_iso_date_string():
    """ISO-строка без времени приводится к datetime на начало дня."""

    # Подготовка
    nomenclature, warehouse, unit = _references()

    # Действие
    transaction = transaction_model.create(
        nomenclature, warehouse, unit, 1, "2026-01-15",
    )

    # Проверки
    assert transaction.period == datetime(2026, 1, 15, 0, 0)


@pytest.mark.parametrize("value", ["10", None, object()])
def test_value_rejects_non_numbers(value):
    """Нечисловое количество отклоняется."""
    # Подготовка
    nomenclature, warehouse, unit = _references()

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        transaction_model.create(
            nomenclature, warehouse, unit, value, datetime(2026, 1, 15),
        )

    # Проверки
    assert exc_info.value is not None


def test_value_rejects_bool():
    """bool не считается количеством"""
    # Подготовка
    nomenclature, warehouse, unit = _references()

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        transaction_model.create(
            nomenclature, warehouse, unit, True, datetime(2026, 1, 15),
        )

    # Проверки
    assert exc_info.value is not None


@pytest.mark.parametrize("period", ["not-a-date", "", None, 123])
def test_period_rejects_invalid_values(period):
    """Некорректный период отклоняется."""
    # Подготовка
    nomenclature, warehouse, unit = _references()

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        transaction_model.create(
            nomenclature, warehouse, unit, 1, period,
        )

    # Проверки
    assert exc_info.value is not None


def test_setters_reject_wrong_reference_types():
    """Ссылки на справочники проверяются по типу."""
    # Подготовка
    nomenclature, warehouse, unit = _references()
    transaction = transaction_model.create(
        nomenclature, warehouse, unit, 1, datetime(2026, 1, 15),
    )

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        transaction.nomenclatures = warehouse
    with pytest.raises(arguments_exeption) as exc_info:
        transaction.warehouses = unit
    with pytest.raises(arguments_exeption) as exc_info:
        transaction.ranges = nomenclature

    # Проверки
    assert exc_info.value is not None


def test_create_returns_transaction_model():
    """create возвращает экземпляр transaction_model."""

    # Подготовка
    nomenclature, warehouse, unit = _references()

    # Действие
    transaction = transaction_model.create(
        nomenclature, warehouse, unit, 1, datetime(2026, 1, 15),
    )

    # Проверки
    assert isinstance(transaction, transaction_model)
    assert transaction.nomenclatures is nomenclature
    assert transaction.warehouses is warehouse
    assert transaction.ranges is unit

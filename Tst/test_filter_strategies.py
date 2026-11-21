import pytest

from Src.Core.exception import arguments_exeption
from Src.Core.filters_type import filters_type
from Src.Logics.filter_strategies import (
    alphabet_filter_strategy,
    between_filter_strategy,
)


@pytest.fixture()
def between():
    """Стратегия BETWEEN."""
    return between_filter_strategy()


@pytest.mark.parametrize(
    "source, bounds",
    [
        ("5", "1..10"),
        ("1", "1..10"),
        ("10", "1..10"),
        ("2.5", "1.5..3.5"),
        ("-5", "-10..0"),
        ("5", "10..1"),
    ],
)


def test_between_includes_numeric_bounds(between, source, bounds):
    """BETWEEN включает границы и не зависит от их порядка."""
    # Подготовка
    strategy = between

    # Действие
    result = strategy.match(source, bounds)

    # Проверки
    assert result is True


@pytest.mark.parametrize(
    "source, bounds",
    [
        ("0", "1..10"),
        ("11", "1..10"),
        ("-11", "-10..0"),
    ],
)


def test_between_rejects_numbers_outside_range(between, source, bounds):
    """Числа вне диапазона не подходят."""
    # Подготовка
    strategy = between

    # Действие
    result = strategy.match(source, bounds)

    # Проверки
    assert result is False


@pytest.mark.parametrize(
    "source, bounds",
    [
        ("Apple", "apple..milk"),
        ("Milk", "apple..milk"),
        ("Banana", "APPLE..MILK"),
        ("banana", "milk..apple"),
    ],
)


def test_between_compares_strings_case_insensitive(between, source, bounds):
    """Строковые границы сравниваются без учёта регистра."""
    # Подготовка
    strategy = between

    # Действие
    result = strategy.match(source, bounds)

    # Проверки
    assert result is True


def test_between_rejects_string_outside_range(between):
    """Строка вне диапазона не подходит."""
    # Подготовка
    strategy = between

    # Действие
    result = strategy.match("Orange", "apple..milk")

    # Проверки
    assert result is False


def test_between_supports_comma_separator(between):
    """Запятая работает как запасной разделитель границ."""
    # Подготовка
    strategy = between

    # Действие
    direct = strategy.match("5", "1,10")
    reversed_bounds = strategy.match("5", "10,1")

    # Проверки
    assert direct is True
    assert reversed_bounds is True


def test_between_supports_decimal_comma(between):
    """Дробные числа можно задавать с запятой внутри границ."""
    # Подготовка
    strategy = between

    # Действие
    result = strategy.match("2.5", "1,5..3,5")

    # Проверки
    assert result is True


@pytest.mark.parametrize(
    "bounds",
    ["", "1", "1..", "..2", "a", None, 123],
)


def test_between_rejects_invalid_bounds(between, bounds):
    """Некорректный диапазон отклоняется."""
    # Подготовка
    strategy = between

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        strategy.validate(bounds)

    # Проверки
    assert exc_info.value is not None


def test_alphabet_is_ordering_strategy():
    """ALPHABET не фильтрует, а задаёт сортировку по возрастанию."""
    # Подготовка
    strategy = alphabet_filter_strategy()

    # Действие
    result = strategy.match("anything", "")

    # Проверки
    assert strategy.is_ordering is True
    assert strategy.reverse is False
    assert result is True


def test_reverse_alphabet_is_ordering_strategy():
    """Обратный ALPHABET сортирует по убыванию."""
    # Подготовка
    strategy = alphabet_filter_strategy(reverse=True)

    # Действие
    result = strategy.match("anything", "")

    # Проверки
    assert strategy.is_ordering is True
    assert strategy.reverse is True
    assert result is True


def test_filters_type_contains_reverse_alphabet():
    """В перечислении есть отдельный тип обратной сортировки."""
    # Подготовка
    enum_member = filters_type.ALPHABET_DESC

    # Действие
    value = enum_member.value

    # Проверки
    assert value == "alphabet_desc"

import pytest

from Src.Core.exception import (
    arguments_exeption,
    max_length_exeption,
    length_exeption,
    validation_exeption,
)
from Src.Core.validator import validator


def test_valid_result_checking_validate():
    """
    Проверяет успешное прохождение валидации при корректных
    входных данных.

    Ожидаемый результат:
    валидатор не бросает исключений, метод завершается
    без ошибок.
    """
    validator.validate("for_test", str, "test", 8, 10)


def test_invalid_result_value_is_none():
    """
    Проверяет реакцию валидатора на пустое значение None.

    Ожидаемый результат:
    при передаче None возникает arguments_exeption.
    """
    with pytest.raises(arguments_exeption):
        validator.validate(None, str, "test", 8)


def test_invalid_result_value_is_empty():
    """
    Проверяет реакцию валидатора на пустую строку.

    Ожидаемый результат:
    при передаче пустой строки возникает arguments_exeption.
    """
    with pytest.raises(arguments_exeption):
        validator.validate("", str, "test", 8)


def test_invalid_result_incorrect_type():
    """
    Проверяет реакцию валидатора на несоответствие типа
    переданного значения ожидаемому.

    Ожидаемый результат:
    при передаче значения другого типа возникает
    arguments_exeption.
    """
    with pytest.raises(arguments_exeption):
        validator.validate("for_test", int, "test", 8)


def test_invalid_result_incorrect_length():
    """
    Проверяет реакцию валидатора на несоответствие длины
    значения ожидаемой.

    Ожидаемый результат:
    при передаче строки неправильной длины возникает
    length_exeption.
    """
    with pytest.raises(length_exeption):
        validator.validate("for_test", str, "test", 4)


def test_invalid_result_incorrect_max_length():
    """
    Проверяет реакцию валидатора на превышение максимально
    допустимой длины значения.

    Ожидаемый результат:
    при передаче строки длиннее max_len возникает
    max_length_exeption.
    """
    with pytest.raises(max_length_exeption):
        validator.validate("for_test1234", str, "test", 12, 10)


def test_valid_result_value_is_digit():
    """
    Проверяет успешную валидацию строки, состоящей только
    из цифр.

    Ожидаемый результат:
    валидатор не бросает исключений, метод завершается
    без ошибок.
    """
    validator.digit_validate("12345")


def test_invalid_result_value_is_not_digit():
    """
    Проверяет реакцию валидатора на строку, содержащую
    не только цифры.

    Ожидаемый результат:
    при передаче строки с буквами возникает
    validation_exeption.
    """
    with pytest.raises(validation_exeption):
        validator.digit_validate("12345test")


def test_valid_result_correct_inn():
    """
    Проверяет успешную валидацию ИНН с корректной
    контрольной суммой.

    Ожидаемый результат:
    валидатор не бросает исключений, метод завершается
    без ошибок.
    """
    validator.check_inn("7707083893")


def test_invalid_result_incorrect_inn():
    """
    Проверяет реакцию валидатора на ИНН с некорректной
    контрольной суммой.

    Ожидаемый результат:
    при передаче ИНН с неверной последней цифрой возникает
    validation_exeption.
    """
    with pytest.raises(validation_exeption):
        validator.check_inn("7707083894")


def test_valid_result_correct_account():
    """
    Проверяет успешную валидацию расчётного счёта
    с корректной контрольной суммой.

    Ожидаемый результат:
    валидатор не бросает исключений, метод завершается
    без ошибок.
    """
    validator.check_account("40702810900000000000", "044525225")


def test_invalid_result_incorrect_account():
    """
    Проверяет реакцию валидатора на расчётный счёт
    с некорректной контрольной суммой.

    Ожидаемый результат:
    при передаче счёта с неверной контрольной суммой
    возникает validation_exeption.
    """
    with pytest.raises(validation_exeption):
        validator.check_account("40702810600000000000", "044525225")


def test_valid_result_value_greater_or_equal_than_zero():
    """
    Проверяет успешную валидацию положительного значения.

    Ожидаемый результат:
    валидатор не бросает исключений, метод завершается
    без ошибок.
    """
    validator.no_lower_that_zero_validate(1)


def test_invalid_result_value_lower_than_zero():
    """
    Проверяет реакцию валидатора на отрицательное значение.

    Ожидаемый результат:
    при передаче значения, меньшего либо равного нулю,
    возникает arguments_exeption.
    """
    with pytest.raises(arguments_exeption):
        validator.no_lower_that_zero_validate(-1)
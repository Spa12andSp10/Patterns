import pytest

from Src.Core.abstract_model import abstact_model
from Src.Core.entity_model import entity_model
from Src.Core.exception import arguments_exeption


class DummyEntity(abstact_model):
    """Заглушка для проверки поведения базового класса без доменной логики."""
    pass


class DummyEntityModel(entity_model):
    """Заглушка для проверки поведения entity_model без доменной логики."""
    pass


def test_valid_result_abstract_model_unique_code_not_empty():
    """
    Ожидаемый результат:
    unique_code автоматически генерируется и не является пустой строкой.
    """
    entity = DummyEntity()

    assert entity.unique_code != ""


def test_valid_result_abstract_model_unique_code_is_unique():
    """
    Ожидаемый результат:
    два разных объекта получают разные значения unique_code.
    """
    en1 = DummyEntity()
    en2 = DummyEntity()

    assert en1 != en2


def test_valid_result_abstract_model_equality_by_unique_code():
    """
    Ожидаемый результат:
    объекты равны, если их unique_code совпадает.
    """
    entity1 = DummyEntity()
    entity2 = DummyEntity()

    entity1.unique_code = "fff"
    entity2.unique_code = "fff"

    assert entity1 == entity2


def test_invalid_result_entity_model_name_empty():
    """
    Ожидаемый результат:
    при передаче пустой строки в name возникает arguments_exeption.
    """
    entity = DummyEntityModel()

    with pytest.raises(arguments_exeption):
        entity.name = ""


def test_invalid_result_entity_model_name_whitespace():
    """
    Ожидаемый результат:
    при передаче строки только из пробелов возникает arguments_exeption.
    """
    entity = DummyEntityModel()

    with pytest.raises(arguments_exeption):
        entity.name = "   "


@pytest.mark.parametrize("value", [None, 123, [], {}, True])
def test_invalid_result_entity_model_name_type(value):
    """
    Ожидаемый результат:
    при передаче значения, не являющегося непустой строкой,
    возникает arguments_exeption.
    """
    entity = DummyEntityModel()

    with pytest.raises(arguments_exeption):
        entity.name = value
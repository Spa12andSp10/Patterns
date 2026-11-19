from abc import ABC

import pytest

from Src.Core.exception import arguments_exeption
from Src.Core.field_kind import field_kind
from Src.Core.field_spec import field_spec


def test_valid_result_field_spec_defaults():
    """
    Проверяет значения по умолчанию у описания поля.
    Ожидаемый результат: kind=primitive, поле обязательное, остальное пусто.
    """
    # Подготовка
    name = "name"

    # Действие
    spec = field_spec(name)

    # Проверки
    assert spec.name == "name"
    assert spec.kind is field_kind.PRIMITIVE
    assert spec.model_cls is None
    assert spec.cast is None
    assert spec.aliases == ()
    assert spec.required is True
    assert spec.default is None


def test_valid_result_field_spec_positional_constructor():
    """
    Проверяет совместимость с кортежами из _fields моделей.
    Ожидаемый результат: поля заполняются в прежнем порядке.
    """
    # Подготовка
    raw = ("coef", "primitive", None, float, (), False, 1.0)

    # Действие
    spec = field_spec(*raw)

    # Проверки
    assert spec.name == "coef"
    assert spec.kind is field_kind.PRIMITIVE
    assert spec.model_cls is None
    assert spec.cast is float
    assert spec.aliases == ()
    assert spec.required is False
    assert spec.default == 1.0


def test_valid_result_field_spec_is_abc():
    """
    Проверяет, что field_spec наследуется от ABC.
    Ожидаемый результат: экземпляр является объектом ABC.
    """
    # Подготовка
    name = "name"

    # Действие
    spec = field_spec(name)

    # Проверки
    assert isinstance(spec, ABC)


def test_valid_result_field_spec_setters():
    """
    Проверяет работу сеттеров описания поля.
    Ожидаемый результат: все значения обновляются.
    """
    # Подготовка
    spec = field_spec("name")

    # Действие
    spec.name = " full_name "
    spec.kind = "model"
    spec.model_cls = dict
    spec.cast = str
    spec.aliases = ("title",)
    spec.required = False
    spec.default = "unknown"

    # Проверки
    assert spec.name == "full_name"
    assert spec.kind is field_kind.MODEL
    assert spec.model_cls is dict
    assert spec.cast is str
    assert spec.aliases == ("title",)
    assert spec.required is False
    assert spec.default == "unknown"


@pytest.mark.parametrize("value", [None, "", "   ", 1])
def test_invalid_result_field_spec_bad_name(value):
    """
    Проверяет валидацию имени поля.
    Ожидаемый результат: пустое или нестроковое имя вызывает arguments_exeption.
    """
    # Подготовка
    name = value

    # Действие и проверки
    with pytest.raises(arguments_exeption):
        field_spec(name)


def test_invalid_result_field_spec_unknown_kind():
    """
    Проверяет валидацию kind.
    Ожидаемый результат: неизвестный kind вызывает arguments_exeption.
    """
    # Подготовка
    name = "name"
    kind = "unknown"

    # Действие и проверки
    with pytest.raises(arguments_exeption):
        field_spec(name, kind)


@pytest.mark.parametrize("value", [object(), 1, "group_model"])
def test_invalid_result_field_spec_bad_model_cls(value):
    """
    Проверяет валидацию model_cls.
    Ожидаемый результат: не-класс вызывает arguments_exeption.
    """
    # Подготовка
    name = "name"
    model_cls = value

    # Действие и проверки
    with pytest.raises(arguments_exeption):
        field_spec(name, model_cls=model_cls)


@pytest.mark.parametrize("value", [1, "str", object()])
def test_invalid_result_field_spec_bad_cast(value):
    """
    Проверяет валидацию cast.
    Ожидаемый результат: не-callable вызывает arguments_exeption.
    """
    # Подготовка
    name = "name"
    cast = value

    # Действие и проверки
    with pytest.raises(arguments_exeption):
        field_spec(name, cast=cast)


@pytest.mark.parametrize("value", [(), [], "alias", None])
def test_invalid_result_field_spec_aliases_must_be_tuple(value):
    """
    Проверяет валидацию aliases.
    Ожидаемый результат: не-кортеж вызывает arguments_exeption.
    """
    # Подготовка
    name = "name"
    aliases = value

    # Действие
    if isinstance(aliases, tuple):
        spec = field_spec(name, aliases=aliases)

        # Проверки
        assert spec.aliases == aliases
        return

    # Действие и проверки
    with pytest.raises(arguments_exeption):
        field_spec(name, aliases=aliases)


@pytest.mark.parametrize("value", [1, 0, "true", None])
def test_invalid_result_field_spec_required_must_be_bool(value):
    """
    Проверяет валидацию required.
    Ожидаемый результат: не-bool вызывает arguments_exeption.
    """
    # Подготовка
    name = "name"
    required = value

    # Действие и проверки
    with pytest.raises(arguments_exeption):
        field_spec(name, required=required)
import pytest

from Src.Core.field_kind import field_kind
from Src.Models.group_model import group_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model
from Src.Models.settings_model import settings_model
from Src.Models.technicalmap_model import technicalmap_model
from Src.Models.warehouse_model import warehouse_model


DOMAIN_MODELS = (
    group_model,
    range_model,
    warehouse_model,
    organization_model,
    nomenclature_model,
    ingredient_model,
    technicalmap_model,
)

EXPECTED_REQUIRED = (
    (group_model, {"name"}),
    (range_model, {"name", "conversion_factor"}),
    (warehouse_model, {"name", "address"}),
    (organization_model, {"name", "inn", "bic", "account", "owner"}),
    (nomenclature_model, {"full_name", "name"}),
    (
        ingredient_model,
        {"full_name", "brutto", "proteins", "fats", "carbohydrates"},
    ),
    (technicalmap_model, {"name", "description", "time", "ingredients"}),
)


@pytest.mark.parametrize("model_cls, expected", EXPECTED_REQUIRED)
def test_valid_result_required_keys_are_stable(model_cls, expected):
    """
    Проверяет, что рефлексия сохранила прежние обязательные поля.
    Ожидаемый результат: required_keys совпадает с эталонным набором.
    """
    # Подготовка
    expected_keys = frozenset(expected)

    # Действие
    result = model_cls.required_keys()

    # Проверки
    assert result == expected_keys


@pytest.mark.parametrize("model_cls", DOMAIN_MODELS)
def test_valid_result_domain_models_do_not_declare_fields(model_cls):
    """
    Проверяет, что доменные модели не дублируют описание полей.
    Ожидаемый результат: собственного _fields у модели нет.
    """
    # Подготовка
    cls_dict = model_cls.__dict__

    # Действие
    has_fields = "_fields" in cls_dict

    # Проверки
    assert has_fields is False


def test_valid_result_technicalmap_name_is_declared_once():
    """
    Проверяет отказ от ручного дублирования name в техкарте.
    Ожидаемый результат: name встречается ровно один раз.
    """
    # Подготовка
    specs = technicalmap_model._specs()

    # Действие
    names = [spec.name for spec in specs]

    # Проверки
    assert names.count("name") == 1
    assert set(names) == {
        "ingredients",
        "preparation_method",
        "description",
        "time",
        "name",
    }


def test_valid_result_ingredient_excludes_inherited_fields():
    """
    Проверяет, что в ингредиент не попадают поля номенклатуры.
    Ожидаемый результат: нет отдельных name, group и range.
    """
    # Подготовка
    specs = ingredient_model._specs()

    # Действие
    names = [spec.name for spec in specs]

    # Проверки
    assert names == [
        "full_name",
        "brutto",
        "proteins",
        "fats",
        "carbohydrates",
        "coef",
        "item_type",
    ]


def test_valid_result_ingredient_aliases():
    """
    Проверяет альтернативные имена полей ингредиента.
    Ожидаемый результат: full_name читается из name, item_type — из type.
    """
    # Подготовка
    specs = {spec.name: spec for spec in ingredient_model._specs()}

    # Действие
    full_name_aliases = specs["full_name"].aliases
    item_type_aliases = specs["item_type"].aliases

    # Проверки
    assert full_name_aliases == ("name",)
    assert item_type_aliases == ("type",)


def test_valid_result_nomenclature_reference_fields():
    """
    Проверяет распознавание ссылочных полей номенклатуры.
    Ожидаемый результат: group и range имеют kind=model и свой model_cls.
    """
    # Подготовка
    specs = {spec.name: spec for spec in nomenclature_model._specs()}

    # Действие
    group_spec = specs["group"]
    range_spec = specs["range"]
    item_type_spec = specs["item_type"]

    # Проверки
    assert group_spec.kind is field_kind.MODEL
    assert group_spec.model_cls is group_model
    assert range_spec.kind is field_kind.MODEL
    assert range_spec.model_cls is range_model
    assert item_type_spec.aliases == ("type",)


def test_valid_result_range_base_forward_reference():
    """
    Проверяет разрешение forward-ref в range_model.base.
    Ожидаемый результат: kind=model, model_cls=range_model.
    """
    # Подготовка
    specs = {spec.name: spec for spec in range_model._specs()}

    # Действие
    base_spec = specs["base"]

    # Проверки
    assert base_spec.kind is field_kind.MODEL
    assert base_spec.model_cls is range_model
    assert base_spec.required is False


def test_valid_result_technicalmap_kinds_and_defaults():
    """
    Проверяет kind и необязательные поля техкарты.
    Ожидаемый результат: preparation_method=dict, ingredients=list.
    """
    # Подготовка
    specs = {spec.name: spec for spec in technicalmap_model._specs()}

    # Действие
    prep_spec = specs["preparation_method"]
    ing_spec = specs["ingredients"]
    name_spec = specs["name"]

    # Проверки
    assert prep_spec.kind is field_kind.DICT
    assert prep_spec.required is False
    assert prep_spec.default == {}
    assert ing_spec.kind is field_kind.LIST
    assert name_spec.required is True


def test_valid_result_ingredient_coef_default():
    """
    Проверяет бизнес-исключение для коэффициента ингредиента.
    Ожидаемый результат: coef необязателен и по умолчанию равен 1.0.
    """
    # Подготовка
    specs = {spec.name: spec for spec in ingredient_model._specs()}

    # Действие
    coef_spec = specs["coef"]

    # Проверки
    assert coef_spec.required is False
    assert coef_spec.default == 1.0


def test_valid_result_settings_model_has_no_reflected_fields():
    """
    Проверяет модель без create.
    Ожидаемый результат: описание полей пустое.
    """
    # Подготовка
    model_cls = settings_model

    # Действие
    result = model_cls._specs()

    # Проверки
    assert result == ()


def test_valid_result_specs_are_cached():
    """
    Проверяет кэширование рефлексии.
    Ожидаемый результат: повторный вызов возвращает тот же кортеж.
    """
    # Подготовка
    model_cls = group_model

    # Действие
    first = model_cls._specs()
    second = model_cls._specs()

    # Проверки
    assert first is second
import pytest

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exeption
from Src.Core.field_spec import field_spec


class stub_chain:
    """Минимальная цепочка десериализации: возвращает source без изменений."""

    def deserialize(self, source, resolver, visited=None):
        return source


class stub_resolver:
    """Минимальный резолвер: умеет искать модель по имени."""

    def __init__(self, by_name=None):
        self.by_name = by_name or {}

    def get_by_name(self, model_cls, name):
        return self.by_name.get((model_cls, name))


class child_model(abstract_model):
    """Заглушка вложенной модели."""

    @classmethod
    def create(cls):
        return cls()


class dummy_model(abstract_model):
    """Модель со всеми поддерживаемыми kind для проверки диспетчеризации."""

    _fields = (
        ("name", "primitive", None, str),
        ("child", "model", None, None, (), False, None),
        ("items", "list", None, None, (), False, None),
        ("meta", "dict", None, None, (), False, {}),
    )

    def __init__(self, name="", child=None, items=None, meta=None):
        super().__init__()
        self.name = name
        self.child = child
        self.items = [] if items is None else items
        self.meta = {} if meta is None else meta

    @classmethod
    def create(cls, name="", child=None, items=None, meta=None):
        return cls(name=name, child=child, items=items, meta=meta)


class parent_model(abstract_model):
    """Модель со ссылкой на вложенную модель по имени."""

    _fields = (
        ("child", "model", child_model, None, (), True, None),
    )

    def __init__(self, child=None):
        super().__init__()
        self.child = child

    @classmethod
    def create(cls, child=None):
        return cls(child=child)


def test_valid_result_from_dict_builds_all_kinds():
    """
    Проверяет сборку значений всех четырёх kind через from_dict.
    Ожидаемый результат: primitive приводится к str, остальные проходят chain.
    """
    # Подготовка
    source = {
        "name": 123,
        "child": {"id": 1},
        "items": [{"id": 2}],
        "meta": {"key": {"id": 3}},
    }
    chain = stub_chain()
    resolver = stub_resolver()

    # Действие
    model = dummy_model.from_dict(source, chain, resolver)

    # Проверки
    assert model.name == "123"
    assert model.child == {"id": 1}
    assert model.items == [{"id": 2}]
    assert model.meta == {"key": {"id": 3}}


def test_valid_result_from_dict_uses_defaults():
    """
    Проверяет значения по умолчанию для отсутствующих необязательных полей.
    Ожидаемый результат: model=null, list=[], dict={}.
    """
    # Подготовка
    source = {"name": "test"}
    chain = stub_chain()
    resolver = stub_resolver()

    # Действие
    model = dummy_model.from_dict(source, chain, resolver)

    # Проверки
    assert model.name == "test"
    assert model.child is None
    assert model.items == []
    assert model.meta == {}


def test_valid_result_from_dict_resolves_string_reference():
    """
    Проверяет разрешение строковой ссылки через резолвер имён.
    Ожидаемый результат: в поле попадает найденная модель.
    """
    # Подготовка
    child = child_model()
    resolver = stub_resolver({(child_model, "Milk"): child})
    source = {"child": "Milk"}
    chain = stub_chain()

    # Действие
    model = parent_model.from_dict(source, chain, resolver)

    # Проверки
    assert model.child is child


def test_invalid_result_from_dict_unknown_string_reference():
    """
    Проверяет ошибку при неизвестной строковой ссылке.
    Ожидаемый результат: arguments_exeption.
    """
    # Подготовка
    source = {"child": "Unknown"}
    chain = stub_chain()
    resolver = stub_resolver()

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        parent_model.from_dict(source, chain, resolver)

    # Проверки
    assert exc_info.value is not None


def test_invalid_result_from_dict_string_without_model_cls():
    """
    Проверяет строковую ссылку без класса модели.
    Ожидаемый результат: arguments_exeption.
    """
    # Подготовка
    source = {"name": "test", "child": "Unknown"}
    chain = stub_chain()
    resolver = stub_resolver()

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        dummy_model.from_dict(source, chain, resolver)

    # Проверки
    assert exc_info.value is not None


def test_invalid_result_from_dict_source_not_dict():
    """
    Проверяет валидацию source.
    Ожидаемый результат: не-dict вызывает arguments_exeption.
    """
    # Подготовка
    source = []
    chain = stub_chain()
    resolver = stub_resolver()

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        dummy_model.from_dict(source, chain, resolver)

    # Проверки
    assert exc_info.value is not None


def test_invalid_result_from_dict_chain_is_none():
    """
    Проверяет валидацию chain.
    Ожидаемый результат: None вызывает arguments_exeption.
    """
    # Подготовка
    source = {"name": "test"}
    chain = None
    resolver = stub_resolver()

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        dummy_model.from_dict(source, chain, resolver)

    # Проверки
    assert exc_info.value is not None


def test_invalid_result_from_dict_resolver_is_none():
    """
    Проверяет валидацию resolver.
    Ожидаемый результат: None вызывает arguments_exeption.
    """
    # Подготовка
    source = {"name": "test"}
    chain = stub_chain()
    resolver = None

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        dummy_model.from_dict(source, chain, resolver)

    # Проверки
    assert exc_info.value is not None


def test_invalid_result_from_dict_visited_not_set():
    """
    Проверяет валидацию visited.
    Ожидаемый результат: не-set вызывает arguments_exeption.
    """
    # Подготовка
    source = {"name": "test"}
    chain = stub_chain()
    resolver = stub_resolver()
    visited = []

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        dummy_model.from_dict(source, chain, resolver, visited=visited)

    # Проверки
    assert exc_info.value is not None


def test_invalid_result_build_model_bad_model_cls():
    """
    Проверяет валидацию model_cls в _build_model.
    Ожидаемый результат: класс, не наследующий abstract_model, вызывает ошибку.
    """
    # Подготовка
    source = {"id": 1}
    bad_model_cls = object
    chain = stub_chain()
    resolver = stub_resolver()
    visited = set()

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        dummy_model._build_model(source, bad_model_cls, chain, resolver, visited)

    # Проверки
    assert exc_info.value is not None


def test_invalid_result_build_value_unknown_kind():
    """
    Проверяет защиту диспетчера от неизвестного kind.
    Ожидаемый результат: arguments_exeption.
    """
    # Подготовка
    spec = field_spec("name")
    spec._field_spec__kind = "unknown"
    value = "value"
    chain = stub_chain()
    resolver = stub_resolver()
    visited = set()

    # Действие
    with pytest.raises(arguments_exeption) as exc_info:
        dummy_model._build_value(spec, value, chain, resolver, visited)

    # Проверки
    assert exc_info.value is not None


def test_valid_result_specs_are_cached():
    """
    Проверяет кэширование разобранных описаний полей.
    Ожидаемый результат: повторный вызов возвращает тот же кортеж.
    """
    # Подготовка
    first = dummy_model._specs()

    # Действие
    second = dummy_model._specs()

    # Проверки
    assert first is second

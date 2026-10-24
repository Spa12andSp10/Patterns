from datetime import date, datetime

from Src.Core.abstract_model import abstract_model
from Src.Core.abstract_convertor import abstract_convertor


def is_simple(source) -> bool:
    return isinstance(source, (str, int, float)) and not isinstance(source, bool)


def handle_simple(source, visited, factory):
    return factory.basic.convert(source)


def is_date(source) -> bool:
    return isinstance(source, (datetime, date))


def handle_date(source, visited, factory):
    return factory.date.convert(source)


def is_reference(source) -> bool:
    return isinstance(source, abstract_model)


def handle_reference(source, visited, factory):
    code = getattr(source, "unique_code", None)

    # Защита от циклов: повторную модель отдаём компактным описанием.
    if code is not None and code in visited:
        return {
            "unique_code": code,
            "type": getattr(source, "item_type", ""),
            "name": getattr(source, "name", ""),
        }

    if code is not None:
        visited.add(code)

    try:
        return factory.collect_members(source, visited)
    finally:
        if code is not None:
            visited.discard(code)


def is_list(source) -> bool:
    return isinstance(source, (list, tuple))


def handle_list(source, visited, factory):
    return {
        str(index): factory.convert(value, visited)
        for index, value in enumerate(source)
    }


def is_dict(source) -> bool:
    return isinstance(source, dict)


def handle_dict(source, visited, factory):
    return {
        key: factory.convert(value, visited)
        for key, value in source.items()
    }


def is_object_with_properties(source) -> bool:
    """Любой объект с публичными property (не только abstract_model).

    Нужен для разбора «обычных» объектов вроде тестовых Composite/WithList,
    которые не наследуют abstract_model, но имеют property-поля.
    """
    if source is None:
        return False
    return bool(abstract_convertor._public(source))


def handle_object_with_properties(source, visited, factory):
    return factory.collect_members(source, visited)
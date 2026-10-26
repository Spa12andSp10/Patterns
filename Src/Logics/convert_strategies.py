
from datetime import date, datetime

from Src.Core.abstract_model import abstract_model
from Src.Core.abstract_convertor import abstract_convertor
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor

_basic = basic_convertor()
_date = datetime_convertor()

def is_simple(source) -> bool:
    return isinstance(source, (str, int, float)) and not isinstance(source, bool)


def handle_simple(source, walker, visited):
    return _basic.convert(source)


def is_date(source) -> bool:
    return isinstance(source, (datetime, date))


def handle_date(source, walker, visited):
    return _date.convert(source)


def is_reference(source) -> bool:
    return isinstance(source, abstract_model)


def handle_reference(source, walker, visited):
    code = getattr(source, "unique_code", None)
    if code is not None and code in visited:
        return {
            "unique_code": code,
            "type": getattr(source, "item_type", ""),
            "name": getattr(source, "name", ""),
        }

    if code is not None:
        visited.add(code)

    try:
        return walker.collect_members(source, visited)
    finally:
        if code is not None:
            visited.discard(code)


def is_list(source) -> bool:
    return isinstance(source, (list, tuple))


def handle_list(source, walker, visited):
    return {
        str(index): walker.convert(value, visited)
        for index, value in enumerate(source)
    }


def is_dict(source) -> bool:
    return isinstance(source, dict)


def handle_dict(source, walker, visited):
    return {
        key: walker.convert(value, visited)
        for key, value in source.items()
    }


def is_object_with_properties(source) -> bool:
    if source is None:
        return False
    return bool(abstract_convertor._public(source))


def handle_object_with_properties(source, walker, visited):
    return walker.collect_members(source, visited)
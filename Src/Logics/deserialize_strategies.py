from Src.Logics.basic_deserialize_convertor import basic_deserialize_convertor
from Src.Logics.datetime_deserialize_convertor import datetime_deserialize_convertor
from Src.Logics.reference_deserialize_convertor import reference_deserialize_convertor

_basic = basic_deserialize_convertor()
_datetime = datetime_deserialize_convertor()


def is_date_value(source, resolver) -> bool:
    if not isinstance(source, dict) or set(source.keys()) != {"value"}:
        return False
    if not isinstance(source["value"], str):
        return False
    try:
        _datetime.convert(source)
        return True
    except Exception:
        return False


def is_value(source, resolver) -> bool:
    if not isinstance(source, dict) or set(source.keys()) != {"value"}:
        return False
    return not is_date_value(source, resolver)


def is_indexed_dict(source, resolver) -> bool:
    if not isinstance(source, dict) or not source:
        return False
    try:
        keys = sorted(source.keys(), key=int)
    except (TypeError, ValueError):
        return False
    return [str(i) for i in range(len(keys))] == keys


def is_model_dict(source, resolver) -> bool:
    if not isinstance(source, dict) or not source:
        return False
    if is_value(source, resolver) or is_date_value(source, resolver):
        return False
    if is_indexed_dict(source, resolver):
        return False
    return resolver.can_resolve(source)


def is_plain_dict(source, resolver) -> bool:
    return (
        isinstance(source, dict)
        and bool(source)
        and not is_value(source, resolver)
        and not is_date_value(source, resolver)
        and not is_indexed_dict(source, resolver)
        and not is_model_dict(source, resolver)
    )


def handle_date(source, chain, resolver, visited):
    return _datetime.convert(source)


def handle_value(source, chain, resolver, visited):
    return _basic.convert(source)


def handle_indexed_dict(source, chain, resolver, visited):
    keys = sorted(source.keys(), key=int)
    return [chain.deserialize(source[k], resolver, visited) for k in keys]


def handle_model(source, chain, resolver, visited):
    conv = reference_deserialize_convertor(resolver).bind(chain)
    return conv.convert(source, visited)


def handle_dict(source, chain, resolver, visited):
    return {k: chain.deserialize(v, resolver, visited) for k, v in source.items()}
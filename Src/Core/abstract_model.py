from __future__ import annotations

from abc import ABC
import uuid
from typing import Any

from Src.Core.deserializer import deserializer
from Src.Core.exception import arguments_exeption
from Src.Core.field_kind import field_kind
from Src.Core.field_spec import field_spec
from Src.Core.model_lookup import model_lookup
from Src.Core.validator import validator


class abstract_model(ABC):
    """Абстрактный базовый класс для доменных моделей.

    Содержит уникальный код, сравнение по коду и помощник
    разбора dict -> модель.
    """

    __unique_code: str
    __type: str = ""

    _fields: tuple = ()
    _field_aliases: dict = {"item_type": ("type",)}
    _field_overrides: dict = {}

    _VALUE_BUILDERS = {
        field_kind.PRIMITIVE: "_build_primitive",
        field_kind.MODEL: "_build_model_value",
        field_kind.LIST: "_build_list",
        field_kind.DICT: "_build_dict",
    }

    def __init__(self) -> None:
        super().__init__()
        self.__unique_code = uuid.uuid4().hex

    @property
    def unique_code(self) -> str:
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str) -> None:
        validator.validate(value, str, "unique_code")
        self.__unique_code = value.strip()

    @property
    def item_type(self) -> str:
        return self.__type

    @item_type.setter
    def item_type(self, value: str) -> None:
        validator.validate(value, str, "type")
        self.__type = value

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, abstract_model):
            return False
        return self.unique_code == value.unique_code

    @classmethod
    def _specs(cls) -> tuple[field_spec, ...]:
        """Разобранные описания полей (кэшируются отдельно для каждого класса)."""
        cached = cls.__dict__.get("_specs_cache")
        if cached is None:
            raw_fields = cls.__dict__.get("_fields")
            if raw_fields:
                cached = tuple(field_spec(*raw) for raw in raw_fields)
            else:
                from Src.Core.model_schema import model_schema
                cached = model_schema.fields(cls)
            cls._specs_cache = cached
        return cached

    @classmethod
    def required_keys(cls) -> frozenset:
        """Ключи, обязательные для сборки модели из dict."""
        return frozenset(spec.name for spec in cls._specs() if spec.required)

    @classmethod
    def entity_type(cls) -> str:
        return ""

    @staticmethod
    def _extract(source: dict, name: str, aliases: tuple = ()):
        """Достаёт значение по name или aliases."""
        if name in source:
            return True, source[name]
        for alias in aliases:
            if alias in source:
                return True, source[alias]
        return False, None

    @staticmethod
    def _as_list(value) -> list:
        """list или indexed_dict -> list."""
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return [value[k] for k in sorted(value.keys(), key=int)]
        return [value]

    @classmethod
    def _build_model(cls, raw: Any, model_cls: type[abstract_model] | None,
                     chain: deserializer, resolver: model_lookup,
                     visited: set[str]) -> Any:
        """dict/строка -> модель."""
        if model_cls is not None and not (
            isinstance(model_cls, type) and issubclass(model_cls, abstract_model)
        ):
            raise arguments_exeption(
                "model_cls", "Ожидался класс abstract_model или None"
            )

        if isinstance(raw, str):
            if model_cls is None:
                raise arguments_exeption(
                    "model_cls", "Для строковой ссылки требуется класс модели"
                )
            model = resolver.get_by_name(model_cls, raw)
            if model is None:
                raise arguments_exeption(
                    "model", f"{model_cls!r} с name={raw!r} не найден"
                )
            return model

        return chain.deserialize(raw, resolver, visited)

    @classmethod
    def _coerce_primitive(cls, value, cast, name: str):
        if cast is None:
            return value
        try:
            return cast(value)
        except (TypeError, ValueError) as e:
            raise arguments_exeption(
                name, f"Не удалось привести {value!r} к {cast.__name__}: {e}"
            )

    @classmethod
    def _build_primitive(cls, spec: field_spec, raw: Any, chain: deserializer,
                         resolver: model_lookup, visited: set[str]) -> Any:
        return cls._coerce_primitive(raw, spec.cast, spec.name)

    @classmethod
    def _build_model_value(cls, spec: field_spec, raw: Any,
                           chain: deserializer, resolver: model_lookup,
                           visited: set[str]) -> Any:
        return cls._build_model(raw, spec.model_cls, chain, resolver, visited)

    @classmethod
    def _build_list(cls, spec: field_spec, raw: Any, chain: deserializer,
                    resolver: model_lookup, visited: set[str]) -> list:
        return [
            cls._build_model(item, spec.model_cls, chain, resolver, visited)
            for item in cls._as_list(raw)
        ]

    @classmethod
    def _build_dict(cls, spec: field_spec, raw: Any, chain: deserializer,
                    resolver: model_lookup, visited: set[str]) -> dict:
        if not isinstance(raw, dict):
            raise arguments_exeption(spec.name, "Ожидался dict")
        return {
            key: chain.deserialize(value, resolver, visited)
            for key, value in raw.items()
        }

    @classmethod
    def _build_value(cls, spec: field_spec, raw: Any, chain: deserializer,
                     resolver: model_lookup, visited: set[str]) -> Any:
        """Строит значение одного поля."""
        builder_name = cls._VALUE_BUILDERS.get(spec.kind)
        if builder_name is None:
            raise arguments_exeption(
                "fields", f"Неизвестный kind={spec.kind!r} у поля {spec.name!r}"
            )
        builder = getattr(cls, builder_name)
        return builder(spec, raw, chain, resolver, visited)

    @classmethod
    def _default_for(cls, spec: field_spec) -> Any:
        if spec.default is not None:
            return spec.default
        if spec.kind == field_kind.LIST:
            return []
        if spec.kind == field_kind.DICT:
            return {}
        return None

    @classmethod
    def from_dict(cls, source: dict, chain: deserializer,
                  resolver: model_lookup,
                  visited: set[str] | None = None):
        """Собирает модель из dict по описанию полей."""
        if not isinstance(source, dict):
            raise arguments_exeption("source", "Ожидался dict")
        if not isinstance(chain, deserializer):
            raise arguments_exeption(
                "chain", "Ожидался объект с методом deserialize"
            )
        if not isinstance(resolver, model_lookup):
            raise arguments_exeption(
                "resolver", "Ожидался объект с методом get_by_name"
            )
        if visited is None:
            visited = set()
        elif not isinstance(visited, set):
            raise arguments_exeption("visited", "Ожидался set")

        kwargs = {}
        for spec in cls._specs():
            found, raw = cls._extract(source, spec.name, spec.aliases)
            if not found:
                if spec.required:
                    raise arguments_exeption(
                        spec.name,
                        f"Отсутствует обязательное поле {spec.name!r} "
                        f"при сборке {cls.__name__}",
                    )
                kwargs[spec.name] = cls._default_for(spec)
                continue
            if raw is None:
                kwargs[spec.name] = cls._default_for(spec)
                continue
            kwargs[spec.name] = cls._build_value(
                spec, raw, chain, resolver, visited
            )

        return cls.create(**kwargs)

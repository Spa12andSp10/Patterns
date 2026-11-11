from abc import ABC
import uuid
from typing import Any, Callable, NamedTuple

from Src.Core.validator import validator
from Src.Core.exception import arguments_exeption


class field_spec(NamedTuple):
    """Описание одного поля модели.

    kind: 'primitive' | 'model' | 'list' | 'dict'.
    """
    name: str
    kind: str = "primitive"
    model_cls: type | None = None
    cast: Callable[[Any], Any] | None = None
    aliases: tuple[str, ...] = ()
    required: bool = True
    default: Any = None


class abstract_model(ABC):
    """Абстрактный базовый класс для доменных моделей.

    Содержит уникальный код, сравнение по коду и помощник
    разбора dict -> модель.
    """

    __unique_code: str
    __type: str = ""

    _fields: tuple = ()

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
    def required_keys(cls) -> frozenset:
        """Ключи, обязательные для сборки модели из dict."""
        return frozenset(
            field_spec(*f).name
            for f in cls._fields
            if field_spec(*f).required
        )

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
    def _build_model(cls, raw, model_cls, chain, resolver, visited: set):
        """dict/строка → модель."""
        if isinstance(raw, str):
            cache = getattr(resolver, "_name_cache", {})
            bucket = cache.get(model_cls)
            if bucket is None:
                raise arguments_exeption(
                    "model",
                    f"Нет кэша имён для {model_cls!r}; "
                    f"строковая ссылка {raw!r} не разрешена",
                )
            model = bucket.get(raw)
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
    def _build_value(cls, spec: field_spec, raw, chain, resolver,
                     visited: set, source: dict):
        """Строит значение одного поля."""
        if spec.kind == "primitive":
            return cls._coerce_primitive(raw, spec.cast, spec.name)

        if spec.kind == "model":
            return cls._build_model(raw, spec.model_cls, chain, resolver, visited)

        if spec.kind == "list":
            return [
                cls._build_model(item, spec.model_cls, chain, resolver, visited)
                for item in cls._as_list(raw)
            ]

        if spec.kind == "dict":
            return {
                k: chain.deserialize(v, resolver, visited)
                for k, v in raw.items()
            }

        raise arguments_exeption(
            "fields", f"Неизвестный kind={spec.kind!r} у поля {spec.name!r}"
        )

    @classmethod
    def _default_for(cls, spec: field_spec):
        if spec.default is not None:
            return spec.default
        if spec.kind == "list":
            return []
        if spec.kind == "dict":
            return {}
        return None

    @classmethod
    def from_dict(cls, source: dict, chain, resolver, visited: set = None):
        """Собирает модель из dict по _fields."""
        if visited is None:
            visited = set()

        kwargs = {}
        for raw_spec in cls._fields:
            spec = field_spec(*raw_spec)
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
                spec, raw, chain, resolver, visited, source
            )

        return cls.create(**kwargs)
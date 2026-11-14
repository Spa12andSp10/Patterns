import inspect
import typing

from Src.Core.field_kind import field_kind
from Src.Core.field_spec import field_spec


class model_schema:
    """Строит описание полей доменной модели через рефлексию."""

    @classmethod
    def fields(cls, model_cls: type) -> tuple[field_spec, ...]:
        """Возвращает описания полей, выведенные из класса модели.

        :param model_cls: Класс доменной модели.
        :return: Кортеж описаний полей; пустой, если у класса нет ``create``.
        """
        create = getattr(model_cls, "create", None)
        if not callable(create):
            return ()

        signature = inspect.signature(create)
        create_hints = cls._hints(create)
        aliases = cls._merged_aliases(model_cls)
        overrides = cls._merged_overrides(model_cls)

        specs = []
        for name, parameter in signature.parameters.items():
            if name == "cls":
                continue
            specs.append(
                cls._spec(
                    model_cls, name, parameter,
                    create_hints, aliases, overrides,
                )
            )
        return tuple(specs)

    @classmethod
    def _spec(cls, model_cls: type, name: str, parameter: inspect.Parameter,
              create_hints: dict, aliases: dict,
              overrides: dict) -> field_spec:
        """Собирает описание одного поля.

        :param model_cls: Класс доменной модели.
        :param name: Имя поля.
        :param parameter: Параметр сигнатуры ``create``.
        :param create_hints: Разрешённые аннотации ``create``.
        :param aliases: Альтернативные имена полей.
        :param overrides: Исключения для required/default.
        :return: Описание поля.
        """
        annotation = cls._annotation(model_cls, name, create_hints)
        kind, model_cls_value = cls._kind(annotation)
        rule = overrides.get(name, {})

        required = rule.get(
            "required",
            parameter.default is inspect.Parameter.empty,
        )
        if "default" in rule:
            default = rule["default"]
        elif required:
            default = None
        elif parameter.default is not inspect.Parameter.empty:
            default = parameter.default
        else:
            default = None

        cast = None
        if kind is field_kind.PRIMITIVE and annotation in (str, int, float):
            cast = annotation

        return field_spec(
            name=name,
            kind=kind,
            model_cls=model_cls_value,
            cast=cast,
            aliases=aliases.get(name, ()),
            required=required,
            default=default,
        )

    @classmethod
    def _annotation(cls, model_cls: type, name: str,
                    create_hints: dict):
        """Определяет тип поля по property или параметру ``create``.

        :param model_cls: Класс доменной модели.
        :param name: Имя поля.
        :param create_hints: Разрешённые аннотации ``create``.
        :return: Разрешённая аннотация или None.
        """
        prop = inspect.getattr_static(model_cls, name, None)
        if isinstance(prop, property):
            hints = cls._hints(prop.fget)
            if "return" in hints:
                return hints["return"]
        return create_hints.get(name)

    @classmethod
    def _kind(cls, annotation) -> tuple[field_kind, type | None]:
        """Определяет способ построения значения поля.

        :param annotation: Аннотация типа поля.
        :return: Пара (kind, класс вложенной модели).
        """
        origin = typing.get_origin(annotation)
        args = typing.get_args(annotation)

        if annotation is dict or origin is dict:
            return field_kind.DICT, None

        if annotation in (list, tuple) or origin in (list, tuple):
            model_cls = cls._model_class(args[0]) if args else None
            return field_kind.LIST, model_cls

        model_cls = cls._model_class(annotation)
        if model_cls is not None:
            return field_kind.MODEL, model_cls

        return field_kind.PRIMITIVE, None

    @staticmethod
    def _model_class(annotation) -> type | None:
        """Возвращает класс доменной модели для аннотации.

        :param annotation: Аннотация типа поля.
        :return: Класс-наследник abstract_model или None.
        """
        from Src.Core.abstract_model import abstract_model

        if isinstance(annotation, type) and issubclass(annotation, abstract_model):
            return annotation
        return None

    @staticmethod
    def _hints(target) -> dict:
        """Безопасно разрешает аннотации объекта.

        :param target: Функция или property.fget.
        :return: Словарь аннотаций; пустой, если разрешить не удалось.
        """
        try:
            return typing.get_type_hints(target)
        except Exception:
            return {}

    @classmethod
    def _merged_aliases(cls, model_cls: type) -> dict:
        """Собирает альтернативные имена полей.

        :param model_cls: Класс доменной модели.
        :return: Словарь field_name -> tuple aliases.
        """
        result = {}
        for base in reversed(model_cls.__mro__):
            value = base.__dict__.get("_field_aliases", {})
            if isinstance(value, dict):
                result.update(value)
        return result

    @classmethod
    def _merged_overrides(cls, model_cls: type) -> dict:
        """Собирает исключения required/default.

        :param model_cls: Класс доменной модели.
        :return: Словарь field_name -> правила.
        """
        result = {}
        for base in reversed(model_cls.__mro__):
            value = base.__dict__.get("_field_overrides", {})
            if not isinstance(value, dict):
                continue
            for name, rule in value.items():
                result.setdefault(name, {}).update(rule)
        return result

from abc import ABC
from typing import Any, Callable

from Src.Core.exception import arguments_exeption
from Src.Core.field_kind import field_kind
from Src.Core.validator import validator


class field_spec(ABC):
    """Описание одного поля модели.

    kind: 'primitive' | 'model' | 'list' | 'dict'.
    """

    def __init__(self, name: str,
                 kind: str | field_kind = field_kind.PRIMITIVE,
                 model_cls: type | None = None,
                 cast: Callable[[Any], Any] | None = None,
                 aliases: tuple[str, ...] = (),
                 required: bool = True,
                 default: Any = None) -> None:
        super().__init__()
        self.name = name
        self.kind = kind
        self.model_cls = model_cls
        self.cast = cast
        self.aliases = aliases
        self.required = required
        self.default = default

    @property
    def name(self) -> str:
        """Возвращает имя поля."""
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        """Устанавливает имя поля.

        :param value: Непустая строка; пробелы по краям отбрасываются.
        :raises arguments_exeption: Если значение не строка или пустое.
        """
        validator.validate(value, str, "name")
        self.__name = value.strip()

    @property
    def kind(self) -> field_kind:
        """Возвращает способ построения значения поля."""
        return self.__kind

    @kind.setter
    def kind(self, value: str | field_kind) -> None:
        """Устанавливает способ построения значения поля.

        :param value: Строка или член field_kind.
        :raises arguments_exeption: Если значение не входит в field_kind.
        """
        if isinstance(value, field_kind):
            self.__kind = value
            return
        try:
            self.__kind = field_kind(value)
        except (TypeError, ValueError):
            raise arguments_exeption(
                "kind", f"Неизвестный kind={value!r}"
            ) from None

    @property
    def model_cls(self) -> type | None:
        """Возвращает класс вложенной модели (если есть)."""
        return self.__model_cls

    @model_cls.setter
    def model_cls(self, value: type | None) -> None:
        """Устанавливает класс вложенной модели.

        :param value: Класс или None.
        :raises arguments_exeption: Если значение не класс и не None.
        """
        if value is not None and not isinstance(value, type):
            raise arguments_exeption(
                "model_cls", "Некорректно переданный аргумент"
            )
        self.__model_cls = value

    @property
    def cast(self) -> Callable[[Any], Any] | None:
        """Возвращает функцию приведения примитива (если есть)."""
        return self.__cast

    @cast.setter
    def cast(self, value: Callable[[Any], Any] | None) -> None:
        """Устанавливает функцию приведения примитива.

        :param value: Callable или None.
        :raises arguments_exeption: Если значение не callable и не None.
        """
        if value is not None and not callable(value):
            raise arguments_exeption(
                "cast", "Некорректно переданный аргумент"
            )
        self.__cast = value

    @property
    def aliases(self) -> tuple[str, ...]:
        """Возвращает альтернативные имена поля."""
        return self.__aliases

    @aliases.setter
    def aliases(self, value: tuple[str, ...]) -> None:
        """Устанавливает альтернативные имена поля.

        :param value: Кортеж строк.
        :raises arguments_exeption: Если значение не кортеж.
        """
        if not isinstance(value, tuple):
            raise arguments_exeption(
                "aliases", "Некорректно переданный аргумент"
            )
        self.__aliases = value

    @property
    def required(self) -> bool:
        """Возвращает признак обязательности поля."""
        return self.__required

    @required.setter
    def required(self, value: bool) -> None:
        """Устанавливает признак обязательности поля.

        :param value: True или False.
        :raises arguments_exeption: Если значение не bool.
        """
        if not isinstance(value, bool):
            raise arguments_exeption(
                "required", "Некорректно переданный аргумент"
            )
        self.__required = value

    @property
    def default(self) -> Any:
        """Возвращает значение поля по умолчанию."""
        return self.__default

    @default.setter
    def default(self, value: Any) -> None:
        """Устанавливает значение поля по умолчанию."""
        self.__default = value

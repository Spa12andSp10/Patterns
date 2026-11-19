from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exeption
from Src.Core.validator import validator


class storage_repository:
    """Репозиторий для хранения списка объектов и счётчика связей."""

    def __init__(self) -> None:
        self.__data: dict = {}
        self.__counts: dict = {}

    def registry(self, source: abstract_model) -> None:
        """Регистрирует доменный объект и все его вложения.

        """
        validator.validate(source, abstract_model)
        self._register(source)

    def registry_range(self, items: list) -> None:
        """Регистрирует сразу же несколько объектов.

        """
        validator.validate(items, list)
        for item in items:
            self.registry(item)

    def get(self, source: str) -> abstract_model:
        """Возвращает объект по уникальному коду.

        """
        validator.validate(source, str)

        if source in self.__data:
            return self.__data[source]
        raise arguments_exeption(
            "unique_code", f"Не найдена доменная сущность по коду : {source}!"
        )

    def can_delete(self, source: abstract_model) -> bool:
        """Проверяет возможность удаления объекта.

        """
        validator.validate(source, abstract_model)

        code = source.unique_code
        if code not in self.__data:
            return False

        return self.__counts.get(code, 0) <= 0

    def delete(self, source: abstract_model) -> None:
        """Удаляет сущность из репозитория.

        """
        validator.validate(source, abstract_model)
        if not self.can_delete(source):
            raise arguments_exeption(
                "unique_code", f"Невозможно удалить запись {source.unique_code}!"
            )

        self.__data.pop(source.unique_code, None)
        self.__counts.pop(source.unique_code, None)

    @property
    def data(self) -> dict:
        """Исходный набор данных."""
        return self.__data

    @property
    def counts(self) -> dict:
        """Исходный набор счётчиков."""
        return self.__counts

    def _register(self, source: abstract_model) -> None:
        """Регистрирует объект и учитывает ссылки на его вложения.

        """
        code = source.unique_code
        if code in self.__data:
            return

        self.__data[code] = source
        self.__counts.setdefault(code, 0)

        for child in self._references(source):
            child_code = child.unique_code
            self.__counts[child_code] = self.__counts.get(child_code, 0) + 1
            self._register(child)

    @staticmethod
    def _references(source: abstract_model):
        """Отдаёт вложенные доменные модели из полей объекта.

        """
        for spec in source._specs():
            value = getattr(source, spec.name, None)
            yield from storage_repository._models_in(value)

    @staticmethod
    def _models_in(value):
        """Отдаёт доменные модели из значения поля.

        """
        if isinstance(value, abstract_model):
            yield value
            return

        if isinstance(value, dict):
            items = value.values()
        elif isinstance(value, (list, tuple)):
            items = value
        else:
            return

        for item in items:
            if isinstance(item, abstract_model):
                yield item

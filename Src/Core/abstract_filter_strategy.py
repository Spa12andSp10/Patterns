from abc import ABC, abstractmethod


class abstract_filter_strategy(ABC):
    """Стратегия обработки значения поля при фильтрации.
    """

    is_ordering: bool = False
    reverse: bool = False

    @abstractmethod
    def match(self, source: str, value: str) -> bool:
        """Проверяет, удовлетворяет ли значение условию.

        :param source: Фактическое значение поля.
        :param value: Значение из условия фильтрации.
        :return: True, если значение подходит.
        """
        ...

    def validate(self, value: str) -> None:
        """Проверяет корректность значения условия.

        По умолчанию значение не проверяется. Стратегии с особым
        форматом значения переопределяют метод.

        :param value: Значение из условия фильтрации.
        :raises arguments_exeption: Если значение некорректно.
        """
        return None


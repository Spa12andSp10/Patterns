"""Стратегии обработки значений полей при фильтрации.

Каждая стратегия отвечает на один вопрос: подходит ли конкретное значение
поля под условие фильтра. 
"""

from Src.Core.abstract_filter_strategy import abstract_filter_strategy
from Src.Core.exception import arguments_exeption


class equal_filter_strategy(abstract_filter_strategy):
    """Стратегия полного совпадения без учёта регистра.

    Пример: ``source="Milk"``, ``value="milk"`` -> True.
    """

    def match(self, source: str, value: str) -> bool:
        """Проверяет полное совпадение значения поля и условия.

        :param source: Фактическое значение поля (строка).
        :param value: Искомое значение из условия фильтрации.
        :return: True, если после нормализации строки одинаковы.
        """
        return source.strip().casefold() == value.strip().casefold()


class like_filter_strategy(abstract_filter_strategy):
    """Стратегия поиска подстроки без учёта регистра.

    Пример: ``source="Main warehouse"``, ``value="ware"``
    -> True.
    """

    def match(self, source: str, value: str) -> bool:
        """Проверяет, содержится ли искомая подстрока в значении поля.

        :param source: Фактическое значение поля (строка).
        :param value: Подстрока из условия фильтрации.
        :return: True, если подстрока найдена (без учёта регистра).
        """
        return value.strip().casefold() in source.strip().casefold()


class between_filter_strategy(abstract_filter_strategy):
    """Стратегия проверки попадания значения в диапазон.
    """

    SEPARATORS = ("..", ",")

    def validate(self, value: str) -> None:
        """Проверяет, что условие содержит корректно заданный диапазон.

        :param value: Строка с диапазоном, например ``"1..10"``.
        :raises arguments_exeption: Если разделитель или границы отсутствуют.
        """
        self.parse_bounds(value)

    def parse_bounds(self, value: str) -> tuple[str, str]:
        """Разбирает строку условия на нижнюю и верхнюю границы.

        :param value: Строка вида ``"min..max"`` (или ``"min,max"``).
        :return: Кортеж ``(нижняя_граница, верхняя_граница)`` без пробелов.
        :raises arguments_exeption: Если значение не строка, пустое,
            не содержит разделитель или одна из границ не заполнена.
        """
        if not isinstance(value, str) or not value.strip():
            raise arguments_exeption(
                "filter_value",
                "Для BETWEEN ожидался диапазон вида min..max",
            )

        raw = value.strip()
        parts = None

        for separator in self.SEPARATORS:
            if separator in raw:
                parts = raw.split(separator, 1)
                break

        if parts is None:
            raise arguments_exeption(
                "filter_value",
                "Для BETWEEN ожидался диапазон вида min..max",
            )

        low, high = (part.strip() for part in parts)
        if not low or not high:
            raise arguments_exeption(
                "filter_value",
                "Обе границы диапазона должны быть заполнены",
            )

        return low, high

    def match(self, source: str, value: str) -> bool:
        """Проверяет, попадает ли значение поля в заданный диапазон.

        :param source: Фактическое значение поля (строка).
        :param value: Строка с диапазоном, например ``"1..10"``.
        :return: True, если значение находится между границами включительно.
        """
        low, high = self.parse_bounds(value)
        actual = str(source).strip()

        low_number = self._to_number(low)
        high_number = self._to_number(high)
        actual_number = self._to_number(actual)

        if (
            low_number is not None
            and high_number is not None
            and actual_number is not None
        ):
            minimum, maximum = sorted((low_number, high_number))
            return minimum <= actual_number <= maximum

        minimum, maximum = sorted(
            (low.casefold(), high.casefold())
        )
        return minimum <= actual.casefold() <= maximum

    @staticmethod
    def _to_number(value: str) -> float | None:
        """Пытается преобразовать строку в число.
        :param value: Строка, которую нужно проверить на числовость.
        :return: Число или None, если строку нельзя преобразовать в float.
        """
        try:
            return float(str(value).strip().replace(",", "."))
        except (TypeError, ValueError):
            return None


class alphabet_filter_strategy(abstract_filter_strategy):
    """Стратегия сортировки по возрастанию (алфавиту).
    """

    is_ordering = True

    def __init__(self, reverse: bool = False) -> None:
        """Задаёт направление сортировки.

        :param reverse: False — по возрастанию, True — по убыванию.
        """
        self.reverse = reverse

    def match(self, source: str, value: str) -> bool:
        """Формально удовлетворяет контракту стратегии.

        :param source: Фактическое значение поля (не используется).
        :param value: Значение условия (не используется).
        :return: Всегда True.
        """
        return True

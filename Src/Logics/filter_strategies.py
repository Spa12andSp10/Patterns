from Src.Core.abstract_filter_strategy import abstract_filter_strategy
from Src.Core.exception import arguments_exeption


class equal_filter_strategy(abstract_filter_strategy):
    """Стратегия полного совпадения без учёта регистра."""

    def match(self, source: str, value: str) -> bool:
        return source.strip().casefold() == value.strip().casefold()


class like_filter_strategy(abstract_filter_strategy):
    """Стратегия поиска подстроки без учёта регистра."""

    def match(self, source: str, value: str) -> bool:
        return value.strip().casefold() in source.strip().casefold()


class between_filter_strategy(abstract_filter_strategy):

    SEPARATORS = ("..", ",")

    def validate(self, value: str) -> None:
        self.parse_bounds(value)

    def parse_bounds(self, value: str) -> tuple[str, str]:
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
        try:
            return float(str(value).strip().replace(",", "."))
        except (TypeError, ValueError):
            return None


class alphabet_filter_strategy(abstract_filter_strategy):

    is_ordering = True

    def __init__(self, reverse: bool = False) -> None:
        self.reverse = reverse

    def match(self, source: str, value: str) -> bool:
        return True

from Src.Core.abstract_filter_strategy import abstract_filter_strategy
from Src.Core.exception import arguments_exeption
from Src.Core.filters_type import filters_type
from Src.Logics.filter_strategies import alphabet_filter_strategy, between_filter_strategy, equal_filter_strategy, like_filter_strategy


class filter_strategy_factory:
    """Фабрика стратегий обработки условий фильтрации."""

    _strategies: dict = {
        filters_type.EQUALS: equal_filter_strategy(),
        filters_type.LIKE: like_filter_strategy(),
        filters_type.BETWEEN: between_filter_strategy(),
        filters_type.ALPHABET: alphabet_filter_strategy(reverse=False),
        filters_type.ALPHABET_DESC: alphabet_filter_strategy(reverse=True),
    }

    @classmethod
    def create(cls, filter_type: filters_type) -> abstract_filter_strategy:
        """Возвращает стратегию для указанного типа фильтра.

        """
        strategy = cls._strategies.get(filter_type)
        if strategy is None:
            raise arguments_exeption("filter_type", "Стратегия не реализована")

        return strategy

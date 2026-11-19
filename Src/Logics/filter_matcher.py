from Src.Core.exception import arguments_exeption
from Src.Dtos.filter_item_dto import filter_item_dto
from Src.Logics.field_path import field_path
from Src.Logics.filter_strategy_factory import filter_strategy_factory


class filter_matcher:
    """Применяет одно условие ``filter_item_dto`` к доменной модели.

    """

    def validate(self, item: filter_item_dto) -> None:
        """Проверяет корректность значения условия.
        """
        if not isinstance(item, filter_item_dto):
            raise arguments_exeption("filter", "Ожидался filter_item_dto")

        strategy = filter_strategy_factory.create(item.filter_type)
        strategy.validate(item.filter_value)

    def match(self, source, item: filter_item_dto) -> bool:
        """Проверяет сущность по одному условию фильтрации.

        """
        self.validate(item)

        if source is None:
            return False

        strategy = filter_strategy_factory.create(item.filter_type)
        if strategy.is_ordering:
            return True

        values = field_path.resolve(source, item.filter_name)
        if not values:
            return False

        for value in values:
            if value is None:
                continue

            actual = value if isinstance(value, str) else str(value)
            if strategy.match(actual, item.filter_value):
                return True

        return False

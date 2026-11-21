from Src.Core.abstract_prototype import abstract_prototype
from Src.Core.entity_type import entity_type
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.field_path import field_path
from Src.Logics.filter_matcher import filter_matcher
from Src.Logics.filter_strategy_factory import filter_strategy_factory
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.technicalmap_model import technicalmap_model


class prototype(abstract_prototype):
    """Универсальный прототип для списков DOMAIN-моделей.
.
    """

    DOMAIN_MODELS: dict = {
        entity_type.NOMENCLATURE.value: nomenclature_model,
        entity_type.GROUP.value: group_model,
        entity_type.RANGE.value: range_model,
        entity_type.RECIPE.value: technicalmap_model,
    }

    def __init__(self, data: list) -> None:
        """Инициализирует прототип.
        """
        super().__init__(data)
        self._matcher = filter_matcher()

    def clone(self, filters: filter_dto = None) -> "prototype":
        """Создаёт новый прототип с отфильтрованными текущими данными.

        """
        return prototype(self._filtered_data(filters))

    def _filtered_data(self, filters: filter_dto = None) -> list:
        """Возвращает данные, отфильтрованные и упорядоченные по условиям.
        """
        if filters is None:
            return list(self.data)

        for condition in filters:
            self._matcher.validate(condition)

        result = [
            item for item in self.data
            if self._matches(item, filters)
        ]
        return self._apply_ordering(result, filters)

    def _apply_ordering(self, data: list, filters: filter_dto) -> list:
        """Сортирует данные по условиям ALPHABET / ALPHABET_DESC.
        """
        ordering = [
            condition for condition in filters
            if filter_strategy_factory.create(
                condition.filter_type
            ).is_ordering
        ]

        for condition in reversed(ordering):
            strategy = filter_strategy_factory.create(condition.filter_type)
            data.sort(
                key=lambda item, cond=condition: self._sort_key(item, cond),
                reverse=strategy.reverse,
            )

        return data

    def _sort_key(self, item, condition) -> tuple:
        """Возвращает ключ сортировки по полю условия.
        """
        values = field_path.resolve(item, condition.filter_name)
        value = values[0] if values else ""

        if value is None or value == "":
            return (2, "")

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return (0, float(value))

        return (1, str(value).casefold())

    def _matches(self, item, filters: filter_dto) -> bool:
        """Проверяет объект по всем условиям фильтра.

        """
        if not self._matches_domain(item, filters.domain):
            return False

        return all(
            self._matcher.match(item, condition)
            for condition in filters
        )

    def _matches_domain(self, item, domain: str) -> bool:
        """Проверяет принадлежность объекта к выбранной DOMAIN-модели.
        """
        if not domain:
            return True

        model_cls = self.DOMAIN_MODELS.get(domain)
        return model_cls is not None and isinstance(item, model_cls)

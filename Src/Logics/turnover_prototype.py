from Src.Core.abstract_prototype import abstract_prototype
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.prototype import prototype


class turnover_prototype(abstract_prototype):
    """Прототип списка транзакций для оборотно-сальдовой ведомости.
    """

    def clone(self, filters: filter_dto = None) -> "turnover_prototype":
        """Создаёт новый прототип с отфильтрованными транзакциями.

        :param filters: Условия фильтрации.
        :return: Новый прототип, исходный не меняется.
        """
        filtered = prototype(self.data).clone(filters).data
        return turnover_prototype(filtered)

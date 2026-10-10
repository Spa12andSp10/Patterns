from Src.Models.technicalmap_model import technicalmap_model


class technicalmap_factory:
    """Фабрика технологических карт (рецептов)."""

    @staticmethod
    def create(ingredients: list, preparation_method: dict,
               description: str, time: str,
               name: str = "") -> technicalmap_model:
        """Универсальный метод — по составу и параметрам.

        :param ingredients: Список ингредиентов блюда.
        :param preparation_method: Словарь {наименование: способ}.
        :param description: Текстовая инструкция.
        :param time: Время приготовления.
        :param name: Краткое наименование блюда.
        :return: Созданная технологическая карта.
        """
        return technicalmap_model(
            ingredients=ingredients,
            preparation_method=preparation_method,
            description=description,
            time=time,
            name=name,
        )
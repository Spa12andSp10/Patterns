from Src.Models.ingredient_model import ingredient_model


class ingredient_factory:
    """Фабрика ингредиентов."""

    @staticmethod
    def create(full_name: str, brutto: float, proteins: float,
               fats: float, carbohydrates: float,
               coef: float, type: str = "product") -> ingredient_model:
        """Универсальный метод — по параметрам ингредиента.

        :param full_name: Полное наименование ингредиента.
        :param brutto: Масса брутто.
        :param proteins: Количество белков.
        :param fats: Количество жиров.
        :param carbohydrates: Количество углеводов.
        :param coef: Коэффициент пересчёта.
        :param type: Тип (product / semi_finished / packaging).
        :return: Созданный ингредиент.
        """
        return ingredient_model(
            full_name=full_name, brutto=brutto, proteins=proteins,
            fats=fats, carbohydrates=carbohydrates, coef=coef, type=type
        )
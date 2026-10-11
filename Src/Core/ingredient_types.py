class ingredient_type:
    """Справочник типов ингредиентов.

    Единый источник правды для всех модулей: и модель ингредиента,
    и технологическая карта используют эти константы, а не строки.
    Это устраняет хрупкость к переименованию типов.
    """

    PRODUCT = "product"
    SEMI_FINISHED = "semi_finished"
    PACKAGING = "packaging"

    ALL = frozenset({PRODUCT, SEMI_FINISHED, PACKAGING})

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Проверяет, что значение — допустимый тип ингредиента.

        :param value: Проверяемое значение.
        :return: True, если значение входит в справочник.
        """
        return value in cls.ALL
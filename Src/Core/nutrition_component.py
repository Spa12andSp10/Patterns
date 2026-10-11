from abc import ABC, abstractmethod


class nutrition_component(ABC):
    """Общий контракт для всего, что может входить в состав блюда.

    Реализуется и одиночным ингредиентом (ingredient_model),
    и вложенной технологической картой (technicalmap_model).
    Позволяет единообразно и рекурсивно считать брутто, нетто
    и БЖУ, поддерживая конструкцию «блюдо в блюде».

    Параметр visited — множество unique_code уже посещённых карт,
    защищает от циклических ссылок при рекурсивном обходе.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Краткое наименование компонента."""
        ...

    @property
    @abstractmethod
    def full_name(self) -> str:
        """Полное наименование компонента."""
        ...

    @property
    @abstractmethod
    def unique_code(self) -> str:
        """Уникальный код компонента (для отслеживания циклов)."""
        ...

    @abstractmethod
    def calculate_brutto(self, visited: set = None) -> float:
        """Считает суммарное брутто компонента.

        :param visited: Множество unique_code посещённых карт.
        :return: Суммарная масса брутто.
        """
        ...

    @abstractmethod
    def calculate_netto(self, visited: set = None) -> float:
        """Считает суммарное нетто компонента.

        :param visited: Множество unique_code посещённых карт.
        :return: Суммарная масса нетто.
        """
        ...

    @abstractmethod
    def calculate_proteins(self, visited: set = None) -> float:
        """Считает суммарные белки компонента.

        :param visited: Множество unique_code посещённых карт.
        :return: Суммарное количество белков.
        """
        ...

    @abstractmethod
    def calculate_fats(self, visited: set = None) -> float:
        """Считает суммарные жиры компонента.

        :param visited: Множество unique_code посещённых карт.
        :return: Суммарное количество жиров.
        """
        ...

    @abstractmethod
    def calculate_carbohydrates(self, visited: set = None) -> float:
        """Считает суммарные углеводы компонента.

        :param visited: Множество unique_code посещённых карт.
        :return: Суммарное количество углеводов.
        """
        ...
from Src.Core.entity_model import entity_model


class group_model(entity_model):
    """Модель группы номенклатуры.

    Содержит определение: наименование.
    Создаётся через classmethod-конструктор create.
    """

    def __init__(self, name: str = "") -> None:
        """Инициализирует группу номенклатуры.

        :param name: Наименование группы.
        """
        super().__init__()
        self.name = name

    @classmethod
    def create(cls, name: str) -> "group_model":
        """Создаёт группу номенклатуры по наименованию.

        :param name: Наименование группы.
        :return: Созданная группа.
        """
        return cls(name=name)
from Src.Core.entity_model import entity_model


class group_model(entity_model):
    """Модель группы номенклатуры."""

    _fields = (
        ("name", "primitive", None, str),
    )

    def __init__(self, name: str = "") -> None:
        super().__init__()
        self.name = name

    @classmethod
    def create(cls, name: str) -> "group_model":
        return cls(name=name)
from Src.Models.group_model import group_model


class group_factory:
    """Фабрика групп номенклатуры."""

    @staticmethod
    def create(name: str) -> group_model:
        """Универсальный метод — по имени."""
        return group_model(name=name)
from Src.Models.warehouse_model import warehouse_model


class warehouse_factory:
    """Фабрика складов."""

    @staticmethod
    def create(name: str, address: str) -> warehouse_model:
        return warehouse_model(name=name, address=address)
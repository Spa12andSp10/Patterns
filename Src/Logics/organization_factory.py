from Src.Models.organization_model import organization_model


class organization_factory:
    """Фабрика организаций."""

    @staticmethod
    def create(name: str, inn: str, bic: str,
               account: str, owner: str) -> organization_model:
        return organization_model(
            name=name, inn=inn, bic=bic, account=account, owner=owner
        )
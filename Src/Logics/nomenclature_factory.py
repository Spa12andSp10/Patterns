from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model


class nomenclature_factory:
    """Фабрика номенклатуры."""

    @staticmethod
    def create(full_name: str, name: str,
               group: group_model, rng: range_model, type: str) -> nomenclature_model:
        return nomenclature_model(
            name=name, full_name=full_name, group=group, range=rng, type=type
        )
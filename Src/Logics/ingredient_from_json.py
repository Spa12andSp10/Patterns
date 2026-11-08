from Src.Core.abstract_deserialization_convertor_factory import abstract_deserialization_convertor_factory
from Src.Core.entity_type import entity_type
from Src.Core.exception import arguments_exeption
from Src.Core.validator import validator
from Src.Logics.model_repository import model_repository
from Src.Models.ingredient_model import ingredient_model


class ingredient_from_json(abstract_deserialization_convertor_factory):
    """Конвертер dict -> ingredient_model."""

    entity = entity_type.INGREDIENT

    @classmethod
    def create(cls, repository: model_repository) -> "ingredient_from_json":
        return cls(repository)

    def __init__(self, repository: model_repository) -> None:
        self._repository = repository

    def deserialize(self, source: dict) -> ingredient_model:
        validator.validate(source, dict, "source")

        unique_code = source.get("unique_code")
        if unique_code is None:
            raise arguments_exeption("unique_code", "Отсутствует unique_code")

        existing = self._repository.get(unique_code)
        if existing is not None:
            return existing

        full_name = source.get("full_name")
        if not full_name:
            raise arguments_exeption("full_name", "Отсутствует full_name")

        brutto = self._require_number(source, "brutto")
        proteins = self._require_number(source, "proteins")
        fats = self._require_number(source, "fats")
        carbohydrates = self._require_number(source, "carbohydrates")
        coef = self._require_number(source, "coef")

        item_type = source.get("item_type")

        model = ingredient_model.create(
            full_name=full_name, brutto=brutto, proteins=proteins,
            fats=fats, carbohydrates=carbohydrates, coef=coef,
            item_type=item_type,
        )
        model.unique_code = unique_code
        return self._repository.put_in_cloud(model)

    @staticmethod
    def _require_number(source: dict, field: str) -> float:
        value = source.get(field)
        validator.validate(value, (float, int))
        return float(value)
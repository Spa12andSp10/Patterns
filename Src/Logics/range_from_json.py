from Src.Core.abstract_deserialization_convertor_factory import abstract_deserialization_convertor_factory

from Src.Core.entity_type import entity_type
from Src.Core.exception import arguments_exeption
from Src.Core.validator import validator
from Src.Logics.model_repository import model_repository
from Src.Models.range_model import range_model


class range_from_json(abstract_deserialization_convertor_factory):
    """Конвертер dict -> range_model."""

    entity = entity_type.RANGE

    @classmethod
    def create(cls, repository: model_repository) -> "range_from_json":
        return cls(repository)

    def __init__(self, repository: model_repository):
        self._repository = repository

    def deserialize(self, source: dict) -> range_model:
        validator.validate(source, dict, "source")

        unique_code = source.get("unique_code")
        if unique_code is None:
            raise arguments_exeption("unique_code", "Отсутствует unique_code")
        exist = self._repository.get(unique_code)
        if exist is not None:
            return exist

        name = source.get("name")
        validator.validate(name, str, "name")

        conversion_factor = source.get("conversion_factor")
        validator.validate(conversion_factor, float, "conversion_factor")

        base_data = source.get("base")
        base = self.deserialize(base_data) if base_data is not None else None

        model = range_model.create(name, conversion_factor, base)
        model.unique_code = unique_code
        return self._repository.put_in_cloud(model)
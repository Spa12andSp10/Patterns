from Src.Core.abstract_deserialization_convertor_factory import abstract_deserialization_convertor_factory
from Src.Core.entity_type import entity_type
from Src.Core.exception import arguments_exeption
from Src.Core.validator import validator
from Src.Logics.model_repository import model_repository
from Src.Models.technicalmap_model import technicalmap_model


class technicalmap_from_json(abstract_deserialization_convertor_factory):
    """Конвертер dict -> technicalmap_model.

    Вложенные ингредиенты создаются через общую фабрику.
    """

    entity = entity_type.RECIPE

    @classmethod
    def create(cls, repository: model_repository) -> "technicalmap_from_json":
        return cls(repository)

    def __init__(self, repository: model_repository) -> None:
        from Src.Logics.deserialization_convertor_factory import  deserialization_convertor_factory
        self._repository = repository
        factory = deserialization_convertor_factory(repository)
        self._ingredient_converter = factory.create(entity_type.INGREDIENT)

    def deserialize(self, source: dict) -> technicalmap_model:
        validator.validate(source, dict, "source")

        unique_code = source.get("unique_code")
        if unique_code is None:
            raise arguments_exeption("unique_code", "Отсутствует unique_code")
        exist = self._repository.get(unique_code)
        if exist is not None:
            return exist

        name = source.get("name")
        validator.validate(name, str, "name")

        description = source.get("description")
        validator.validate(description, str, "description")

        time = source.get("time")
        validator.validate(time, str, "time")

        ingredient_data = source.get("ingredients")
        if ingredient_data is None:
            raise arguments_exeption("ingredients", "Отсутствует ingredients")
        if not isinstance(ingredient_data, dict):
            raise arguments_exeption("ingredients", "Должен быть словарём")

        ingredient = [
            self._ingredient_converter.deserialize(i)
            for i in ingredient_data.values()
        ]

        method_data = source.get("preparation_method", {})
        if not isinstance(method_data, dict):
            raise arguments_exeption("preparation_method", "Должен быть словарём")

        preparation_method = {}
        for key, value in method_data.items():
            if isinstance(value, dict):
                v = value.get("value")
            else:
                v = value
            if v is None:
                raise arguments_exeption(
                    "preparation_method", f"Отсутствует value для '{key}'"
                )
            preparation_method[key] = v

        model = technicalmap_model.create(
            ingredient, preparation_method, description, time, name,
        )
        model.unique_code = unique_code
        return self._repository.put_in_cloud(model)
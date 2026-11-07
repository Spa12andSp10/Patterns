from Src.Core.abstract_deserialization_convertor_factory import abstract_deserialization_convertor_factory
from Src.Core.validator import validator
from Src.Core.exception import arguments_exeption
from Src.Models.technicalmap_model import technicalmap_model
from Src.Logics.model_repository import model_repository
from Src.Logics.ingredient_from_json import ingredient_from_json


class technicalmap_from_json(abstract_deserialization_convertor_factory):
    """Конвертер dict -> technicalmap_model.

    Создаёт technicalmap_model по полям unique_code, name, description,
    time, ingredients, preparation_method. Вложенные ингредиенты
    разрешаются через ingredient_from_json: если объект с таким
    unique_code уже есть в model_repository, возвращается
    существующий — это разрешает повторные ссылки при
    десериализации графа.
    """

    def __init__(self, repository: model_repository) -> None:
        self._repository = repository
        self._ingredient_converter = ingredient_from_json(repository)

    def convert(self, source: dict) -> technicalmap_model:
        """Конвертор"""
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
            self._ingredient_converter.convert(i)
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
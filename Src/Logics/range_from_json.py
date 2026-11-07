from Src.Core.abstract_deserialization_convertor_factory import abstract_deserialization_convertor_factory
from Src.Models.range_model import range_model
from Src.Core.validator import validator
from Src.Core.exception import arguments_exeption
from Src.Logics.model_repository import model_repository


class range_from_json(abstract_deserialization_convertor_factory):
    """Конвертер dict -> range_model.

    Создаёт range_model по полям unique_code, name, conversion_factor, base.
    База (base) разрешается рекурсивно через convert: если объект
    с таким unique_code уже есть в model_repository, возвращается
    существующий — это разрешает повторные ссылки и цепочки
    единиц измерения без дубликатов.
    """

    def __init__(self, repository: model_repository):
        self._repository = repository

    def convert(self, source: dict) -> range_model:
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

        conversion_factor = source.get("conversion_factor")
        validator.validate(conversion_factor, float, "conversion_factor")

        base_data = source.get("base")
        base = self.convert(base_data) if base_data is not None else None

        model = range_model.create(name, conversion_factor, base)
        model.unique_code = unique_code
        return self._repository.put_in_cloud(model)
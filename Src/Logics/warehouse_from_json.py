from Src.Core.abstract_deserialization_convertor_factory import abstract_deserialization_convertor_factory
from Src.Models.warehouse_model import warehouse_model
from Src.Core.validator import validator
from Src.Core.exception import arguments_exeption
from Src.Logics.model_repository import model_repository


class warehouse_from_json(abstract_deserialization_convertor_factory):
    """Конвертер dict ->< warehouse_model.

    Создаёт warehouse_model по полям unique_code, name, address.
    Если объект с таким unique_code уже есть в model_repository,
    возвращает существующий — это разрешает повторные ссылки
    при десериализации модельного графа.
    """

    def __init__(self, repository: model_repository):
        self._repository = repository

    def convert(self, source: dict) -> warehouse_model:
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

        address = source.get("address")
        validator.validate(address, str, "address")

        model = warehouse_model.create(name, address)
        model.unique_code = unique_code
        return self._repository.put_in_cloud(model)
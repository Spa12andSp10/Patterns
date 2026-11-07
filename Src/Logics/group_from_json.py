from Src.Core.abstract_deserialization_convertor_factory import abstract_deserialization_convertor_factory
from Src.Models.group_model import group_model
from Src.Core.validator import validator
from Src.Core.exception import arguments_exeption
from Src.Logics.model_repository import model_repository

class group_from_json(abstract_deserialization_convertor_factory):

    """Конвертер dict -> group_model.

    Создаёт group_model по unique_code/name из JSON.
    Если объект с таким unique_code уже есть в model_repository —
    возвращает существующий (кэш для разрешения повторных ссылок).
    """

    def __init__(self, repository: model_repository):
        self._repository = repository

    def convert(self, source: dict) -> group_model:

        """Конвертер""" 

        validator.validate(source, dict)

        unique_code = source.get("unique_code")
        if unique_code is None:
            raise arguments_exeption("unique_code", "Отсутствует unique_code")
        exist = self._repository.get(unique_code)
        if exist is not None:
            return exist

        name = source.get("name")
        validator.validate(name, str)

        model = group_model.create(name)
        model.unique_code = unique_code
        

        return self._repository.put_in_cloud(model)

        
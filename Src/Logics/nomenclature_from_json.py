from Src.Core.abstract_deserialization_convertor_factory import abstract_deserialization_convertor_factory
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.validator import validator
from Src.Core.exception import arguments_exeption
from Src.Logics.model_repository import model_repository
from Src.Logics.group_from_json import group_from_json
from Src.Logics.range_from_json import range_from_json


class nomenclature_from_json(abstract_deserialization_convertor_factory):
    """Конвертер dict -> nomenclature_model.

    Создаёт nomenclature_model по полям unique_code, full_name, name,
    item_type, group, range. Вложенные group и range разрешаются
    через соответствующие конвертеры: если объект с таким unique_code
    уже есть в model_repository, возвращается существующий —
    это разрешает повторные ссылки при десериализации графа.
    """

    def __init__(self, repository: model_repository):
        self._repository = repository
        self._group_converter = group_from_json(repository)
        self._range_converter = range_from_json(repository)

    def convert(self, source: dict) -> nomenclature_model:
        """Конвертор"""
        validator.validate(source, dict, "source")

        unique_code = source.get("unique_code")
        if unique_code is None:
            raise arguments_exeption("unique_code", "Отсутствует unique_code")
        exist = self._repository.get(unique_code)
        if exist is not None:
            return exist

        full_name = source.get("full_name")
        validator.validate(full_name, str, "full_name")

        name = source.get("name")
        validator.validate(name, str, "name")

        item_type = source.get("item_type")
        validator.validate(item_type, str, "item_type")

        group_data = source.get("group")
        if group_data is None:
            raise arguments_exeption("group", "Отсутствует group")
        group = self._group_converter.convert(group_data)

        range_data = source.get("range")
        if range_data is None:
            raise arguments_exeption("range", "Отсутствует range")
        range_ = self._range_converter.convert(range_data)

        model = nomenclature_model.create(
            full_name, name, group, range_, item_type,
        )
        model.unique_code = unique_code
        return self._repository.put_in_cloud(model)
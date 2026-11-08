from Src.Core.abstract_deserialization_convertor_factory import abstract_deserialization_convertor_factory
from Src.Core.entity_type import entity_type
from Src.Core.exception import arguments_exeption
from Src.Core.validator import validator
from Src.Logics.model_repository import model_repository
from Src.Models.nomenclature_model import nomenclature_model


class nomenclature_from_json(abstract_deserialization_convertor_factory):
    """Конвертер dict -> nomenclature_model.

    Вложенные group/range создаются через общую фабрику —
    конвертер не знает о конкретных классах своих зависимостей.
    """

    entity = entity_type.NOMENCLATURE

    @classmethod
    def create(cls, repository: model_repository) -> "nomenclature_from_json":
        return cls(repository)

    def __init__(self, repository: model_repository):
        from Src.Logics.deserialization_convertor_factory import deserialization_convertor_factory
        self._repository = repository
        factory = deserialization_convertor_factory(repository)
        self._group_converter = factory.create(entity_type.GROUP)
        self._range_converter = factory.create(entity_type.RANGE)

    def deserialize(self, source: dict) -> nomenclature_model:
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
        group = self._group_converter.deserialize(group_data)

        range_data = source.get("range")
        if range_data is None:
            raise arguments_exeption("range", "Отсутствует range")
        range_ = self._range_converter.deserialize(range_data)

        model = nomenclature_model.create(
            full_name, name, group, range_, item_type,
        )
        model.unique_code = unique_code
        return self._repository.put_in_cloud(model)
from Src.Core.abstract_deserialization_convertor_factory import abstract_deserialization_convertor_factory
from Src.Models.organization_model import organization_model
from Src.Core.validator import validator
from Src.Core.exception import arguments_exeption
from Src.Logics.model_repository import model_repository


class organization_from_json(abstract_deserialization_convertor_factory):
    """Конвертер dict -> organization_model.

    Создаёт organization_model по полям unique_code, name, inn, bic,
    account, owner. Контрольные суммы ИНН и счёта проверяются
    валидатором. Если объект с таким unique_code уже есть
    в model_repository, возвращает существующий — это разрешает
    повторные ссылки при десериализации модельного графа.
    """

    def __init__(self, repository: model_repository):
        self._repository = repository

    def convert(self, source: dict) -> organization_model:
        """Конвертор"""
        validator.validate(source, dict, "source")

        unique_code = source.get("unique_code")
        if unique_code is None:
            raise arguments_exeption("unique_code", "Отсутствует unique_code")
        exist = self._repository.get(unique_code)
        if exist is not None:
            return exist

        account = source.get("account")
        validator.validate(account, str, "account")
        validator.check_account(account, source.get("bic"))

        inn = source.get("inn")
        validator.validate(inn, str, "inn")
        validator.check_inn(inn)

        bic = source.get("bic")
        validator.validate(bic, str, "bic")

        name = source.get("name")
        validator.validate(name, str, "name")

        owner = source.get("owner")
        validator.validate(owner, str, "owner")

        model = organization_model.create(name, inn, bic, account, owner)
        model.unique_code = unique_code
        return self._repository.put_in_cloud(model)
from Src.Core.abstract_model import abstract_model
from Src.Models.organization_model import organization_model
from Src.Core.validator import validator
from Src.Core.exception import arguments_exeption
from Src.Dtos.report_type_enum import report_type_enum


class settings_model(abstract_model):
    """Модель настроек приложения.

    Содержит карточку организации, ФИО руководителя и главного
    бухгалтера, а также флаг первого запуска.
    """

    __organization: organization_model = None
    __boss_name: str = ""
    __account_name: str = ""
    __first_launch_flag: bool = True
    __max_len_boss_name = 255
    __max_len_account_name = 255
    __response_format = "TXT"

    @property
    def organization(self) -> organization_model:
        """Возвращает карточку организации."""
        return self.__organization

    @organization.setter
    def organization(self, value: organization_model = None):
        validator.validate(value, organization_model, "organization")
        self.__organization = value

    @property
    def boss_name(self) -> str:
        """Возвращает ФИО руководителя."""
        return self.__boss_name

    @boss_name.setter
    def boss_name(self, value: str) -> None:
        validator.validate(value, str, "boss_name", max_len=self.__max_len_boss_name)
        self.__boss_name = value

    @property
    def account_name(self) -> str:
        """Возвращает ФИО главного бухгалтера."""
        return self.__account_name

    @account_name.setter
    def account_name(self, value: str):
        validator.validate(value, str, "account_name", max_len=self.__max_len_account_name)
        self.__account_name = value

    @property
    def first_launch_flag(self) -> bool:
        return self.__first_launch_flag

    @first_launch_flag.setter
    def first_launch_flag(self, new_flag: bool):
        validator.validate(new_flag, bool, "first_launch_flag")
        self.__first_launch_flag = new_flag

    @property
    def response_format(self) -> str:
        """Возвращает базовый формат данных (значение из settings.json)."""
        return self.__response_format

    @response_format.setter
    def response_format(self, value: str) -> None:
        validator.validate(value, str, "response_format")
        try:
            report_type_enum.from_slug(value)
        except ValueError:
            raise arguments_exeption(
                "response_format", f"Недопустимый формат: {value!r}."
            )
        self.__response_format = value
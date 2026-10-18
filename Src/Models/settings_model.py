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
        """Устанавливает карточку организации.

        :param value: Новая карточка организации.
        :raises arguments_exeption: Если значение не organization_model.
        """
        validator.validate(value, organization_model, "organization")
        self.__organization = value

    @property
    def boss_name(self) -> str:
        """Возвращает ФИО руководителя."""
        return self.__boss_name

    @boss_name.setter
    def boss_name(self, value: str) -> None:
        """Устанавливает ФИО руководителя.

        :param value: ФИО руководителя (строка до 255 символов).
        :raises arguments_exeption: Если значение не строка или None.
        :raises max_length_exeption: Если длина превышает 255 символов.
        """
        validator.validate(value, str, "boss_name", max_len=self.__max_len_boss_name)
        self.__boss_name = value

    @property
    def account_name(self) -> str:
        """Возвращает ФИО главного бухгалтера."""
        return self.__account_name

    @account_name.setter
    def account_name(self, value: str):
        """Устанавливает ФИО главного бухгалтера.

        :param value: ФИО главного бухгалтера (строка до 255 символов).
        :raises arguments_exeption: Если значение не строка или None.
        :raises max_length_exeption: Если длина превышает 255 символов.
        """
        validator.validate(value, str, "account_name", max_len=self.__max_len_account_name)
        self.__account_name = value

    @property
    def first_launch_flag(self) -> bool:
        """Возвращает флаг первого запуска."""
        return self.__first_launch_flag

    @first_launch_flag.setter
    def first_launch_flag(self, new_flag: bool):
        """Устанавливает флаг первого запуска.

        :param new_flag: Новое значение флага (True/False).
        :raises arguments_exeption: Если значение не bool.
        """
        validator.validate(new_flag, bool, "first_launch_flag")
        self.__first_launch_flag = new_flag

    @property
    def response_format(self) -> str:
        """Возвращает базовый формат данных (значение из settings.json)."""
        return self.__response_format

    @response_format.setter
    def response_format(self, value: str) -> None:
        """Устанавливает новый базовый формат данных.

        Формат проверяется по единому справочнику report_type_enum —
        это единственный источник истины о поддерживаемых форматах.
        from_slug регистронезависим, поэтому 'HTML', 'html' и 'Html'
        считаются одним и тем же форматом.

        :param value: Новый строчный базовый формат данных (str).
        :raises arguments_exeption: Если значение не строка или None.
        :raises arguments_exeption: Если формат отсутствует в report_type_enum.
        """
        validator.validate(value, str, "response_format")
        try:
            report_type_enum.from_slug(value)
        except ValueError:
            raise arguments_exeption(
                "response_format", f"Недопустимый формат: {value!r}."
            )
        self.__response_format = value
import json

from Src.Core.abstract_manager import abstract_manager
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model
from Src.Core.validator import validator


class settings_manager(abstract_manager):
    """Менеджер для работы с настройками (Singleton).

    Читает JSON-файл настроек, преобразует его в settings_model
    и предоставляет доступ к «сырым» данным через свойство data.
    """

    __default_file_name = "settings.json"
    _settings: settings_model = settings_model()

    __required_top_keys = (
        "organization",
        "account_name",
        "boss_name",
        "first_launch_flag",
    )
    __required_org_keys = (
        "name",
        "inn",
        "bic",
        "account",
        "owner",
    )
    
    def __new__(cls):
        """Реализует шаблон Singleton.

        :return: Единственный экземпляр settings_manager.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    def load(self, file_name: str = "") -> None:
        """Загружает настройки из JSON-файла.

        :param file_name: Путь к файлу. Если пусто — используется
            значение по умолчанию (settings.json).
        """
        inner_file_name = file_name if file_name != "" else self.__default_file_name
        self._is_loaded = False
        try:
            with open(inner_file_name, "r") as file:
                self._data = json.load(file)
        except Exception as e:
            return
        
        self._is_loaded = self.convert()

    def convert(self) -> bool:
        """Преобразует «сырые» данные JSON в settings_model.

        Все проверки структуры JSON делегируются validator.

        :return: True, если преобразование прошло успешно.
        :raises arguments_exeption: Если в JSON отсутствует обязательный
            ключ или значение поля некорректно.
        """
        validator.require_keys(
            self._data,
            self.__required_top_keys,
            field="settings"
        )

        org_data = self._data["organization"]
        validator.require_dict(org_data, field="organization")

        validator.require_keys(
            org_data,
            self.__required_org_keys,
            field="organization"
        )

        org = organization_model(
            name=org_data["name"],
            inn=org_data["inn"],
            bic=org_data["bic"],
            account=org_data["account"],
            owner=org_data["owner"],
        )

        self._settings.organization = org
        self._settings.account_name = self._data["account_name"]
        self._settings.boss_name = self._data["boss_name"]
        self._settings.first_launch_flag = self._data["first_launch_flag"]
        return True

    @property
    def settings(self) -> settings_model:
        """Возвращает загруженную модель настроек."""
        return self._settings

    @settings.setter
    def settings(self, value: settings_model):
        """Устанавливает модель настроек.

        :param value: Новая модель настроек.
        """
        self._settings = value

    @property
    def data(self) -> dict:
        """Возвращает «сырые» данные JSON (нужно storage_manager)."""
        return self._data
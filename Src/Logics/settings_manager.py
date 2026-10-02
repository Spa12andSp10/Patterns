import json

from Src.Core.abstract_manager import abstract_manager
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model


class settings_manager(abstract_manager):
    """Менеджер для работы с настройками (Singleton).

    Читает JSON-файл настроек, преобразует его в settings_model
    и предоставляет доступ к «сырым» данным через свойство data.
    """

    __default_file_name = "settings.json"
    _settings: settings_model = settings_model()

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
        with open(inner_file_name, "r") as file:
            self._data = json.load(file)
        self._is_loaded = self.convert()

    def convert(self) -> bool:
        """Преобразует «сырые» данные JSON в settings_model.

        :return: True, если преобразование прошло успешно, иначе False.
        """
        try:
            org_data = self._data.get("organization")

            if org_data is None:
                return False

            org = organization_model(
                name=org_data["name"],
                inn=org_data["inn"],
                bic=org_data["bic"],
                account=org_data["account"],
                owner=org_data["owner"]
            )
            self._settings.organization = org
            self._settings.account_name = self._data["account_name"]
            self._settings.boss_name = self._data["boss_name"]
            self._settings.first_launch_flag = self._data["first_launch_flag"]
            return True
        except Exception:
            return False

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
import json

from Src.Core.abstract_manager import abstract_manager
from Src.Logics.convert_factory import convert_factory
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model
from Src.Core.validator import validator


class settings_manager(abstract_manager):
    """Менеджер для работы с настройками (Singleton)."""

    __default_file_name = "settings.json"
    _settings: settings_model = settings_model()

    __required_top_keys = (
        "organization", "account_name", "boss_name", "first_launch_flag", "response_format"
    )
    __required_org_keys = (
        "name", "inn", "bic", "account", "owner",
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

        :param file_name: Путь к файлу настроек. Если пусто — ищет settings.json.
        """
        inner_file_name = file_name if file_name != "" else self.__default_file_name
        self._is_loaded = False
        try:
            with open(inner_file_name, "r", encoding="utf-8") as file:
                self._data = json.load(file)
        except Exception:
            return
        self._is_loaded = self.convert()


    def save(self, file_name: str = "") -> bool:
        """Сохраняет «сырые» данные self._data обратно в JSON-файл.

        :param file_name: Путь к файлу. Если пусто — settings.json.
        :return: True, если запись прошла успешно, иначе False.
        """
        inner_file_name = file_name if file_name != "" else self.__default_file_name
        if not self._data:
            return False
        try:
            with open(inner_file_name, "w", encoding="utf-8") as file:
                json.dump(self._data, file, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False

    def save_settings(self, file_name: str = "") -> bool:
        """Сохраняет текущую модель self._settings в JSON-файл.

        Сериализация доменных моделей делегируется convert_factory,
        чтобы не дублировать логику обхода property-полей.

        :param file_name: Путь к файлу. Если пусто — settings.json.
        :return: True, если запись прошла успешно, иначе False.
        """
        inner_file_name = file_name if file_name != "" else self.__default_file_name
        try:
            factory = convert_factory.create_default()
            payload = factory.convert(self._settings)
            data = json.loads(convert_factory.to_json(payload))

            with open(inner_file_name, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            # Синхронизируем «сырые» данные, чтобы save() потом
            # записал актуальное состояние.
            self._data = data
            return True
        except OSError:
            return False


    def convert(self) -> bool:
        """Преобразует «сырые» данные JSON в settings_model.

        :return: True, если преобразование прошло успешно.
        """
        validator.require_keys(self._data, self.__required_top_keys, field="settings")

        org_data = self._data["organization"]
        validator.require_dict(org_data, field="organization")
        validator.require_keys(org_data, self.__required_org_keys, field="organization")

        org = organization_model.create(
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
        self._settings.response_format = self._data["response_format"]
        return True

    @property
    def settings(self) -> settings_model:
        """Возвращает модель настроек."""
        return self._settings

    @settings.setter
    def settings(self, value: settings_model):
        """Устанавливает модель настроек."""
        self._settings = value

    @property
    def data(self) -> dict:
        """Возвращает словарь с «сырыми» данными из JSON."""
        return self._data
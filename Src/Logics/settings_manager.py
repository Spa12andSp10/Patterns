import json
from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import base_exception, arguments_exeption
from Src.Models.settings_model import settings_model
from Src.Logics.settings_deserializer import settings_deserializer
from Src.Logics.convert_factory import convert_factory
from Src.Core.abstract_convertor import abstract_convertor


class settings_manager(abstract_manager):
    """Singleton-менеджер настроек приложения."""

    __default_file_name = "settings.json"

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._settings: settings_model = None
            self._file_name: str = self.__default_file_name
            self._is_loaded: bool = False

    @property
    def settings(self) -> settings_model:
        """Возвращает модель настроек (или пустую с дефолтами, если не загружено)."""
        if self._settings is None:
            self._settings = settings_model()
        return self._settings

    @settings.setter
    def settings(self, value: settings_model) -> None:
        if not isinstance(value, settings_model):
            raise arguments_exeption("settings", "Ожидалась settings_model")
        self._settings = value
        self._is_loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def file_name(self) -> str:
        return self._file_name

    def load(self, file_name: str = "") -> bool:
        """Загружает настройки из файла через settings_deserializer."""
        inner = file_name or self._file_name
        model = settings_deserializer.load(inner)
        if model is None:
            return False

        self._settings = model
        self._file_name = inner
        self._is_loaded = True
        return True

    def reload(self) -> bool:
        """Перечитывает настройки из того же файла."""
        return self.load(self._file_name)

    def save(self, file_name: str = "") -> bool:
        """Сохраняет настройки в файл через общий механизм walker."""
        if self._settings is None:
            return False

        inner = file_name or self._file_name

        try:
            walker = convert_factory().create()
            raw = walker.convert(self._settings)
            data = json.loads(abstract_convertor.to_json(raw))
            with open(inner, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (OSError, base_exception):
            return False

        self._file_name = inner
        return True
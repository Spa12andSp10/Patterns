import json
from Src.Core.abstract_convertor import abstract_convertor
from Src.Logics.convert_factory import convert_factory
from Src.Logics.storage_manager import storage_manager


class storage_persistence:
    """Чтение/запись storage_data.json.

    Отвечает за I/O и сериализацию моделей.
    """

    __default_file_name = "storage_data.json"

    def __init__(self, storage: storage_manager):
        self._storage = storage

    @staticmethod
    def _read_json(file_name: str) -> dict:
        with open(file_name, "r", encoding="utf-8") as file:
            return json.load(file)

    def load_raw(self, file_name: str = "") -> dict:
        """Читает «сырой» JSON. Десериализация — не здесь.

        :return: Словарь из файла или {} при ошибке.
        """
        inner = file_name if file_name != "" else self.__default_file_name
        try:
            return self._read_json(inner)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_raw(self, data: dict, file_name: str = "") -> bool:
        """Сохраняет «сырой» словарь обратно в файл."""
        inner = file_name if file_name != "" else self.__default_file_name
        if not data:
            return False
        try:
            with open(inner, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False

    def save_models(self, file_name: str = "") -> bool:
        """Сериализует текущие доменные модели в JSON-файл."""
        inner = file_name if file_name != "" else self.__default_file_name
        serializer = convert_factory().create()

        payload = {
            "groups":       [serializer.convert(g) for g in self._storage.groups],
            "ranges":       [serializer.convert(r) for r in self._storage.ranges],
            "nomenclature": [serializer.convert(n) for n in self._storage.nomenclatures],
            "warehouse":    [serializer.convert(w) for w in self._storage.warehouses],
            "recipes":      [serializer.convert(r) for r in self._storage.recipes],
        }

        try:
            data = json.loads(abstract_convertor.to_json(payload))
            with open(inner, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False
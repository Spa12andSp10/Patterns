from abc import ABC
import uuid

from Src.Core.exception import arguments_exeption


class abstact_model(ABC):
    """Абстрактный базовый класс для доменных моделей.

    Содержит только генерацию уникального кода и сравнение
    объектов по этому коду.
    """

    __unique_code: str

    def __init__(self) -> None:
        """Инициализирует экземпляр и генерирует уникальный код."""
        super().__init__()
        self.__unique_code = uuid.uuid4().hex

    @property
    def unique_code(self) -> str:
        """Возвращает уникальный код объекта."""
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str) -> None:
        """Устанавливает уникальный код объекта.

        :param value: Новый уникальный код (строка без пробелов по краям).
        :raises arguments_exeption: Если значение пустое или состоит из пробелов.
        """
        if value is None or not isinstance(value, str) or value.strip() == "":
            raise arguments_exeption("unique_code", "Некорректно переданный аргумент!")
        self.__unique_code = value.strip()

    def __eq__(self, value: object) -> bool:
        """Сравнивает объекты по уникальному коду.

        :param value: Объект для сравнения.
        :return: True, если unique_code совпадает, иначе False.
        :raises arguments_exeption: Если передан объект не типа abstact_model.
        """
        if not isinstance(value, abstact_model):
            raise arguments_exeption("value", "Некорректно переданный аргумент")
        return self.unique_code == value.unique_code
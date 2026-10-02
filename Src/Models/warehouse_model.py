from Src.Core.entity_model import entity_model
from Src.Core.exception import arguments_exeption, max_length_exeption
from Src.Core.validator import validator


class warehouse_model(entity_model):
    """Модель склада.

    Содержит определения: наименование, адрес и максимальную
    длину адреса.
    """

    __address: str = ""
    __max_len_address: int = 255

    def __init__(self, name: str = "", address: str = "") -> None:
        """Инициализирует склад.

        :param name: Наименование склада.
        :param address: Адрес склада.
        """
        super().__init__()
        self.name = name
        self.address = address

    @property
    def address(self) -> str:
        """Возвращает адрес склада."""
        return self.__address

    @address.setter
    def address(self, value: str) -> None:
        """Устанавливает адрес склада.

        :param value: Адрес склада.
        :raises arguments_exeption: Если значение не строка или None.
        :raises max_length_exeption: Если длина превышает максимально допустимую.
        """
        validator.validate(value, str, "address", max_len=self.__max_len_address)
        self.__address = value
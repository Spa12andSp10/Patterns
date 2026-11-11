from Src.Core.entity_model import entity_model
from Src.Core.validator import validator


class warehouse_model(entity_model):
    """Модель склада."""

    __address: str = ""
    __max_len_address: int = 255

    _fields = (
        ("name", "primitive", None, str),
        ("address", "primitive", None, str),
    )

    def __init__(self, name: str = "", address: str = "") -> None:
        super().__init__()
        self.name = name
        self.address = address

    @classmethod
    def create(cls, name: str, address: str) -> "warehouse_model":
        return cls(name=name, address=address)

    @property
    def address(self) -> str:
        return self.__address

    @address.setter
    def address(self, value: str) -> None:
        validator.validate(value, str, "address", max_len=self.__max_len_address)
        self.__address = value
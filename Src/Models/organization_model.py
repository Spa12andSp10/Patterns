from Src.Core.entity_model import entity_model
from Src.Core.validator import validator


class organization_model(entity_model):
    """Модель организации."""

    __inn: str = ""
    __bic: str = ""
    __account: str = ""
    __owner: str = ""
    __len_inn: int = 10
    __len_bic: int = 9
    __len_account: int = 20
    __max_len_owner: int = 50

    _fields = (
        ("name", "primitive", None, str),
        ("inn", "primitive", None, str),
        ("bic", "primitive", None, str),
        ("account", "primitive", None, str),
        ("owner", "primitive", None, str),
    )

    def __init__(self, name: str = "", inn: str = "", bic: str = "",
                 account: str = "", owner: str = "") -> None:
        super().__init__()
        self.name = name
        self.inn = inn
        self.bic = bic
        self.account = account
        self.owner = owner

    @classmethod
    def create(cls, name: str, inn: str, bic: str,
               account: str, owner: str) -> "organization_model":
        return cls(name=name, inn=inn, bic=bic,
                   account=account, owner=owner)

    @property
    def inn(self) -> str:
        return self.__inn

    @inn.setter
    def inn(self, value: str) -> None:
        validator.validate(value, str, "inn", self.__len_inn)
        validator.digit_validate(value, "inn")
        validator.check_inn(value)
        self.__inn = value

    @property
    def bic(self) -> str:
        return self.__bic

    @bic.setter
    def bic(self, value: str) -> None:
        validator.validate(value, str, "bic", self.__len_bic)
        validator.digit_validate(value, "bic")
        self.__bic = value

    @property
    def account(self) -> str:
        return self.__account

    @account.setter
    def account(self, value: str) -> None:
        validator.validate(value, str, "account", self.__len_account)
        validator.digit_validate(value, "account")
        validator.check_account(value, self.__bic)
        self.__account = value

    @property
    def owner(self) -> str:
        return self.__owner

    @owner.setter
    def owner(self, value: str) -> None:
        validator.validate(value, str, "owner", max_len=self.__max_len_owner)
        self.__owner = value
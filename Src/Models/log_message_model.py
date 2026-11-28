from datetime import date

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exeption


"""Модель сообщения логоьтв"""
class log_message_model(abstract_model):

    __period: date
    __system_name: str = ""
    __message_type: str = ""
    __message: str = ""

    def __init__(self):
        super().__init__()
        self.period = date.today()

    @classmethod
    def create(cls, period: date | str, system_name: str, message_type: str, message: str) -> "log_message_model":
        item = cls()
        item.period = period
        item.system_name = system_name
        item.message_type = message_type
        item.message = message
        return item

    @property
    def period(self) -> date:
        return self.__period

    @period.setter
    def period(self, value: date | str) -> None:
        self.__period = self._to_datetime(value)

    @staticmethod
    def _to_datetime(value: date | str) -> date:
        """Перевод к верной дате"""
        if type(value) is date:
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value.strip())
            except ValueError:
                raise arguments_exeption("period", "Некорректная дата, ожидался формат YYYY-MM-DD")
        raise arguments_exeption("period", "Ожидались дата или ISO-строка YYYY-MM-DD")

    @property
    def system_name(self) -> str:
        return self.__system_name

    @system_name.setter
    def system_name(self, value: str) -> None:
        self.__system_name = str(value)

    @property
    def message_type(self) -> str:
        return self.__message_type

    @message_type.setter
    def message_type(self, value) -> None:
        self.__message_type = getattr(value, "value", str(value))

    @property
    def message(self) -> str:
        return self.__message

    @message.setter
    def message(self, value: str) -> None:
        self.__message = str(value)

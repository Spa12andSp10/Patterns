from Src.Core.entity_model import entity_model
from Src.Core.validator import validator
from Src.Core.exception import arguments_exeption


class report_data_dto(entity_model):
    """DTO для табличных данных отчёта.

    Хранит заголовки таблицы и строки данных. Используется всеми
    форматами отчётов (TXT, HTML, CSV, XML, Markdown, PNG) как
    универсальный промежуточный формат.
    """

    __header: list = []
    __rows: list = []

    @property
    def header(self) -> list:
        """Возвращает список заголовков таблицы."""
        return self.__header

    @header.setter
    def header(self, value: list) -> None:
        """Устанавливает заголовки таблицы.

        :param value: Список заголовков (строки).
        :raises arguments_exeption: Если значение не список.
        """
        if not isinstance(value, list):
            raise arguments_exeption("header", "Должен быть списком")
        self.__header = value

    @property
    def rows(self) -> list:
        """Возвращает список строк данных."""
        return self.__rows

    @rows.setter
    def rows(self, value: list) -> None:
        """Устанавливает строки данных.

        :param value: Список строк (каждая строка — список ячеек).
        :raises arguments_exeption: Если значение не список.
        """
        if not isinstance(value, list):
            raise arguments_exeption("rows", "Должен быть списком")
        self.__rows = value

    @classmethod
    def create(cls, header: list, rows: list) -> "report_data_dto":
        """Создаёт DTO табличных данных.

        :param header: Список заголовков.
        :param rows: Список строк данных.
        :return: Созданный DTO.
        """
        dto = cls()
        dto.header = header
        dto.rows = rows
        return dto
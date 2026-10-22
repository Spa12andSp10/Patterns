from Src.Core.entity_model import entity_model
from Src.Core.validator import validator
from Src.Core.exception import arguments_exeption


class report_result_dto(entity_model):
    """Модель для хранения результата формирования отчета.

    Может содержать либо текстовый результат (HTML, XML, TXT),
    либо бинарный файл (CSV, PNG, Markdown). Дополнительно хранит
    MIME-тип результата — его выставляет сам отчёт, чтобы потребитель
    (main.py, контроллер) не знал, какой формат перед ним.
    """

    __text: str = ""
    __binary: bytes = b''
    __mime: str = ""

    @property
    def text(self) -> str:
        """Возвращает текстовый результат отчета."""
        return self.__text

    @text.setter
    def text(self, value: str) -> None:
        """Устанавливает текстовый результат.

        При установке текста бинарные данные очищаются.
        :param value: Текст отчета.
        :raises arguments_exeption: Если значение не строка.
        """
        validator.validate(value, str)
        self.__text = value
        self.__binary = b''

    @property
    def binary(self) -> bytes:
        """Возвращает бинарный результат отчета (файл)."""
        return self.__binary

    @property
    def is_binary(self) -> bool:
        """True, если результат — бинарный (готовый файл), иначе текстовый."""
        return bool(self.__binary)

    @binary.setter
    def binary(self, value: bytes) -> None:
        """Устанавливает бинарный результат.

        При установке бинарных данных текстовый результат очищается.
        :param value: Байты файла.
        :raises arguments_exeption: Если значение не bytes или bytearray.
        """
        if not isinstance(value, (bytes, bytearray)):
            raise arguments_exeption("binary", "Ожидалось bytes")
        if len(value) > 0:
            self.__text = ""
            self.__binary = bytes(value)

    @property
    def mime(self) -> str:
        """Возвращает MIME-тип результата (например, 'text/csv; charset=utf-8')."""
        return self.__mime

    @mime.setter
    def mime(self, value: str) -> None:
        """Устанавливает MIME-тип результата.

        :param value: MIME-строка.
        :raises arguments_exeption: Если значение не строка или пустое.
        """
        validator.validate(value, str, "mime")
        self.__mime = value.strip()
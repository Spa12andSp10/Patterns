# Src/Dtos/report_type_enum.py
from enum import Enum


class report_type_enum(Enum):
    """Типы отчёта.

    Каждому значению сопоставлен MIME-тип, который используется
    при отдаче отчёта клиенту (браузеру — для рендеринга,
    программе — для парсинга).
    """

    TXT      = (1, "text/plain; charset=utf-8")
    CSV      = (2, "text/csv; charset=utf-8")
    MARKDOWN = (3, "text/markdown; charset=utf-8")
    XML      = (4, "application/xml; charset=utf-8")
    HTML     = (5, "text/html; charset=utf-8")
    PNG      = (6, "text/png")

    def __init__(self, code: int, mime: str):
        """Инициализирует элемент перечисления.

        :param code: Уникальный числовой код формата.
        :param mime: MIME-тип для формирования HTTP-заголовка Content-Type.
        """
        self.code = code
        self.mime = mime

    @property
    def slug(self) -> str:
        """Строка для URL/query: 'txt', 'markdown', 'xml', 'html', 'csv'."""
        return self.name.lower()

    @classmethod
    def from_slug(cls, slug: str) -> "report_type_enum":
        """Ищет тип отчёта по строке.

        :param slug: Строка формата (например, 'html').
        :raises ValueError: Если формат неизвестен.
        """
        slug = (slug or "").strip().lower()
        for item in cls:
            if item.slug == slug:
                return item
        raise ValueError(f"Неизвестный формат: {slug!r}")

    @classmethod
    def all_slugs(cls) -> list[str]:
        """Список всех допустимых slug'ов."""
        return [item.slug for item in cls]
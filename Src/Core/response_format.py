class response_format:
    """Справочник допустимых форматов ответа (значения из settings.json)."""

    CSV = "CSV"
    MARKDOWN = "Markdown"
    XML = "XML"
    TXT = "TXT"
    HTML = "HTML"

    ALL = frozenset({CSV, MARKDOWN, XML, TXT, HTML})

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Проверяет, что значение — допустимый формат ответа."""
        return value in cls.ALL
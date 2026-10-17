from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_data_extractor import report_data_extractor

class markdown_report(abstract_report):
    """Формирует отчет в формате Markdown-таблицы."""

    def build(self, source):
        """Формирует Markdown-текст из доменной модели.

        :param source: Доменная модель (рецепт, номенклатура, единица измерения).
        :return: DTO с бинарными данными (Markdown, UTF-8).
        """
        validator.validate(source, object, "source")
        
        header, rows = report_data_extractor.extract(source)

        header_str = "| " + " | ".join(str(h) for h in header) + " |\n"
        
        separator = "|" + "|".join([":---:" for _ in header]) + "|\n"

        data = ""
        for row in rows:
            data += "| " + " | ".join(str(c) for c in row) + " |\n"

        markdown = header_str + separator + data
        
        result = report_result_dto()
        result.binary = markdown.encode("utf-8")
        return result
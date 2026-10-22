from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.report_data_extractor import report_data_extractor


class markdown_report(abstract_report):
    """Формирует отчет в формате Markdown-таблицы."""

    def build(self, source):
        validator.validate(source, object, "source")

        data = report_data_extractor.extract(source)

        header_str = "| " + " | ".join(str(h) for h in data.header) + " |\n"
        separator = "|" + "|".join([":---:" for _ in data.header]) + "|\n"

        body = ""
        for row in data.rows:
            body += "| " + " | ".join(str(c) for c in row) + " |\n"

        markdown = header_str + separator + body

        result = report_result_dto()
        result.binary = markdown.encode("utf-8")
        result.mime = report_type_enum.MARKDOWN.mime
        return result
from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.report_data_extractor import report_data_extractor


class text_report(abstract_report):
    """Формирует отчет в виде простого текста (TXT)."""

    def build(self, source):
        validator.validate(source, object, "source")

        data = report_data_extractor.extract(source)

        text_lines = [" | ".join(str(h) for h in data.header)]
        for row in data.rows:
            text_lines.append(" | ".join(str(c) for c in row))

        result = report_result_dto()
        result.text = "\n".join(text_lines)
        result.mime = report_type_enum.TXT.mime
        return result
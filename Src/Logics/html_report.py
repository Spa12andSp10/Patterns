from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.report_data_extractor import report_data_extractor


class html_report(abstract_report):
    """Формирует отчет в формате HTML-таблицы."""

    __STYLE = (
        "table { border-collapse: collapse; } "
        "th, td { border: 1px solid #999; padding: 4px 8px; } "
        "th { background: #eee; }"
    )

    def build(self, source):
        validator.validate(source, object, "source")

        data = report_data_extractor.extract(source)

        parts = [
            "<!DOCTYPE html>",
            "<html><head><meta charset=\"utf-8\"><title>Отчёт</title>",
            f"<style>{self.__STYLE}</style>",
            "</head><body>",
            "<h1>Отчёт</h1>",
            "<table>",
            "<thead><tr>",
        ]

        for h in data.header:
            parts.append(f"<th>{h}</th>")
        parts.append("</tr></thead>")

        parts.append("<tbody>")
        for row in data.rows:
            parts.append("<tr>")
            for cell in row:
                parts.append(f"<td>{cell}</td>")
            parts.append("</tr>")
        parts.append("</tbody>")

        parts.append("</table>")
        parts.append("</body></html>")

        result = report_result_dto()
        result.text = "".join(parts)
        result.mime = report_type_enum.HTML.mime
        return result
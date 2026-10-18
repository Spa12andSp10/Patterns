from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_data_extractor import report_data_extractor


class html_report(abstract_report):
    """Формирует отчет в формате HTML-таблицы.

    Шаблон статический, поэтому обходимся без шаблонизатора:
    собираем разметку обычной конкатенацией строк.
    """

    __STYLE = (
        "table { border-collapse: collapse; } "
        "th, td { border: 1px solid #999; padding: 4px 8px; } "
        "th { background: #eee; }"
    )

    def build(self, source):
        """Формирует HTML-код из доменной модели.

        :param source: Доменная модель (рецепт, номенклатура, единица измерения).
        :return: DTO с текстом HTML.
        """
        validator.validate(source, object, "source")

        header, rows = report_data_extractor.extract(source)

        parts = [
            "<!DOCTYPE html>",
            "<html><head><meta charset=\"utf-8\"><title>Отчёт</title>",
            f"<style>{self.__STYLE}</style>",
            "</head><body>",
            "<h1>Отчёт</h1>",
            "<table>",
            "<thead><tr>",
        ]

        for h in header:
            parts.append(f"<th>{h}</th>")
        parts.append("</tr></thead>")

        parts.append("<tbody>")
        for row in rows:
            parts.append("<tr>")
            for cell in row:
                parts.append(f"<td>{cell}</td>")
            parts.append("</tr>")
        parts.append("</tbody>")

        parts.append("</table>")
        parts.append("</body></html>")

        result = report_result_dto()
        result.text = "".join(parts)
        return result
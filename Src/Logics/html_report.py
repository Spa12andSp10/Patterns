from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_data_extractor import report_data_extractor
from jinja2 import Environment, BaseLoader

class html_report(abstract_report):
    """Формирует отчет в формате HTML-таблицы."""

    def build(self, source):
        """Формирует HTML-код из доменной модели.

        :param source: Доменная модель (рецепт, номенклатура, единица измерения).
        :return: DTO с текстом HTML.
        """
        validator.validate(source, object, "source")
        
        header, data = report_data_extractor.extract(source)

        template_str = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Отчёт</title>
<style>table { border-collapse: collapse; } th, td { border: 1px solid #999; padding: 4px 8px; } th { background: #eee; }</style>
</head><body>
    <h1>Отчёт</h1>
    <table>
        <thead><tr>
            {% for h in header %}<th>{{ h }}</th>{% endfor %}
        </tr></thead>
        <tbody>
            {% for row in rows %}
            <tr>
                {% for cell in row %}<td>{{ cell }}</td>{% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body></html>"""

        env = Environment(loader=BaseLoader())
        html = env.from_string(template_str).render(header=header, rows=data)

        result = report_result_dto()
        result.text = html
        return result
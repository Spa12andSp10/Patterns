from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_data_extractor import report_data_extractor


class text_report(abstract_report):
    """Формирует отчет в виде простого текста (TXT).
    
    Данные представляются в виде плоской таблицы, разделенной
    вертикальными чертами (|), что удобно для чтения в консоли
    или простых текстовых редакторах.
    """

    def build(self, source):
        """Формирует текстовое представление доменной модели.

        :param source: Доменная модель (рецепт, номенклатура, единица измерения).
        :return: DTO с текстовым результатом.
        """
        validator.validate(source, object, "source")
        
        header, rows = report_data_extractor.extract(source)
        
        text_lines = [" | ".join(str(h) for h in header)]
        
        for row in rows:
            text_lines.append(" | ".join(str(c) for c in row))
            
        result = report_result_dto()
        result.text = "\n".join(text_lines)
        return result
from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_data_extractor import report_data_extractor
import csv
import io

class csv_report(abstract_report):
    """Формирует отчет в формате CSV."""

    def build(self, source):
        """Формирует CSV-файл (в виде байтов) из доменной модели.

        :param source: Доменная модель (рецепт, номенклатура, единица измерения).
        :return: DTO с бинарными данными (UTF-8 BOM).
        """
        validator.validate(source, object, "source")
        
        header, rows = report_data_extractor.extract(source)
        data = [header] + rows

        buffer = io.StringIO()
        write = csv.writer(buffer, lineterminator='\n')
        write.writerows(data)

        csv_bytes = ("\ufeff" + buffer.getvalue()).encode("utf-8")

        result = report_result_dto()
        result.binary = csv_bytes
        return result
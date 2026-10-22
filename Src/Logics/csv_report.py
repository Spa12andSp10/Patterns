import csv
import io

from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.report_data_extractor import report_data_extractor


class csv_report(abstract_report):
    """Формирует отчет в формате CSV."""

    def build(self, source):
        """Формирует CSV-файл (в виде байтов) из доменной модели.

        :param source: Доменная модель.
        :return: DTO с бинарными данными (UTF-8 BOM) и MIME.
        """
        validator.validate(source, object, "source")

        data = report_data_extractor.extract(source)
        table = [data.header] + data.rows

        buffer = io.StringIO()
        write = csv.writer(buffer, lineterminator='\n')
        write.writerows(table)

        csv_bytes = ("\ufeff" + buffer.getvalue()).encode("utf-8")

        result = report_result_dto()
        result.binary = csv_bytes
        result.mime = report_type_enum.CSV.mime
        return result
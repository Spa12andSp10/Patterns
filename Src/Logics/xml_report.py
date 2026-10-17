import xml.etree.ElementTree as ET
from xml.dom import minidom

from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_data_extractor import report_data_extractor

class xml_report(abstract_report):
    """Формирует отчет в формате XML-документа."""

    def build(self, source):
        """Формирует XML-код из доменной модели.

        :param source: Доменная модель (рецепт, номенклатура, единица измерения).
        :return: DTO с текстом XML.
        """
        validator.validate(source, object, "source")
        
        header, rows = report_data_extractor.extract(source)

        root = ET.Element("report")
        
        header_el = ET.SubElement(root, "header")
        for h in header:
            ET.SubElement(header_el, "column").text = str(h)

        data_el = ET.SubElement(root, "data")
        for row in rows:
            row_el = ET.SubElement(data_el, "row")
            for col_value in row:
                ET.SubElement(row_el, "cell").text = str(col_value)

        rough = ET.tostring(root, encoding="utf-8")
        pretty = minidom.parseString(rough).toprettyxml(indent="  ", encoding="utf-8")

        result = report_result_dto()
        result.text = pretty.decode("utf-8")
        return result
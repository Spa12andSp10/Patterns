from Src.Core.abstract_factory import abstract_factory
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.settings_manager import settings_manager
from Src.Logics.text_report import text_report
from Src.Logics.html_report import html_report
from Src.Logics.xml_report import xml_report
from Src.Logics.csv_report import csv_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.png_report import png_report
from Src.Core.exception import arguments_exeption

class report_factory(abstract_factory):
    """Фабрика для создания отчетов разных форматов."""

    __mapping: dict
    __settings: settings_manager


    def __init__(self, settings: settings_manager = None):
        """Инициализирует фабрику.
        
        :param settings: Менеджер настроек. Если None — берется Singleton.
        """
        self.__mapping = {
            report_type_enum.TXT: text_report,
            report_type_enum.HTML: html_report,
            report_type_enum.XML: xml_report,
            report_type_enum.CSV: csv_report,
            report_type_enum.MARKDOWN: markdown_report,
            report_type_enum.PNG: png_report,
        }
        self.__settings = settings if settings is not None else settings_manager()

    def create(self, report_type: report_type_enum) -> abstract_report:
        """Создает экземпляр отчета по его типу.
        
        :param report_type: Формат отчета (TXT, CSV, HTML и т.д.).
        :raises ValueError: Если тип не зарегистрирован.
        """
        if report_type not in self.__mapping:
            raise ValueError(f"Неизвестный тип отчёта: {report_type!r}")
        return self.__mapping[report_type]()
    
    def create_default(self) -> abstract_report:
        """Создает отчет в формате, указанном в настройках (settings.json).

        Формат читается из settings_model.response_format и переводится
        в report_type_enum через from_slug. Если
        формат в настройках оказался невалидным (например, settings.json
        правили вручную в обход сеттера), бросается понятная ошибка
        вместо «сырого» ValueError.

        :raises arguments_exeption: Если формат в настройках не найден
            в справочнике report_type_enum.
        """
        form = self.__settings.settings.response_format
        try:
            report_type = report_type_enum.from_slug(form)
        except ValueError:
            raise arguments_exeption(
                "create_default", f"Неизвестный формат в настройках: {form!r}"
            )
        return self.create(report_type)
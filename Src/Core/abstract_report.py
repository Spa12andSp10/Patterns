from Src.Dtos.report_result_dto import report_result_dto
from abc import ABC, abstractmethod
from Src.Core.abstract_model import abstract_model

"""
Абстрактный класс для формирования отчета
"""

class abstract_report(ABC):

    """
    Сформировать отчет
    """
    @abstractmethod
    def build(self, source: abstract_model) -> report_result_dto:
        """Формирует отчет на основе переданного источника данных."""
        pass
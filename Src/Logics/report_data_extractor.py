from Src.Models.technicalmap_model import technicalmap_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exeption

class report_data_extractor:
    """Извлекает и формирует табличные данные для отчетов.
    
    Преобразует любую доменную модель (рецепт, номенклатуру, единицу
    измерения) в универсальный набор заголовков и строк, который
    затем используется всеми форматами отчетов (TXT, HTML, CSV и др.).
    """

    @staticmethod
    def _extract_recipe(source: technicalmap_model):
        """Извлекает данные из технологической карты (рецепта).

        :param source: Рецепт.
        :return: Кортеж (список заголовков, список строк данных).
        """
        header = ["Code", "Name", "Brutto", "Netto", "Proteins", "Fats", "Carbohydrates"]
        data = []
        for item in source.ingredients:
            data.append([
                item.unique_code,
                item.name,
                item.calculate_brutto(),
                item.calculate_netto(),
                item.calculate_proteins(),
                item.calculate_fats(),
                item.calculate_carbohydrates(),
            ])
        return header, data

    @staticmethod
    def _extract_nomenclature(source: nomenclature_model):
        """Извлекает данные из номенклатуры.

        :param source: Номенклатура.
        :return: Кортеж (список заголовков, список строк данных).
        """
        header = ["Code", "Name", "Full name", "Group", "Range"]
        group_name = source.group.name if source.group else "Not found"
        range_name = source.range.name if source.range else "Not found"

        data = [[
            source.unique_code,
            source.name,
            source.full_name,
            group_name,
            range_name,
        ]]

        return header, data

    @staticmethod
    def _extract_range(source: range_model):
        """Извлекает данные из единицы измерения.

        :param source: Единица измерения.
        :return: Кортеж (список заголовков, список строк данных).
        """
        header = ["Code", "Name", "Coef", "Base"]

        base_name = source.base.name if source.base else "Not found"

        data = [[
            source.unique_code,
            source.name,
            source.conversion_factor,
            base_name,
        ]]

        return header, data

    @staticmethod
    def extract(source):
        """Универсальная точка входа для извлечения данных.

        :param source: Доменная модель (рецепт, номенклатура, единица измерения).
        :return: Кортеж (список заголовков, список строк данных).
        :raises arguments_exeption: Если передан неподдерживаемый тип.
        """
        if isinstance(source, technicalmap_model):
            return report_data_extractor._extract_recipe(source)
        elif isinstance(source, nomenclature_model):
            return report_data_extractor._extract_nomenclature(source)
        elif isinstance(source, range_model):
            return report_data_extractor._extract_range(source)
        else:
            raise arguments_exeption("extract", "Неверный тип формирования отчета")
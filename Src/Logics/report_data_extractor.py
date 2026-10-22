from Src.Models.technicalmap_model import technicalmap_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Dtos.report_data_dto import report_data_dto
from Src.Core.exception import arguments_exeption


class report_data_extractor:
    """Извлекает и формирует табличные данные для отчетов.

    Преобразует любую доменную модель (рецепт, номенклатуру, единицу
    измерения) в универсальный DTO с заголовками и строками, который
    затем используется всеми форматами отчетов (TXT, HTML, CSV и др.).

    Фабрика [тип сущности, метод] позволяет расширять набор
    поддерживаемых сущностей без правки метода extract.
    """

    @staticmethod
    def _extract_recipe(source: technicalmap_model) -> report_data_dto:
        """Извлекает данные из технологической карты (рецепта).

        :param source: Рецепт.
        :return: DTO с заголовками и строками данных.
        """
        header = ["Code", "Name", "Brutto", "Netto",
                  "Proteins", "Fats", "Carbohydrates"]
        rows = []
        for item in source.ingredients:
            rows.append([
                item.unique_code,
                item.name,
                item.calculate_brutto(),
                item.calculate_netto(),
                item.calculate_proteins(),
                item.calculate_fats(),
                item.calculate_carbohydrates(),
            ])
        return report_data_dto.create(header, rows)

    @staticmethod
    def _extract_nomenclature(source: nomenclature_model) -> report_data_dto:
        """Извлекает данные из номенклатуры.

        :param source: Номенклатура.
        :return: DTO с заголовками и строками данных.
        """
        header = ["Code", "Name", "Full name", "Group", "Range"]
        group_name = source.group.name if source.group else "Not found"
        range_name = source.range.name if source.range else "Not found"

        rows = [[
            source.unique_code,
            source.name,
            source.full_name,
            group_name,
            range_name,
        ]]

        return report_data_dto.create(header, rows)

    @staticmethod
    def _extract_range(source: range_model) -> report_data_dto:
        """Извлекает данные из единицы измерения.

        :param source: Единица измерения.
        :return: DTO с заголовками и строками данных.
        """
        header = ["Code", "Name", "Coef", "Base"]
        base_name = source.base.name if source.base else "Not found"

        rows = [[
            source.unique_code,
            source.name,
            source.conversion_factor,
            base_name,
        ]]

        return report_data_dto.create(header, rows)

    _extractors: dict = {
        technicalmap_model: _extract_recipe.__func__,
        nomenclature_model: _extract_nomenclature.__func__,
        range_model: _extract_range.__func__,
    }

    @classmethod
    def extract(cls, source) -> report_data_dto:
        """Универсальная точка входа для извлечения данных.

        Ищет в фабрике метод по типу сущности и вызывает его.

        :param source: Доменная модель (рецепт, номенклатура, единица измерения).
        :return: DTO с заголовками и строками данных.
        :raises arguments_exeption: Если передан неподдерживаемый тип.
        """
        for entity_type, extractor in cls._extractors.items():
            if isinstance(source, entity_type):
                return extractor(source)

        raise arguments_exeption(
            "extract",
            f"Неверный тип формирования отчета: {type(source).__name__}"
        )
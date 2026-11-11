from Src.Core.exception import arguments_exeption
from Src.Dtos.report_data_dto import report_data_dto
from Src.Models.group_model import group_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.technicalmap_model import technicalmap_model


class report_data_extractor:
    """Преобразует доменную модель в табличные данные (header + rows).

    Поддерживаемые типы: technicalmap_model, ingredient_model,
    nomenclature_model, range_model, group_model, warehouse_model.

    Порядок isinstance-проверок важен:
      - technicalmap_model — до ingredient/nomenclature (у него свои поля);
      - ingredient_model — ДО nomenclature_model (это его наследник);
      - nomenclature_model — до range_model (не пересекаются, но порядок
        фиксированный);
      - group_model и warehouse_model — листья, в конце.
    """

    @staticmethod
    def extract(source) -> report_data_dto:
        """Строит табличные данные по доменной модели.

        :param source: Доменная модель.
        :return: DTO с header и rows.
        :raises arguments_exeption: Если тип не поддерживается.
        """
        if isinstance(source, technicalmap_model):
            return report_data_extractor._from_recipe(source)

        # ingredient_model наследует nomenclature_model — проверяем раньше
        if isinstance(source, ingredient_model):
            return report_data_extractor._from_ingredient(source)

        if isinstance(source, nomenclature_model):
            return report_data_extractor._from_nomenclature(source)

        if isinstance(source, range_model):
            return report_data_extractor._from_range(source)

        if isinstance(source, group_model):
            return report_data_extractor._from_group(source)

        if isinstance(source, warehouse_model):
            return report_data_extractor._from_warehouse(source)

        raise arguments_exeption(
            "extract",
            f"Неверный тип формирования отчета: {type(source).__name__}",
        )


    @staticmethod
    def _from_recipe(source: technicalmap_model) -> report_data_dto:
        """Рецепт: шапка с общими полями + строки ингредиентов.

        Колонки: ingredient, brutto, proteins, fats, carbohydrates,
        coef, method.
        """
        header = [
            "ingredient", "brutto", "proteins", "fats",
            "carbohydrates", "coef", "method",
        ]
        rows = []
        for ing in source.ingredients:
            method = source.preparation_method.get(
                getattr(ing, "full_name", ""), ""
            )
            rows.append([
                getattr(ing, "full_name", ""),
                ing.brutto,
                ing.proteins,
                ing.fats,
                ing.carbohydrates,
                ing.coef,
                method,
            ])
        return report_data_dto.create(header=header, rows=rows)


    @staticmethod
    def _from_ingredient(source: ingredient_model) -> report_data_dto:
        """Ингредиент: одноимённые поля в одной строке."""
        header = [
            "full_name", "brutto", "proteins", "fats",
            "carbohydrates", "coef", "item_type", "unique_code",
        ]
        rows = [[
            source.full_name,
            source.brutto,
            source.proteins,
            source.fats,
            source.carbohydrates,
            source.coef,
            source.item_type,
            source.unique_code,
        ]]
        return report_data_dto.create(header=header, rows=rows)


    @staticmethod
    def _from_nomenclature(source: nomenclature_model) -> report_data_dto:
        """Номенклатура: поля + ссылки group/range (по name)."""
        header = [
            "name", "full_name", "group", "range",
            "item_type", "unique_code",
        ]
        rows = [[
            source.name,
            source.full_name,
            getattr(source.group, "name", "") if source.group else "",
            getattr(source.range, "name", "") if source.range else "",
            source.item_type,
            source.unique_code,
        ]]
        return report_data_dto.create(header=header, rows=rows)


    @staticmethod
    def _from_range(source: range_model) -> report_data_dto:
        """Единица измерения: name, conversion_factor, base, unique_code."""
        header = ["name", "conversion_factor", "base", "unique_code"]
        rows = [[
            source.name,
            source.conversion_factor,
            getattr(source.base, "name", "") if source.base else "",
            source.unique_code,
        ]]
        return report_data_dto.create(header=header, rows=rows)


    @staticmethod
    def _from_group(source: group_model) -> report_data_dto:
        """Группа номенклатуры: name, unique_code."""
        header = ["name", "unique_code"]
        rows = [[source.name, source.unique_code]]
        return report_data_dto.create(header=header, rows=rows)


    @staticmethod
    def _from_warehouse(source: warehouse_model) -> report_data_dto:
        """Склад: name, address, unique_code."""
        header = ["name", "address", "unique_code"]
        rows = [[source.name, source.address, source.unique_code]]
        return report_data_dto.create(header=header, rows=rows)
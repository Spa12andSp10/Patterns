from Src.Core.exception import arguments_exeption
from Src.Dtos.report_data_dto import report_data_dto
from Src.Models.group_model import group_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.technicalmap_model import technicalmap_model
from Src.Models.transaction_model import transaction_model


class report_data_extractor:
    """Преобразует доменные данные в табличные (header + rows).

    Поддерживаемые типы: technicalmap_model, ingredient_model,
    nomenclature_model, range_model, group_model, warehouse_model,
    список транзакций (оборотно-сальдовая ведомость).

    Порядок isinstance-проверок важен:
      - technicalmap_model — до ingredient/nomenclature;
      - ingredient_model — ДО nomenclature_model;
      - nomenclature_model — до range_model;
      - group_model и warehouse_model.
      - список транзакций проверяется до одиночных моделей.
    """

    TRANSACTION_HEADER = [
        "nomenclature",
        "warehouse",
        "range",
        "opening_balance",
        "debit",
        "credit",
        "closing_balance",
    ]

    @staticmethod
    def extract(source) -> report_data_dto:
        """Строит табличные данные по доменной модели.

        :param source: Доменная модель, список транзакций или report_data_dto.
        :return: DTO с header и rows.
        :raises arguments_exeption: Если тип не поддерживается.
        """
        if isinstance(source, report_data_dto):
            return source

        if isinstance(source, (list, tuple)) and (
            not source
            or all(isinstance(item, transaction_model) for item in source)
        ):
            return report_data_extractor._from_transactions(source)

        if isinstance(source, technicalmap_model):
            return report_data_extractor._from_recipe(source)

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

    @staticmethod
    def _from_transactions(source: list) -> report_data_dto:
        """ОСВ: группировка движений по номенклатуре, складу и единице.

        Положительное ``value`` — приход (debit), отрицательное — расход
        (credit). ``opening_balance`` всегда 0, ``closing_balance`` равен
        разности debit и credit. Завершающая строка «ИТОГО» добавляется,
        только если есть движения.

        :param source: Список транзакций (может быть пустым).
        :return: DTO с header и rows.
        """
        groups = {}

        for item in source:
            key = (
                item.nomenclatures.unique_code,
                item.warehouses.unique_code,
                item.ranges.unique_code,
            )
            group = groups.setdefault(key, {
                "nomenclature": item.nomenclatures.name,
                "warehouse": item.warehouses.name,
                "range": item.ranges.name,
                "opening_balance": 0.0,
                "debit": 0.0,
                "credit": 0.0,
            })

            if item.value >= 0:
                group["debit"] += item.value
            else:
                group["credit"] += abs(item.value)

        rows = []
        total_debit = 0.0
        total_credit = 0.0

        for group in groups.values():
            debit = round(group["debit"], 2)
            credit = round(group["credit"], 2)
            closing = round(debit - credit, 2)

            rows.append([
                group["nomenclature"],
                group["warehouse"],
                group["range"],
                group["opening_balance"],
                debit,
                credit,
                closing,
            ])

            total_debit += debit
            total_credit += credit

        if rows:
            total_debit = round(total_debit, 2)
            total_credit = round(total_credit, 2)
            rows.append([
                "ИТОГО", "", "", 0.0,
                total_debit,
                total_credit,
                round(total_debit - total_credit, 2),
            ])

        return report_data_dto.create(
            header=report_data_extractor.TRANSACTION_HEADER,
            rows=rows,
        )
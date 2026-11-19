from Src.Core.abstract_prototype import abstract_prototype
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.report_data_dto import report_data_dto
from Src.Logics.prototype import prototype


class turnover_prototype(abstract_prototype):
    """Прототип для формирования оборотно-сальдовой ведомости (ОСВ).
    """

    HEADER = [
        "nomenclature",
        "warehouse",
        "range",
        "opening_balance",
        "debit",
        "credit",
        "closing_balance",
    ]

    def clone(self, filters: filter_dto = None) -> "turnover_prototype":
        """Создаёт новый прототип с отфильтрованными транзакциями.
        """
        filtered = prototype(self.data).clone(filters).data
        return turnover_prototype(filtered)

    def build(self) -> report_data_dto:
        """Строит ОСВ в формате ``report_data_dto``
        """
        groups = {}

        for item in self.data:
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

        return report_data_dto.create(header=self.HEADER, rows=rows)

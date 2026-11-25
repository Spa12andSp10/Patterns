from datetime import date, datetime, time

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exeption
from Src.Core.validator import validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model


class transaction_model(abstract_model):
    """Модель транзакции: движение номенклатуры по складу.

    Положительное ``value`` — приход, отрицательное — расход.
    """

    __ranges: range_model
    __warehouses: warehouse_model
    __nomenclatures: nomenclature_model
    __value: float
    __period: datetime

    def __init__(self,nomenclatures: nomenclature_model,warehouses: warehouse_model,ranges: range_model,value: float,period: datetime,) -> None:
        """Создаёт транзакцию.
        """
        super().__init__()
        self.nomenclatures = nomenclatures
        self.warehouses = warehouses
        self.ranges = ranges
        self.value = value
        self.period = period

    @classmethod
    def create(cls,nomenclatures: nomenclature_model,warehouses: warehouse_model,ranges: range_model,value: float,period: datetime,) -> "transaction_model":
        """Создаёт транзакцию из набора полей.
        """
        return cls(
            nomenclatures=nomenclatures,
            warehouses=warehouses,
            ranges=ranges,
            value=value,
            period=period,
        )

    @property
    def ranges(self) -> range_model:
        return self.__ranges

    @ranges.setter
    def ranges(self, source: range_model) -> None:
        """Устанавливает единицу измерения.
        """
        validator.validate(source, range_model, "ranges")
        self.__ranges = source

    @property
    def warehouses(self) -> warehouse_model:
        """Возвращает склад."""
        return self.__warehouses

    @warehouses.setter
    def warehouses(self, source: warehouse_model) -> None:
        """Устанавливает склад.
        """
        validator.validate(source, warehouse_model, "warehouses")
        self.__warehouses = source

    @property
    def nomenclatures(self) -> nomenclature_model:
        """Возвращает номенклатуру."""
        return self.__nomenclatures

    @nomenclatures.setter
    def nomenclatures(self, source: nomenclature_model) -> None:
        """Устанавливает номенклатуру.
        """
        validator.validate(source, nomenclature_model, "nomenclatures")
        self.__nomenclatures = source

    @property
    def value(self) -> float:
        """Возвращает количество: больше нуля — приход, меньше — расход."""
        return self.__value

    @value.setter
    def value(self, source: float | int) -> None:
        """Устанавливает количество.
        """
        if isinstance(source, bool) or not isinstance(source, (int, float)):
            raise arguments_exeption("value", "Ожидалось число")
        self.__value = float(source)

    @property
    def period(self) -> datetime:
        """Возвращает дату и время операции."""
        return self.__period

    @period.setter
    def period(self, source: datetime | date | str) -> None:
        """Устанавливает дату и время операции.
        """
        self.__period = self._to_datetime(source)

    @staticmethod
    def _to_datetime(source: datetime | date | str) -> datetime:
        """Приводит дату к ``datetime``.
        """
        if isinstance(source, datetime):
            return source
        if isinstance(source, date):
            return datetime.combine(source, time.min)
        if isinstance(source, str):
            try:
                return datetime.fromisoformat(source.strip())
            except ValueError:
                raise arguments_exeption(
                    "period", "Некорректная дата, ожидался формат ISO"
                )
        raise arguments_exeption(
            "period", "Ожидались datetime, date или ISO-строка"
        )

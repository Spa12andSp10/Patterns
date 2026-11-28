from datetime import date

from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_manager import abstract_manager
from Src.Core.abstract_observation import abstract_observation
from Src.Core.event_type import event_types
from Src.Core.message_type import message_type
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.observer import observer
from Src.Logics.prototype import prototype
from Src.Models.log_message_model import log_message_model

"""Логгер"""

class logger(abstract_manager, abstract_observation):
    LOG_FIELDS = ("period", "system_name", "message_type", "message")

    _logs: list[log_message_model]

    def __new__(cls):
        """Реализует Singleton"""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._logs = []
        self._file_name = "log.txt"
        self._is_loaded = False

    @staticmethod
    def _event_name(event_type: object) -> str:
        """Приводит событие к строковому имени/"""
        res = getattr(event_type, "value", event_type)
        return str(res)

    @staticmethod
    def _message_type(details: dict, params: object) -> object:
        """Определяет тип сообщения."""
        if "message_type" in details:
            return details["message_type"]
        if isinstance(params, BaseException):
            return message_type.ERROR
        return message_type.INFO

    @staticmethod
    def _message(params: object, default: str) -> str:
        """Возвращает текст события."""
        if params is None:
            return default
        return str(params)

    @property
    def logs(self) -> list[log_message_model]:
        """Возвращает копию списка логов. Это защищпет внуьркнней хранилище"""
        return list(self._logs)

    def load(self, file_name: str = "") -> None:
        """Подписывает логгер на observer."""
        self._is_loaded = False
        observer.add(self)
        if file_name:
            self._file_name = file_name
        self._is_loaded = True

    def handler(self, event_type: event_types | str, params: object = None) -> None:
        """Обработчик событий observer. Он создаёт и добавляет запись в журнал."""
        event_name = self._event_name(event_type)
        details = params if isinstance(params, dict) else {}

        self._logs.append(
            log_message_model.create(period=date.today(), system_name=details.get("system_name", event_name), message_type=self._message_type(details, params), message=details.get("message", self._message(params, event_name)))
        )

    def _row(self, item: log_message_model) -> dict:
        converter = convert_factory().create()
        raw = converter.convert(item)
        raw["period"] = self._period_text(item)
        return raw

    def serialize(self) -> list[dict]:
        """Возвращает все логи в виде словарей для API и отчётов."""
        return [self._row(item) for item in self._logs]

    def deserialize(self, raw: dict) -> log_message_model:
        """Собирает модель log_message_model из словаря через общую фабрику."""
        return deserialize_factory().deserialize(raw)

    def to_dicts(self, items=None) -> list[dict]:
        """Возвращает словари для переданных записей или для всего журнала."""
        return [self._row(item)for item in (self._logs if items is None else items)]

    def query(self, filters=None) -> list[dict]:
        """Фильтрует и сортирует логи через прототип. Емли нет фильтров, то возвращает все."""
        if isinstance(filters, dict):
            filters = filter_dto.from_dict(filters)
        rows = self.serialize()
        return prototype(rows).clone(filters).data

    def to_json(self, rows: list[dict]) -> str:
        """Упаковывает строки журнала в JSON с полями count и items."""
        return abstract_convertor.to_json({"count": len(rows),"items": rows})

    def save(self, file_name: str = "") -> bool:
        """Записывает текстовый журнал в файл и возвращает успешность."""
        inner = file_name or self._file_name
        try:
            with open(inner, "w", encoding="utf-8") as file:
                file.write(self.to_text())
        except OSError:
            return False

        self._file_name = inner
        return True

    @staticmethod
    def _period_text(log: log_message_model) -> str:
        """правильное формирование даты"""
        return str(log.period)[:10]

    @classmethod
    def _line(cls, log: log_message_model) -> str:
        """Формирует одну строку текстового журнала."""
        return (f"{cls._period_text(log)} [{log.message_type}] {log.system_name}: {log.message}")
    
    def to_text(self) -> str:
        """Собирает весь журнал в теокст по строкам."""
        return "\n".join(self._line(log) for log in self._logs)
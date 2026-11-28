from Src.Core.abstract_observation import abstract_observation
from Src.Core.validator import validator

"""Наблюдатель"""

class observer():
    handlers: list[abstract_observation] = []

    @staticmethod
    def add(source: abstract_observation) -> None:
        """Добавление  нового наблюдаемого поля"""
        validator.validate(source, abstract_observation)
        for handler in observer.handlers:
            if handler is source:
                return

        observer.handlers.append(source)

    @staticmethod
    def delete(source: abstract_observation) -> None:
        """Удаление наблюдаемого поля"""
        validator.validate(source, abstract_observation)
        for handler in observer.handlers[:]:
            if handler is source:
                observer.handlers.remove(handler)

    @staticmethod
    def create(event_type: str, params: object = None):
        """Создание"""
        for handler in observer.handlers[:]:
            if handler is not None:
                handler.handler(event_type, params)
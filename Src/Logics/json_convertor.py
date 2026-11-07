from datetime import date, datetime, time, timedelta

class json_convertor:

    def __init__(self):
        self.__handlers: list = []

    def register(self, predicate, converter) -> None:

        self.__handlers.append((predicate, converter))
        return self

    def convert(self, value):
        """Приводит значение к JSON-совместимому виду."""
        for predicate, handler in self.__handlers:
            if predicate(value):
                return handler(value, self)
        raise TypeError(
            f"Нет стратегии для типа {type(value).__name__}: {value!r}"
        )
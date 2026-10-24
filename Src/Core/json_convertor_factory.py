from datetime import date, datetime, time, timedelta


class json_convertor_factory:
    """Реестр обработчиков: (проверка типа, функция приведения).

    Обработчики проверяются в порядке регистрации; первый
    подходящий выигрывает. Порядок регистрации = приоритет.
    """

    _handlers: list = []

    @classmethod
    def register(cls, predicate, converter) -> None:
        """Регистрирует обработчик.

        :param predicate: Функция (value) -> bool — подходит ли тип.
        :param converter: Функция (value, recurse) -> JSON-совместимое
            значение. recurse — ссылка на рекурсивный обход,
            чтобы обработчик мог разворачивать вложенные структуры.
        """
        cls._handlers.append((predicate, converter))

    @classmethod
    def clear(cls) -> None:
        """Очищает реестр (для тестов)."""
        cls._handlers.clear()

    @classmethod
    def convert(cls, value, recurse):
        """Приводит значение к JSON-совместимому виду.

        :param value: Исходное значение.
        :param recurse: Функция рекурсивного обхода (для контейнеров).
        :return: JSON-совместимое значение.
        """
        for predicate, converter in cls._handlers:
            if predicate(value):
                return converter(value, recurse)
        return str(value)

    @classmethod
    def create_default(cls) -> None:
        """Регистрирует стандартный набор обработчиков (один раз).

        Порядок регистрации = приоритет:
          1. dict;
          2. list/tuple;
          3. datetime/date/time;
          4. timedelta;
          5. примитивы (str/int/float/bool/None).
        Fallback str(value) — внутри convert().
        """
        if getattr(cls, "_defaults_done", False):
            return
        cls._defaults_done = True

        cls.register(cls._is_dict, cls._convert_dict)
        cls.register(cls._is_sequence, cls._convert_sequence)
        cls.register(cls._is_datetime, cls._convert_datetime)
        cls.register(cls._is_timedelta, cls._convert_timedelta)
        cls.register(cls._is_primitive, cls._convert_primitive)

    @staticmethod
    def _is_dict(value) -> bool:
        return isinstance(value, dict)

    @staticmethod
    def _convert_dict(value, recurse):
        return {k: recurse(v) for k, v in value.items()}

    @staticmethod
    def _is_sequence(value) -> bool:
        return isinstance(value, (list, tuple))

    @staticmethod
    def _convert_sequence(value, recurse):
        return [recurse(v) for v in value]

    @staticmethod
    def _is_datetime(value) -> bool:
        return isinstance(value, (datetime, date, time))

    @staticmethod
    def _convert_datetime(value, recurse):
        return value.isoformat()

    @staticmethod
    def _is_timedelta(value) -> bool:
        return isinstance(value, timedelta)

    @staticmethod
    def _convert_timedelta(value, recurse):
        return value.total_seconds()

    @staticmethod
    def _is_primitive(value) -> bool:
        return isinstance(value, (str, int, float, bool)) or value is None

    @staticmethod
    def _convert_primitive(value, recurse):
        return value
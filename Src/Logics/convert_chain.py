class convert_chain:
    """Цепочка отвественностей"""

    def __init__(self):
        self._handlers: list = []

    def register(self, predicate, handler) -> "convert_chain":
        """Регистрирует стратегию. Возвращает self для цепочки."""
        self._handlers.append((predicate, handler))
        return self

    def clear(self) -> None:
        """Очищает реестр"""
        self._handlers.clear()

    def convert(self, source, walker, visited: set = None):
        """Разбирает значение по первой подходящей стратегии.

        :param source: Исходное значение.
        :param walker: Обходчик моделей (нужен стратегиям для рекурсии).
        :param visited: Множество unique_code посещённых моделей.
        :return: Разобранное значение.
        """
        if visited is None:
            visited = set()
        for predicate, handler in self._handlers:
            if predicate(source):
                return handler(source, walker, visited)

        return {"value": source}


class field_path:
    """Разрешает путь к полю доменной модели.

    """

    MAX_DEPTH: int = 32

    @classmethod
    def resolve(cls, source, path: str) -> list:
        """Возвращает все значения, найденные по указанному пути.

        """
        if source is None or not isinstance(path, str):
            return []

        normalized = path.strip()
        if not normalized:
            return []

        parts = [part for part in normalized.split(".") if part]
        return cls._walk(source, parts, 0)

    @classmethod
    def _walk(cls, source, parts: list, depth: int) -> list:
        """Рекурсивно проходит по частям пути.

        """
        if source is None or depth > cls.MAX_DEPTH:
            return []

        if isinstance(source, (list, tuple)):
            result = []
            for item in source:
                result.extend(cls._walk(item, parts, depth + 1))
            return result

        if not parts:
            return [source]

        head = parts[0]
        rest = parts[1:]

        if head.endswith("[]"):
            head = head[:-2]

        if not head or head.startswith("_"):
            return []

        if isinstance(source, dict):
            if head not in source:
                return []
            value = source[head]
        else:
            try:
                value = getattr(source, head)
            except AttributeError:
                return []

        return cls._walk(value, rest, depth + 1)

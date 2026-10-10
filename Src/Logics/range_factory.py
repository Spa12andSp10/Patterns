from Src.Models.range_model import range_model


class range_factory:
    """Фабрика единиц измерения."""

    @staticmethod
    def create_gram() -> range_model:
        return range_model(name="Gram", conversion_factor=1, base=None)

    @staticmethod
    def create_milliliter() -> range_model:
        return range_model(name="Milliliter", conversion_factor=1, base=None)

    @staticmethod
    def create_kilogram(base: range_model = None) -> range_model:
        if base is None:
            base = range_factory.create_gram()
        return range_model(name="Kilogram", conversion_factor=1000, base=base)

    @staticmethod
    def create_tonna(base: range_model = None) -> range_model:
        if base is None:
            base = range_factory.create_kilogram()
        return range_model(name="Tonna", conversion_factor=1000, base=base)

    @staticmethod
    def create_liter(base: range_model = None) -> range_model:
        if base is None:
            base = range_factory.create_milliliter()
        return range_model(name="Liter", conversion_factor=1000, base=base)
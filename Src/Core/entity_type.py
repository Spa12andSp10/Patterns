from enum import Enum


class entity_type(str, Enum):
    """Типы доменных сущностей, поддерживаемых десериализацией"""
    GROUP = "group"
    RANGE = "range"
    NOMENCLATURE = "nomenclature"
    INGREDIENT = "ingredient"
    RECIPE = "recipe"
    WAREHOUSE = "warehouse"
    ORGANIZATION = "organization"
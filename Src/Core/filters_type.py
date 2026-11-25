from enum import Enum


class filters_type(str, Enum):
    EQUALS = "equals"
    LIKE = "like"
    BETWEEN = "between"
    ALPHABET = "alphabet"
    ALPHABET_DESC = "alphabet_desc"

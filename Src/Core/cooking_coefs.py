# Справочник коэффициентов изменения БЖУ при тепловой обработке.
# Ключ — ключевое слово способа приготовления (в нижнем регистре).
# Значение — словарь с коэффициентами для каждого нутриента:
#   proteins/fats/carbohydrates.
# 1.0 — без изменений; <1 — потери; >1 — прирост (поглощение масла).
COOKING_COEFS: dict[str, dict[str, float]] = {
    "boil":         {"proteins": 0.95, "fats": 0.90, "carbohydrates": 0.95},
    "boiling":      {"proteins": 0.95, "fats": 0.90, "carbohydrates": 0.95},
    "cook":         {"proteins": 0.95, "fats": 0.90, "carbohydrates": 0.95},
    "fry":          {"proteins": 0.95, "fats": 1.30, "carbohydrates": 0.95},
    "frying":       {"proteins": 0.95, "fats": 1.30, "carbohydrates": 0.95},
    "roast":        {"proteins": 0.95, "fats": 1.30, "carbohydrates": 0.95},
    "bake":         {"proteins": 0.95, "fats": 0.85, "carbohydrates": 0.95},
    "baking":       {"proteins": 0.95, "fats": 0.85, "carbohydrates": 0.95},
    "stew":         {"proteins": 0.95, "fats": 0.95, "carbohydrates": 0.90},
    "stewing":      {"proteins": 0.95, "fats": 0.95, "carbohydrates": 0.90},
    "steam":        {"proteins": 0.98, "fats": 0.98, "carbohydrates": 0.98},
    "steaming":     {"proteins": 0.98, "fats": 0.98, "carbohydrates": 0.98},
    "blanch":       {"proteins": 0.95, "fats": 0.95, "carbohydrates": 0.90},
    "blanching":    {"proteins": 0.95, "fats": 0.95, "carbohydrates": 0.90},
}

# Коэффициенты по умолчанию, если способ приготовления не распознан
# или не задан. Означают отсутствие изменений БЖУ при обработке.
DEFAULT_COOKING_COEF: dict[str, float] = {
    "proteins": 1.0,
    "fats": 1.0,
    "carbohydrates": 1.0,
}


def resolve_cooking_coef(method: str) -> dict[str, float]:
    """Определяет коэффициент изменения БЖУ по способу приготовления.

    Ищет в переданном способе ключевое слово из справочника
    COOKING_COEFS (без учёта регистра). Если способ не распознан
    или не передан — возвращает коэффициенты по умолчанию.

    :param method: Способ приготовления (например, "boil").
    :return: Словарь с ключами proteins/fats/carbohydrates,
             где значение — коэффициент изменения нутриента.
    """
    if not method:
        return dict(DEFAULT_COOKING_COEF)

    lowered = method.lower()
    for keyword, coef in COOKING_COEFS.items():
        if keyword in lowered:
            return dict(coef)

    return dict(DEFAULT_COOKING_COEF)
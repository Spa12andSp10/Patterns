import json

from Src.Core.exception import arguments_exeption
from Src.Core.validator import validator
from Src.Models.settings_model import settings_model
from Src.Logics.organization_from_json import organization_from_json

"""Функции для десериализации данных из settings"""

def load_settings(path: str) -> settings_model:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    return settings_from_json(data)


def settings_from_json(source: dict) -> settings_model:
    validator.validate(source, dict, "source")

    org_data = source.get("organization")
    if org_data is None:
        raise arguments_exeption("organization", "Отсутствует organization")

    model = settings_model()

    model.organization = organization_from_json().convert(org_data)

    boss_name = source.get("boss_name")
    if boss_name is None:
        raise arguments_exeption("boss_name", "Отсутствует boss_name")
    model.boss_name = boss_name

    account_name = source.get("account_name")
    if account_name is None:
        raise arguments_exeption("account_name", "Отсутствует account_name")
    model.account_name = account_name

    flag = source.get("first_launch_flag")
    if flag is None:
        raise arguments_exeption("first_launch_flag","Отсутствует first_launch_flag")
    model.first_launch_flag = flag

    fmt = source.get("response_format")
    if fmt is None:
        raise arguments_exeption("response_format","Отсутствует response_format")
    model.response_format = fmt

    unique_code = source.get("unique_code")
    if unique_code is not None:
        model.unique_code = unique_code

    return model
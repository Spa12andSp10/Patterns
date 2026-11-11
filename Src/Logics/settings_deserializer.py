import json
from Src.Core.exception import arguments_exeption
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model


class settings_deserializer:
    """JSON (после walker) -> settings_model."""

    @staticmethod
    def from_dict(data: dict) -> settings_model:
        if not isinstance(data, dict):
            raise arguments_exeption("settings", "Должен быть словарём")

        model = settings_model()

        org_data = data.get("organization")
        if org_data is not None:
            model.organization = settings_deserializer._organization(org_data)

        model.boss_name = data.get("boss_name", "")
        model.account_name = data.get("account_name", "")
        model.first_launch_flag = data.get("first_launch_flag", True)
        model.response_format = data.get("response_format", "TXT")
        if data.get("unique_code"):
            model.unique_code = data["unique_code"]
        return model

    @staticmethod
    def _organization(source: dict) -> organization_model:
        if not isinstance(source, dict):
            raise arguments_exeption("organization", "Должен быть словарём")

        for key in ("name", "inn", "bic", "account", "owner"):
            if key not in source:
                raise arguments_exeption(
                    "organization", f"Отсутствует поле {key!r}"
                )

        model = organization_model.create(
            name=source["name"],
            inn=source["inn"],
            bic=source["bic"],
            account=source["account"],
            owner=source["owner"],
        )
        code = source.get("unique_code")
        if code:
            model.unique_code = code
        return model

    @staticmethod
    def load(file_name: str) -> settings_model | None:
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                return settings_deserializer.from_dict(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            return None
import json
from Src.Core.validator import validator

class json_loaded():

    @staticmethod
    def load_json(value: str) -> dict:
        validator.validate(value, str)
        validator.file_not_exist(value)
        validator.empty_file(value)
        with open(value, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
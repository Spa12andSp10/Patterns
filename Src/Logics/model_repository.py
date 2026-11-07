from typing import Optional
from Src.Core.abstract_model import abstract_model
from Src.Core.validator import validator

class model_repository:

    def __init__(self):
        self.__cloud: dict[str, abstract_model] = {}

    @property
    def cloud(self) -> dict[str, abstract_model]:
        return dict(self.__cloud)

    def get(self, unique_code: str) -> Optional[abstract_model]:
        return self.__cloud.get(unique_code)

    def check_unique_code(self, unique_code: str) -> bool:
        if unique_code in self.__cloud:
            return True
        else:
            return False

    def put_in_cloud(self, value: abstract_model) -> abstract_model:

        validator.validate(value, abstract_model)

        code = value.unique_code
        exist = self.__cloud.get(code)
        if exist is not None:
            return exist

        self.__cloud[code] = value
        return value

    def clear(self):
        self.__cloud.clear()

    def __len__(self) -> int:
        return len(self.__cloud)

    def __contains__(self, unique_code: str) -> bool:
        return unique_code in self.__cloud
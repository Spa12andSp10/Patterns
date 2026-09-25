from Src.Core.abstract_model import abstact_model
from Src.Core.exception import arguments_exeption, max_length_exeption


"""
Общий класс для наследования. Содержит стандартное определение: код, наименование
"""
class entity_model(abstact_model):
    __name:str = ""

    """
    Наименование
    """
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        if value is None or not isinstance(value, str) or value.strip() == "":
            raise arguments_exeption("name", "Некорректно переданный аргумент")
        if len(value.strip()) > self.__max_length:
            raise max_length_exeption("name", self.__max_length)
        self.__name = value.strip()

  
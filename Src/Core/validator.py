from Src.Core.exception import (
    arguments_exeption,
    max_length_exeption,
    length_exeption,
    validation_exeption,
)


class validator:
    """Набор статических методов для валидации значений полей.

    Используется сеттерами доменных моделей и менеджеров для проверки
    входных данных: типа, длины, числовых значений, ИНН, расчётного счёта.
    """

    @staticmethod
    def validate(value, type_, field="field", leng=None, max_len=None, document=None):
        """Проверяет значение на пустоту, тип, длину и максимальную длину.

        :param value: Проверяемое значение.
        :param type_: Ожидаемый тип значения.
        :param field: Имя поля для сообщения об ошибке.
        :param leng: Ожидаемая точная длина (если задана).
        :param max_len: Максимально допустимая длина (если задана).
        :param document: Название документа/поля для сообщения об ошибке.
        :raises arguments_exeption: Если значение None или пустая строка.
        :raises arguments_exeption: Если тип значения не совпадает с type_.
        :raises length_exeption: Если длина не совпадает с leng.
        :raises max_length_exeption: Если длина превышает max_len.
        """
        if value is None:
            raise arguments_exeption(field, "Пустой аргумент")

        if isinstance(value, str) and value.strip() == "":
            raise arguments_exeption(field, "Пустой аргумент")

        if value == "":
            raise arguments_exeption(field, "Пустой аргумент")

        if not isinstance(value, type_):
            raise arguments_exeption(field, "Некорректно переданный аргумент")

        if leng is not None and len(str(value).strip()) != leng:
            raise length_exeption(field, leng, document)

        if max_len is not None and len(str(value).strip()) > max_len:
            raise max_length_exeption(field, max_len)

    @staticmethod
    def digit_validate(value, field="field"):
        """Проверяет, что строка состоит только из цифр.

        :param value: Проверяемая строка.
        :param field: Имя поля для сообщения об ошибке.
        :raises validation_exeption: Если строка содержит не только цифры.
        """
        if value.isdigit() is False:
            raise validation_exeption(field, "Аргумент содержит числовые значения")

    @staticmethod
    def check_inn(value):
        """Проверяет контрольную сумму ИНН.

        :param value: Строка ИНН длиной 10 символов.
        :raises validation_exeption: Если контрольная сумма некорректна.
        """
        total = (2 * int(value[0]) + 4 * int(value[1]) + 10 * int(value[2]) +
                 3 * int(value[3]) + 5 * int(value[4]) + 9 * int(value[5]) +
                 4 * int(value[6]) + 6 * int(value[7]) + 8 * int(value[8]))
        result = total % 11
        if result > 9:
            result %= 10
        if result != int(value[-1]):
            raise validation_exeption("inn", "Некорректный ИНН!")

    @staticmethod
    def check_account(value, bic):
        """Проверяет контрольную сумму расчётного счёта.

        Использует последние три цифры БИК текущей организации.

        :param value: Строка расчётного счёта длиной 20 символов.
        :param bic: БИК банка (последние три цифры используются в проверке).
        :raises validation_exeption: Если контрольная сумма некорректна.
        """
        last = bic[-3:]
        new_value = last + value
        cnt = 1
        total = 0
        for i in range(23):
            match cnt:
                case 1:
                    total += 7 * int(new_value[i])
                    cnt += 1
                case 2:
                    total += 1 * int(new_value[i])
                    cnt += 1
                case 3:
                    total += 3 * int(new_value[i])
                    cnt = 1
        if total % 10 != 0:
            raise validation_exeption("account", "Некорректный Счет!")

    @staticmethod
    def no_lower_that_zero_validate(value, field="field"):
        """Проверяет, что значение строго больше нуля.

        :param value: Проверяемое числовое значение.
        :param field: Имя поля для сообщения об ошибке.
        :raises arguments_exeption: Если значение меньше или равно нулю.
        """
        if value <= 0:
            raise arguments_exeption(field, "Аргумент должен быть больше нуля")
    
    @staticmethod
    def require_keys(data, keys, field="data"):
        """Проверяет наличие обязательных ключей в словаре.

        :param data: Проверяемый словарь.
        :param keys: Итерируемая коллекция обязательных ключей.
        :param field: Имя поля/документа для сообщения об ошибке.
        :raises arguments_exeption: Если data не словарь.
        :raises arguments_exeption: Если отсутствует хотя бы один ключ.
        """
        if not isinstance(data, dict):
            raise arguments_exeption(field, "Должен быть словарём")

        for key in keys:
            if key not in data:
                raise arguments_exeption(
                    f"{field}.{key}",
                    f"Отсутствует обязательный ключ '{key}' в {field}"
                )

    @staticmethod
    def require_dict(data, field="data"):
        """Проверяет, что значение является словарём.

        :param data: Проверяемое значение.
        :param field: Имя поля для сообщения об ошибке.
        :raises arguments_exeption: Если значение не словарь.
        """
        if not isinstance(data, dict):
            raise arguments_exeption(field, "Должен быть объектом (словарём)")
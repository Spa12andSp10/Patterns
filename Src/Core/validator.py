from Src.Core.exception import (
    arguments_exeption,
    max_length_exeption,
    length_exeption,
    validation_exeption,
)


class validator:

    @staticmethod
    def validate(value, type_, field="field", leng=None, max_len=None, document=None):
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
        if value.isdigit() is False:
            raise validation_exeption(field, "Аргумент содержит числовые значения")

    @staticmethod
    def check_inn(value):
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
        if value <= 0:
            raise arguments_exeption(field, "Аргумент должен быть больше нуля")
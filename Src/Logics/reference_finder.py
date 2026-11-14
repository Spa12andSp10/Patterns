from itertools import chain
from typing import Callable, Iterable

from Src.Core.abstract_model import abstract_model


def _container_items(value):
    """Возвращает пары (ключ, элемент) для контейнера.

    :param value: Значение поля.
    :return: items() для словаря, enumerate() для списка/кортежа, иначе ().
    """
    if isinstance(value, dict):
        return value.items()
    if isinstance(value, (list, tuple)):
        return enumerate(value)
    return ()


def _references_in(value):
    """Отдаёт ссылки из значения поля.

    :param value: Значение поля.
    :return: Итератор пар (ключ, вложенная модель).
    """
    if isinstance(value, abstract_model):
        yield None, value
        return

    for key, item in _container_items(value):
        if isinstance(item, abstract_model):
            yield key, item


def _segment(field_name: str, key):
    """Строит сегмент пути для поля.

    :param field_name: Имя поля.
    :param key: None для одиночной ссылки, иначе индекс/ключ контейнера.
    :return: Сегмент пути.
    """
    return field_name if key is None else f"{field_name}[{key!r}]"


def _field_children(model: abstract_model, spec):
    """Отдаёт ссылки одного поля модели.

    :param model: Модель-владелец поля.
    :param spec: Описание поля.
    :return: Итератор пар (вложенная модель, сегмент пути).
    """
    value = getattr(model, spec.name, None)

    for key, child in _references_in(value):
        yield child, _segment(spec.name, key)


class reference_finder:
    """Ищет ссылки на доменную модель в наборе сущностей.

    Класс отвечает только за поиск ссылок. Источник сущностей
    передаётся снаружи, поэтому класс не зависит от storage_manager
    и легко тестируется.
    """

    def __init__(self, entities: Callable[[], Iterable]) -> None:
        """Сохраняет источник сущностей.

        :param entities: Callable без аргументов, возвращающий итерируемое
            доменных моделей.
        """
        self._entities = entities

    def find(self, target: abstract_model):
        """Ищет первую ссылку на target.

        :param target: Доменная модель, на которую ищем ссылки.
        :return: (владелец, путь_до_поля) или None.
        """
        target_code = target.unique_code

        for owner in self._entities():
            if owner.unique_code == target_code:
                continue

            path = self._path_to(owner, target_code)
            if path is not None:
                return owner, path

        return None

    def _path_to(self, owner: abstract_model, target_code: str):
        """Обходит граф ссылок от owner и возвращает путь до target_code.

        :param owner: Сущность, с которой начинается обход.
        :param target_code: unique_code искомой сущности.
        :return: Путь до ссылки или None.
        """
        visited = {owner.unique_code}
        stack = [(owner, "")]

        while stack:
            model, prefix = stack.pop()

            for child, segment in self._children(model):
                path = f"{prefix}.{segment}" if prefix else segment

                if child.unique_code == target_code:
                    return path

                if child.unique_code not in visited:
                    visited.add(child.unique_code)
                    stack.append((child, path))

        return None

    @staticmethod
    def _children(model: abstract_model):
        """Отдаёт ссылочные поля модели без вложенных циклов.

        :param model: Модель, поля которой просматриваются.
        :return: Итератор пар (вложенная модель, сегмент пути).
        """
        return chain.from_iterable(
            _field_children(model, spec)
            for spec in model._specs()
        )

import pytest

from Src.Core.abstract_observation import abstract_observation
from Src.Core.event_type import event_types
from Src.Core.exception import arguments_exeption
from Src.Logics.observer import observer


class handler_stub(abstract_observation):
    def __init__(self):
        self.events = []

    def handler(self, event_type, params=None):
        self.events.append((event_type, params))


@pytest.fixture(autouse=True)
def clean_observer():
    observer.handlers.clear()
    yield
    observer.handlers.clear()


def test_add_registers_handler_once():
    # Подготовка
    stub = handler_stub()

    # Действие
    observer.add(stub)
    observer.add(stub)

    # Проверки
    assert observer.handlers == [stub]
    assert len(observer.handlers) == 1


def test_add_preserves_registration_order():
    # Подготовка
    first = handler_stub()
    second = handler_stub()
    third = handler_stub()

    # Действие
    observer.add(first)
    observer.add(second)
    observer.add(third)

    # Проверки
    assert observer.handlers == [first, second, third]


def test_create_passes_event_and_params_to_handlers():
    # Подготовка
    first = handler_stub()
    second = handler_stub()
    observer.add(first)
    observer.add(second)
    params = {"message": "Событие"}

    # Действие
    observer.create(event_types.LOAD_SETTINGS, params)

    # Проверки
    assert first.events == [(event_types.LOAD_SETTINGS, params)]
    assert second.events == [(event_types.LOAD_SETTINGS, params)]


def test_create_without_params_passes_none():
    # Подготовка
    stub = handler_stub()
    observer.add(stub)

    # Действие
    observer.create(event_types.WEB_REQUEST)

    # Проверки
    assert stub.events == [(event_types.WEB_REQUEST, None)]


def test_delete_removes_only_target_handler():
    # Подготовка
    first = handler_stub()
    second = handler_stub()
    observer.add(first)
    observer.add(second)

    # Действие
    observer.delete(first)
    observer.create(event_types.CHANGE_STORAGE)

    # Проверки
    assert first.events == []
    assert second.events == [(event_types.CHANGE_STORAGE, None)]


def test_delete_unknown_handler_keeps_registered_handlers():
    # Подготовка
    registered = handler_stub()
    unknown = handler_stub()
    observer.add(registered)

    # Действие
    observer.delete(unknown)
    observer.create(event_types.CHANGE_STORAGE)

    # Проверки
    assert registered.events == [(event_types.CHANGE_STORAGE, None)]
    assert unknown.events == []


def test_add_rejects_not_observation():
    # Подготовка
    source = object()

    # Действие
    with pytest.raises(arguments_exeption):
        observer.add(source)

    # Проверки
    assert observer.handlers == []


def test_create_skips_none_handler():
    # Подготовка
    stub = handler_stub()
    observer.handlers[:] = [None, stub]

    # Действие
    observer.create(event_types.LOAD_STORAGE)

    # Проверки
    assert stub.events == [(event_types.LOAD_STORAGE, None)]


def test_handlers_shared_between_instances():
    # Подготовка
    first = observer()
    second = observer()
    stub = handler_stub()

    # Действие
    first.add(stub)

    # Проверки
    assert stub in second.handlers
    assert second.handlers == first.handlers

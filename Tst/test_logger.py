import json
import re
from datetime import date

import pytest

from Src.Core.event_type import event_types
from Src.Core.message_type import message_type
from Src.Logics.logger import logger
from Src.Logics.observer import observer
from Src.Models.log_message_model import log_message_model


@pytest.fixture
def clean_logger():
    observer.handlers.clear()
    if hasattr(logger, "instance"):
        delattr(logger, "instance")
    yield logger()
    observer.handlers.clear()
    if hasattr(logger, "instance"):
        delattr(logger, "instance")


def test_singleton_returns_same_instance(clean_logger):
    # Подготовка
    instance = clean_logger

    # Действие
    second = logger()

    # Проверки
    assert second is instance


def test_repeated_init_keeps_logs(clean_logger):
    # Подготовка
    instance = clean_logger
    instance.handler(event_types.CHANGE_STORAGE)

    # Действие
    instance.__init__()

    # Проверки
    assert len(instance.logs) == 1


def test_load_registers_once_and_sets_file_name(clean_logger):
    # Подготовка
    instance = clean_logger

    # Действие
    instance.load("custom.txt")
    instance.load("custom.txt")

    # Проверки
    assert observer.handlers.count(instance) == 1
    assert instance._file_name == "custom.txt"
    assert instance._is_loaded is True


def test_handler_uses_event_details(clean_logger):
    # Подготовка
    instance = clean_logger
    details = {"message": "Настройки загружены", "system_name": "settings", "message_type": message_type.INFO}

    # Действие
    instance.handler(event_types.LOAD_SETTINGS, details)

    # Проверки
    row = instance.serialize()[0]
    assert row["system_name"] == "settings"
    assert row["message_type"] == "INFO"
    assert row["message"] == "Настройки загружены"


def test_handler_uses_exception_for_error_type(clean_logger):
    # Подготовка
    instance = clean_logger

    # Действие
    instance.handler(event_types.WEB_REQUEST, ValueError("boom"))

    # Проверки
    row = instance.serialize()[0]
    assert row["message_type"] == "ERROR"
    assert row["message"] == "boom"
    assert row["system_name"] == "web_request"


def test_handler_defaults_for_plain_event(clean_logger):
    # Подготовка
    instance = clean_logger

    # Действие
    instance.handler(event_types.CHANGE_STORAGE)

    # Проверки
    row = instance.serialize()[0]
    assert row["message"] == "change_storage"
    assert row["system_name"] == "change_storage"
    assert row["message_type"] == "INFO"


def test_serialize_to_dicts_and_to_text_use_date_only(clean_logger):
    # Подготовка
    instance = clean_logger
    instance.handler(event_types.LOAD_STORAGE, {"message": "Хранилище загружено"})

    # Действие
    rows = instance.serialize()
    dicts = instance.to_dicts()
    text = instance.to_text()

    # Проверки
    assert rows == dicts
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", rows[0]["period"])
    assert text.splitlines()[0].startswith(rows[0]["period"])


def test_query_filters_and_sorts(clean_logger):
    # Подготовка
    instance = clean_logger
    instance.handler("x", {"message": "target a", "message_type": "INFO", "system_name": "s"})
    instance.handler("x", {"message": "target c", "message_type": "ERROR", "system_name": "s"})
    instance.handler("x", {"message": "target b", "message_type": "INFO", "system_name": "s"})
    filters = {"filters": [{"filter_name": "message", "filter_value": "target", "filter_type": "like"},{"filter_name": "message_type", "filter_type": "alphabet_desc"},]}

    # Действие
    result = instance.query(filters)

    # Проверки
    assert [row["message"] for row in result] == ["target a", "target b", "target c"]


def test_to_json_contains_count_and_items(clean_logger):
    # Подготовка
    instance = clean_logger
    instance.handler(event_types.LOAD_STORAGE, {"message": "Хранилище загружено"})

    # Действие
    payload = json.loads(instance.to_json(instance.query()))

    # Проверки
    assert payload["count"] == 1
    assert payload["items"][0]["message"] == "Хранилище загружено"


def test_deserialize_builds_log_model(clean_logger):
    # Подготовка
    raw = {"period": "2026-11-28", "system_name": "crud", "message_type": "INFO", "message": "Создан объект"}

    # Действие
    model = clean_logger.deserialize(raw)

    # Проверки
    assert isinstance(model, log_message_model)
    assert model.period == date(2026, 11, 28)
    assert model.system_name == raw["system_name"]
    assert model.message == raw["message"]

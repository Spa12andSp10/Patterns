import pytest

from pathlib import Path
from Src.Logics.settings_manager import settings_manager
from Src.Core.exception import arguments_exeption


def _settings_path() -> str:
    """Путь к settings.json в папке Tst (рядом с тестом)."""
    return str(Path(__file__).resolve().parent / "settings.json")


def test_valid_result_settings_manager_singleton():
    """
    Проверяет работу шаблона Singleton.
    Ожидаемый результат: два вызова settings_manager() возвращают один и тот же объект.
    """
    # Подготовка
    instance1 = settings_manager()

    # Действие
    instance2 = settings_manager()

    # Проверки
    assert instance1 is instance2


def test_valid_result_settings_manager_same_settings():
    """
    Проверяет, что все экземпляры Singleton ссылаются на один и тот же settings_model.
    Ожидаемый результат: instance1.settings и instance2.settings — один объект.
    """
    # Подготовка
    instance1 = settings_manager()
    instance2 = settings_manager()

    # Действие
    settings1 = instance1.settings
    settings2 = instance2.settings

    # Проверки
    assert settings1 is settings2


def test_valid_result_settings_manager_load_success():
    """
    Проверяет успешную загрузку настроек из JSON.
    Ожидаемый результат: после load() settings не равен None.
    """
    # Подготовка
    manager = settings_manager()

    # Действие
    manager.load(_settings_path())

    # Проверки
    assert manager.settings is not None


def test_valid_result_settings_manager_is_loaded_true():
    """
    Проверяет флаг is_loaded после загрузки настроек.
    Ожидаемый результат: is_loaded становится True, settings не равен None.
    """
    # Подготовка
    manager = settings_manager()

    # Действие
    manager.load(_settings_path())

    # Проверки
    assert manager.is_loaded is True
    assert manager.settings is not None


def test_valid_result_settings_manager_organization_filled():
    """
    Проверяет, что после загрузки заполнена карточка организации.
    Ожидаемый результат: organization не равен None, реквизиты соответствуют JSON.
    """
    # Подготовка
    manager = settings_manager()
    manager.load(_settings_path())

    # Действие
    org = manager.settings.organization

    # Проверки
    assert org is not None
    assert org.name == "Romashka LLC"
    assert org.inn == "7707083893"
    assert org.bic == "044525225"


def test_valid_result_settings_manager_boss_and_account_name():
    """
    Проверяет, что после загрузки заполнены ФИО руководителя и главного бухгалтера.
    Ожидаемый результат: boss_name и account_name соответствуют данным из JSON.
    """
    # Подготовка
    manager = settings_manager()
    manager.load(_settings_path())

    # Действие
    boss_name = manager.settings.boss_name
    account_name = manager.settings.account_name

    # Проверки
    assert boss_name == "Ivanov I. I."
    assert account_name == "Semyonov. A. G."


def test_valid_result_settings_manager_settings_not_empty():
    """
    Проверяет, что после загрузки доступна заполненная модель настроек.
    Ожидаемый результат: is_loaded=True, organization заполнена,
    first_launch_flag имеет bool-значение.
    """
    # Подготовка
    manager = settings_manager()
    manager.load(_settings_path())

    # Действие
    settings = manager.settings

    # Проверки
    assert manager.is_loaded is True
    assert settings.organization is not None
    assert isinstance(settings.first_launch_flag, bool)
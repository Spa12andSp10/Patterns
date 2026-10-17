from Src.Logics.text_report import text_report
from Src.Models.technicalmap_model import technicalmap_model
from Src.Core.abstract_factory import abstract_factory
from Src.Core.abstract_report import abstract_report
from Src.Logics.storage_manager import storage_manager
from Src.Logics.settings_manager import settings_manager
from Src.Logics.report_factory import report_factory
from Src.Dtos.report_type_enum import report_type_enum
from pathlib import Path
import pytest

def _storage_path() -> str:
    """Путь к storage_data.json (эталонные данные)."""
    return str(Path(__file__).resolve().parent / "storage_data.json")

def test_valid_result_name():
    tr = text_report()
    sm = storage_manager()
    sm.load(_storage_path())

    assert len(sm.recipes) > 0, "storage_data.json не содержит рецептов"

    result = tr.build(sm.recipes[0])
    assert result.text != ""

def test_valid_result_name2():
    rf = report_factory()
    result = rf.create(report_type_enum.TXT)
    assert isinstance(result, text_report)

@pytest.mark.xfail(reason="CSV ещё не поддержан")
def test_invalid_result_name3():
    rf = report_factory()
    rf.create(report_type_enum.CSV)

def test_valud_result_name4():
    rf = report_factory()
    result = rf.create(report_type_enum.TXT)
    assert result

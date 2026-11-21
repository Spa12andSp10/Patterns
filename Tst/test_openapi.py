import asyncio
from pathlib import Path

import connexion
import httpx
import yaml

import main as main_module


def _spec_path() -> Path:
    """Путь к OpenAPI-спецификации в корне проекта."""
    return Path(__file__).resolve().parent.parent / "openapi.yaml"


def _spec() -> dict:
    """Загружает OpenAPI-спецификацию из корня проекта."""
    with open(_spec_path(), encoding="utf-8") as file:
        return yaml.safe_load(file)


def test_openapi_is_valid_yaml():
    """openapi.yaml читается как корректный YAML."""

    # Подготовка
    # Действие
    spec = _spec()

    # Проверки
    assert isinstance(spec.get("paths"), dict)
    assert isinstance(spec.get("components"), dict)


def test_openapi_contains_osv_endpoint():
    """Операция POST /api/osv присутствует в спецификации."""

    # Подготовка
    # Действие
    paths = _spec()["paths"]

    # Проверки
    assert "/api/osv" in paths
    assert paths["/api/osv"]["post"]["operationId"] == "main.osv_report"


def test_openapi_contains_filter_endpoint():
    """Операция POST /api/filter/{entity_type}."""

    # Подготовка
    # Действие
    paths = _spec()["paths"]

    # Проверки
    assert "/api/filter/{entity_type}" in paths
    assert (
        paths["/api/filter/{entity_type}"]["post"]["operationId"]
        == "main.filter_entities"
    )


def test_openapi_operation_ids_exist_in_main():
    """Все operationId ссылаются на существующие функции main."""

    # Подготовка
    # Действие
    paths = _spec()["paths"]

    # Проверки
    for path, item in paths.items():
        for method, operation in item.items():
            if not isinstance(operation, dict):
                continue
            operation_id = operation.get("operationId")
            if operation_id is None:
                continue
            function_name = operation_id.split(".")[-1]
            assert hasattr(main_module, function_name), (
                f"{method.upper()} {path}: нет функции {operation_id}"
            )


def test_openapi_static_paths_precede_dynamic_entity_type():
    """Статические пути объявлены  /api/{entity_type}.

    """

    # Подготовка
    paths = list(_spec()["paths"])

    # Действие
    dynamic = paths.index("/api/{entity_type}")

    # Проверки
    for path in paths:
        is_static_one_segment = path.count("/") == 2 and "{" not in path
        if is_static_one_segment:
            assert paths.index(path) < dynamic, (
                f"Статический путь {path} должен быть объявлен "
                f"раньше /api/{{entity_type}}"
            )


def test_osv_is_resolved_before_dynamic_entity_type():
    """ASGI-запрос к /api/osv не попадает в /api/{entity_type}.

    """

    # Подготовка
    app = connexion.FlaskApp(__name__)
    app.add_url_rule(
        "/api/osv",
        "osv_stub",
        lambda: {"header": [], "rows": []},
        methods=["POST"],
    )
    app.add_api(str(_spec_path()))

    async def request():
        transport = httpx.ASGITransport(app=app.middleware)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test",
        ) as client:
            return await client.post("/api/osv", json={"filters": []})

    # Действие
    response = asyncio.run(request())

    # Проверки
    assert response.status_code == 200, response.text
    assert response.json() == {"header": [], "rows": []}


def test_openapi_filter_condition_supports_all_types():
    """Схема FilterCondition описывает between и обе сортировки."""
    # Подготовка
    spec = _spec()
    condition = spec["components"]["schemas"]["FilterCondition"]
    filter_type = condition["properties"]["filter_type"]

    # Действие
    supported_types = set(filter_type["enum"])

    # Проверки
    assert supported_types >= {
        "equals", "like", "between", "alphabet", "alphabet_desc",
        "reverse_alphabet", "alphabet_reverse",
    }
    assert condition["required"] == ["filter_name"]


def test_openapi_osv_returns_downloadable_file():
    """Ответ ОСВ описан как скачиваемый файл отчёта."""

    # Подготовка
    spec = _spec()

    # Действие
    responses = spec["paths"]["/api/osv"]["post"]["responses"]

    # Проверки
    assert responses["200"] == {
        "$ref": "#/components/responses/BinaryFile"
    }
    binary = spec["components"]["responses"]["BinaryFile"]
    assert "text/csv" in binary["content"]
    assert "Content-Disposition" in binary["headers"]

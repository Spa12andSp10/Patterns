import io
from pathlib import Path

import connexion
from flask import Response, request, send_file

from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.entity_resolver import entity_resolver
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager

api = connexion.FlaskApp(__name__)


def _storage_path() -> str:
    """Путь к файлу storage_data.json (эталонные данные)."""
    return str(Path(__file__).resolve().parent / "Tst" / "storage_data.json")


def _settings_path() -> str:
    """Путь к файлу settings.json (настройки приложения)."""
    return str(Path(__file__).resolve().parent / "Tst" / "settings.json")


def _init_storage() -> storage_manager:
    """Инициализирует и загружает хранилище при старте приложения."""
    settings_manager().load(_settings_path())
    settings_manager().settings.first_launch_flag = True
    storage = storage_manager()
    storage.first_start(_storage_path())
    return storage


storage = _init_storage()
factory = report_factory()
resolver = entity_resolver(storage)


def _parse_report_type(slug: str) -> report_type_enum:
    """Разбирает slug формата отчёта.

    :raises ValueError: Если формат неизвестен.
    """
    return report_type_enum.from_slug(slug)


def _download_page(download_url: str, file_name: str) -> Response:
    """HTML-страница со ссылкой на скачивание бинарного файла."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Скачивание файла</title>
        <style>
            body {{ font-family: sans-serif; text-align: center; margin-top: 50px; }}
            .btn {{ display: inline-block; padding: 10px 20px; background: #007bff;
                    color: white; text-decoration: none; border-radius: 5px; }}
            .btn:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <h2>Файл {file_name} готов к скачиванию</h2>
        <p><a href="{download_url}" class="btn">Скачать файл</a></p>
    </body>
    </html>
    """
    return Response(html, content_type="text/html; charset=utf-8")


def _build_response(result, download_url: str, file_name: str) -> Response:
    """Отдаёт либо текст напрямую, либо страницу со ссылкой на файл.

    MIME берётся из result.mime — контроллер не знает, какой формат
    перед ним.
    """
    if result.is_binary:
        return _download_page(download_url, file_name)
    return Response(result.text, status=200, content_type=result.mime)


def _send_binary(result, file_name: str):
    """Отдаёт бинарный файл как attachment."""
    return send_file(
        io.BytesIO(result.binary),
        mimetype=result.mime.split(";")[0].strip(),
        as_attachment=True,
        download_name=file_name,
    )


def _resolve_or_error(entity_type: str, code: str):
    """Обёртка над резолвером: (entity, None) или (None, Response)."""
    try:
        return resolver.resolve(entity_type, code), None
    except LookupError as e:
        return None, Response(str(e), status=404)
    except Exception as e:
        return None, Response(str(e), status=400)


def _find_default_recipe():
    """Жёстко заданный рецепт для /api/get_report."""
    return next(
        (card for card in storage.recipes
         if card.name == "Pasta with beef in milk-apple sauce"),
        None,
    )


@api.route("/api/get_report", methods=["GET"])
def get_report():
    """Возвращает отчёт по жестко заданному рецепту.

    Формат определяется параметром ?fmt= или берется из настроек.
    Если формат бинарный, возвращается HTML-страница со ссылкой
    на скачивание.
    """
    recipe = _find_default_recipe()
    if recipe is None:
        return "Рецепт не найден", 404

    fmt = (request.args.get("fmt") or "").lower() \
        or settings_manager().settings.response_format.lower()

    try:
        report_type = _parse_report_type(fmt)
    except ValueError:
        return f"Неизвестный формат: {fmt!r}", 400

    result = factory.create(report_type).build(recipe)
    file_name = f"{recipe.name}.{report_type.slug}"

    return _build_response(
        result,
        download_url=f"/api/get_report/download?fmt={report_type.slug}",
        file_name=file_name,
    )


@api.route("/api/get_report/download", methods=["GET"])
def get_report_download():
    """Отдаёт бинарный файл отчета для жестко заданного рецепта."""
    recipe = _find_default_recipe()
    if recipe is None:
        return "Рецепт не найден", 404

    fmt = (request.args.get("fmt") or "").lower()
    try:
        report_type = _parse_report_type(fmt)
    except ValueError:
        return "Неизвестный формат", 400

    result = factory.create(report_type).build(recipe)

    if not result.is_binary:
        return "Этот формат не является файлом", 400

    return _send_binary(result, f"{recipe.name}.{report_type.slug}")


@api.route("/api/get_report_with_type_and_code", methods=["GET"])
def get_report_with_type_and_code():
    """Возвращает отчет по указанному типу сущности и уникальному коду.

    Тип сущности (`type`) может быть: recipe, nomenclature, range.
    """
    fmt = (request.args.get("fmt") or "").lower() \
        or settings_manager().settings.response_format.lower()

    try:
        report_type = _parse_report_type(fmt)
    except ValueError:
        return f"Неизвестный формат: {fmt!r}", 400

    entity_type = (request.args.get("type") or "").lower()
    code = (request.args.get("code") or "").strip()

    entity, error = _resolve_or_error(entity_type, code)
    if error is not None:
        return error

    try:
        result = factory.create(report_type).build(entity)
    except Exception as e:
        return f"Ошибка формирования отчета: {str(e)}", 500

    file_name = f"{entity_type}_{code}.{report_type.slug}"

    return _build_response(
        result,
        download_url=(
            f"/api/get_report_download_with_type_and_code"
            f"?fmt={report_type.slug}&type={entity_type}&code={code}"
        ),
        file_name=file_name,
    )


@api.route("/api/get_report_download_with_type_and_code", methods=["GET"])
def get_report_download_with_type_and_code():
    """Отдаёт бинарный файл отчёта для указанной сущности (скачивание)."""
    fmt = (request.args.get("fmt") or "").lower()
    entity_type = (request.args.get("type") or "").lower()
    code = (request.args.get("code") or "").strip()

    try:
        report_type = _parse_report_type(fmt)
    except ValueError:
        return "Неизвестный формат", 400

    entity, error = _resolve_or_error(entity_type, code)
    if error is not None:
        return error

    result = factory.create(report_type).build(entity)

    if not result.is_binary:
        return "Этот формат не является файлом", 400

    return _send_binary(result, f"{entity_type}_{code}.{report_type.slug}")


@api.route("/api/create_default", methods=["GET"])
def create_default():
    """Формирует отчёт в формате, указанном в settings.json.

    Формат берется динамически из файла настроек. Если он бинарный,
    возвращается страница со ссылкой на скачивание.
    """
    entity_type = (request.args.get("type") or "").lower()
    code = (request.args.get("code") or "").strip()

    entity, error = _resolve_or_error(entity_type, code)
    if error is not None:
        return error

    sm = settings_manager()
    sm.load(_settings_path())

    fmt = sm.settings.response_format.lower()
    report_type = _parse_report_type(fmt)

    try:
        result = factory.create(report_type).build(entity)
    except Exception as e:
        return f"Ошибка формирования отчета: {str(e)}", 500

    file_name = f"{entity_type}_{code}.{report_type.slug}"

    return _build_response(
        result,
        download_url=(
            f"/api/create_default_download?type={entity_type}&code={code}"
        ),
        file_name=file_name,
    )


@api.route("/api/create_default_download", methods=["GET"])
def create_default_download():
    """Отдаёт бинарный файл дефолтного формата (только для скачивания)."""
    entity_type = (request.args.get("type") or "").lower()
    code = (request.args.get("code") or "").strip()

    entity, error = _resolve_or_error(entity_type, code)
    if error is not None:
        return error

    sm = settings_manager()
    sm.load(_settings_path())
    fmt = sm.settings.response_format.lower()
    report_type = _parse_report_type(fmt)

    try:
        result = factory.create(report_type).build(entity)
    except Exception as e:
        return f"Ошибка формирования отчета: {str(e)}", 500

    if not result.is_binary:
        return "Текущий формат в настройках не является файлом", 400

    return _send_binary(result, f"{entity_type}_{code}.{report_type.slug}")


if __name__ == "__main__":
    api.run(host="0.0.0.0", port=1111)
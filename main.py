# main.py
import io
from pathlib import Path

import connexion
from flask import Response, request, send_file

from Src.Dtos.report_type_enum import report_type_enum
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
    """Инициализирует и загружает хранилище при старте приложения.
    
    Загружает настройки, ставит флаг первого старта, инициализирует
    и загружает справочники из JSON.
    """
    settings_manager().load(_settings_path())
    settings_manager().settings.first_launch_flag = True
    storage = storage_manager()
    storage.first_start(_storage_path())
    return storage


# Глобальные экземпляры хранилища и фабрики отчетов
storage = _init_storage()
factory = report_factory()


@api.route("/api/get_report", methods=["GET"])
def get_report():
    """Возвращает отчёт по жестко заданному рецепту.
    
    Формат определяется параметром ?fmt= или берется из настроек.
    Если формат бинарный, возвращается HTML-страница со ссылкой на скачивание.
    """
    recipe = next(
        (card for card in storage.recipes
         if card.name == "Pasta with beef in milk-apple sauce"),
        None,
    )
    if recipe is None:
        return "Рецепт не найден", 404

    # Определение формата (из query или из настроек по умолчанию)
    fmt = (request.args.get("fmt") or "").lower() \
        or settings_manager().settings.response_format.lower()

    try:
        report_type = report_type_enum.from_slug(fmt)
    except ValueError:
        return f"Неизвестный формат: {fmt!r}", 400

    result = factory.create(report_type).build(recipe)

    if result.binary:
        # Формируем страницу для скачивания файла
        download_url = f"/api/get_report/download?fmt={report_type.slug}"
        file_name = f"{recipe.name}.{report_type.slug}"
        
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

    # Если текстовый формат - возвращаем его напрямую
    return Response(result.text, status=200, content_type=report_type.mime)


@api.route("/api/get_report/download", methods=["GET"])
def get_report_download():
    """Отдаёт бинарный файл отчета (только для скачивания)."""
    recipe = next(
        (card for card in storage.recipes
         if card.name == "Pasta with beef in milk-apple sauce"),
        None,
    )
    if recipe is None:
        return "Рецепт не найден", 404

    fmt = (request.args.get("fmt") or "").lower()
    try:
        report_type = report_type_enum.from_slug(fmt)
    except ValueError:
        return "Неизвестный формат", 400

    result = factory.create(report_type).build(recipe)

    if not result.binary:
        return "Этот формат не является файлом", 400

    return send_file(
        io.BytesIO(result.binary),
        mimetype=report_type.mime.split(";")[0].strip(),
        as_attachment=True,
        download_name=f"{recipe.name}.{report_type.slug}",
    )


@api.route("/api/get_report_with_type_and_code", methods=["GET"])
def get_report_with_type_and_code():
    """Возвращает отчет по указанному типу сущности и уникальному коду.
    
    Тип сущности (`type`) может быть: recipe, nomenclature, range.
    """
    fmt = (request.args.get("fmt") or "").lower()
    if not fmt:
        fmt = settings_manager().settings.response_format.lower()
        
    try:
        report_type = report_type_enum.from_slug(fmt)
    except ValueError:
        return f"Неизвестный формат: {fmt!r}", 400

    entity_type = (request.args.get("type") or "").lower()
    if not entity_type:
        return "Параметр 'type' обязателен", 400

    code = (request.args.get("code") or "").strip()
    if not code:
        return "Параметр 'code' обязателен", 400

    # Поиск сущности
    entity = None
    if entity_type == "recipe":
        entity = next((x for x in storage.recipes if x.unique_code == code), None)
    elif entity_type == "nomenclature":
        entity = next((x for x in storage.nomenclatures if x.unique_code == code), None)
    elif entity_type == "range":
        entity = next((x for x in storage.ranges if x.unique_code == code), None)
    
    if not entity:
        return f"Сущность типа '{entity_type}' с кодом '{code}' не найдена", 404

    try:
        result = factory.create(report_type).build(entity)
    except Exception as e:
        return f"Ошибка формирования отчета: {str(e)}", 500

    if result.is_binary:
        download_url = f"/api/get_report_download_with_type_and_code?fmt={report_type.slug}&type={entity_type}&code={code}"
        file_name = f"{entity_type}_{code}.{report_type.slug}"
        
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

    return Response(result.text, status=200, content_type=report_type.mime)


@api.route("/api/get_report_download_with_type_and_code", methods=["GET"])
def get_report_download_with_type_and_code():
    """Отдаёт бинарный файл отчёта для указанной сущности (скачивание)."""
    fmt = (request.args.get("fmt") or "").lower()
    entity_type = (request.args.get("type") or "").lower()
    code = (request.args.get("code") or "").strip()

    try:
        report_type = report_type_enum.from_slug(fmt)
    except ValueError:
        return "Неизвестный формат", 400

    entity = None
    if entity_type == "recipe":
        entity = next((x for x in storage.recipes if x.unique_code == code), None)
    elif entity_type == "nomenclature":
        entity = next((x for x in storage.nomenclatures if x.unique_code == code), None)
    elif entity_type == "range":
        entity = next((x for x in storage.ranges if x.unique_code == code), None)

    if not entity:
        return "Сущность не найдена", 404

    result = factory.create(report_type).build(entity)

    if not result.is_binary:
        return "Этот формат не является файлом", 400

    return send_file(
        io.BytesIO(result.binary),
        mimetype=report_type.mime.split(";")[0].strip(),
        as_attachment=True,
        download_name=f"{entity_type}_{code}.{report_type.slug}",
    )


@api.route("/api/create_default", methods=["GET"])
def create_default():
    """Формирует отчёт в формате, указанном в settings.json.
    
    Формат берется динамически из файла настроек. Если он бинарный,
    возвращается страница со ссылкой на скачивание.
    """
    entity_type = (request.args.get("type") or "").lower()
    code = (request.args.get("code") or "").strip()

    if not entity_type or not code:
        return "Параметры 'type' и 'code' обязательны", 400

    # Поиск сущности
    entity = None
    if entity_type == "recipe":
        entity = next((x for x in storage.recipes if x.unique_code == code), None)
    elif entity_type == "nomenclature":
        entity = next((x for x in storage.nomenclatures if x.unique_code == code), None)
    elif entity_type == "range":
        entity = next((x for x in storage.ranges if x.unique_code == code), None)

    if not entity:
        return "Сущность не найдена", 404

    # Перечитываем настройки с диска, чтобы подхватить актуальный формат
    sm = settings_manager()
    sm.load(_settings_path())
    
    fmt = sm.settings.response_format.lower()
    report_type = report_type_enum.from_slug(fmt)

    try:
        report = factory.create(report_type)
        result = report.build(entity)
    except Exception as e:
        return f"Ошибка формирования отчета: {str(e)}", 500

    if result.is_binary:
        download_url = f"/api/create_default_download?type={entity_type}&code={code}"
        file_name = f"{entity_type}_{code}.{report_type.slug}"
        
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

    return Response(result.text, status=200, content_type=report_type.mime)


@api.route("/api/create_default_download", methods=["GET"])
def create_default_download():
    """Отдаёт бинарный файл дефолтного формата (только для скачивания)."""
    entity_type = (request.args.get("type") or "").lower()
    code = (request.args.get("code") or "").strip()

    if not entity_type or not code:
        return "Параметры 'type' и 'code' обязательны", 400

    # Поиск сущности
    entity = None
    if entity_type == "recipe":
        entity = next((x for x in storage.recipes if x.unique_code == code), None)
    elif entity_type == "nomenclature":
        entity = next((x for x in storage.nomenclatures if x.unique_code == code), None)
    elif entity_type == "range":
        entity = next((x for x in storage.ranges if x.unique_code == code), None)

    if not entity:
        return "Сущность не найдена", 404

    # Перечитываем настройки с диска
    sm = settings_manager()
    sm.load(_settings_path())
    fmt = sm.settings.response_format.lower()
    report_type = report_type_enum.from_slug(fmt)

    try:
        report = factory.create(report_type)
        result = report.build(entity)
    except Exception as e:
        return f"Ошибка формирования отчета: {str(e)}", 500

    if not result.is_binary:
        return "Текущий формат в настройках не является файлом", 400

    return send_file(
        io.BytesIO(result.binary),
        mimetype=report_type.mime.split(";")[0].strip(),
        as_attachment=True,
        download_name=f"{entity_type}_{code}.{report_type.slug}",
    )


if __name__ == "__main__":
    api.run(host="0.0.0.0", port=1111)
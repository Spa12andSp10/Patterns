import io
from pathlib import Path

import connexion
from flask import Response, request, send_file

from Src.Core.exception import arguments_exeption
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.entity_resolver import entity_resolver
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_bootstrap import storage_bootstrap
from Src.Logics.storage_deserializer import storage_deserializer
from Src.Logics.storage_manager import storage_manager

api = connexion.FlaskApp(__name__)



def _storage_path() -> str:
    """Путь к файлу storage_data.json (эталонные данные)."""
    return str(Path(__file__).resolve().parent / "Tst" / "storage_data.json")


def _storage_models_path() -> str:
    """Путь к сериализованному storage (если он уже сохранён)."""
    return str(Path(__file__).resolve().parent / "Tst" / "serialized_storage.json")


def _settings_path() -> str:
    """Путь к файлу settings.json (настройки приложения)."""
    return str(Path(__file__).resolve().parent / "Tst" / "settings.json")



def _init_settings() -> settings_manager:
    """Загружает настройки через сам менеджер."""
    sm = settings_manager()
    sm.load(_settings_path())
    return sm


def _init_storage() -> storage_manager:
    """Инициализирует хранилище.

    Логика:
      1. Если есть serialized_storage.json — грузим его
         через storage_deserializer (симметрично save_models).
      2. Иначе — первый старт: наполняем из «сырого» storage_data.json
         через storage_bootstrap.
    """
    storage = storage_manager()

    models_path = Path(_storage_models_path())
    if models_path.exists():
        ok = storage_deserializer(storage).load(str(models_path))
        if ok:
            storage._is_loaded = True
            return storage

    raw_path = Path(_storage_path())
    if raw_path.exists():
        storage_bootstrap(storage).first_start(str(raw_path))
        storage._is_loaded = True

    return storage


settings_manager_instance = _init_settings()
storage = _init_storage()

factory = report_factory()
resolver = entity_resolver(storage)



def _parse_report_type(slug: str) -> report_type_enum:
    """Разбирает slug формата отчёта."""
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
    """Отдаёт либо текст напрямую, либо страницу со ссылкой на файл."""
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


def _find_references(target_model, storage, visited=None):
    """Ищет ссылки на target_model в других сущностях.
    Возвращает (объект_родитель, имя_поля) или None.
    """
    if visited is None:
        visited = set()

    if target_model.unique_code in visited:
        return None
    visited.add(target_model.unique_code)

    all_entities = (
        storage.groups + storage.ranges + storage.nomenclatures +
        storage.warehouses + storage.recipes
    )

    for entity in all_entities:
        if entity is target_model:
            continue
        for attr_name in dir(entity):
            if attr_name.startswith("_"):
                continue

            try:
                attr_value = getattr(entity, attr_name)
            except Exception:
                continue

            if attr_value is target_model:
                return entity, attr_name

            if isinstance(attr_value, list):
                for item in attr_value:
                    if item is target_model:
                        return entity, attr_name

                    if hasattr(item, "unique_code"):
                        for sub_attr in dir(item):
                            if sub_attr.startswith("_"):
                                continue
                            try:
                                if getattr(item, sub_attr) is target_model:
                                    return entity, f"{attr_name}[].{sub_attr}"
                            except Exception:
                                pass

    return None



@api.route("/api/get_report", methods=["GET"])
def get_report():
    """Возвращает отчёт по жестко заданному рецепту."""
    recipe = _find_default_recipe()
    if recipe is None:
        return "Рецепт не найден", 404

    fmt = (request.args.get("fmt") or "").lower() \
        or settings_manager_instance.settings.response_format.lower()

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
    """Возвращает отчет по указанному типу сущности и уникальному коду."""
    fmt = (request.args.get("fmt") or "").lower() \
        or settings_manager_instance.settings.response_format.lower()

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
    """Формирует отчёт в формате, указанном в settings.json."""
    entity_type = (request.args.get("type") or "").lower()
    code = (request.args.get("code") or "").strip()

    entity, error = _resolve_or_error(entity_type, code)
    if error is not None:
        return error

    settings_manager_instance.reload()

    fmt = settings_manager_instance.settings.response_format.lower()
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

    settings_manager_instance.reload()

    fmt = settings_manager_instance.settings.response_format.lower()
    report_type = _parse_report_type(fmt)

    try:
        result = factory.create(report_type).build(entity)
    except Exception as e:
        return f"Ошибка формирования отчета: {str(e)}", 500

    if not result.is_binary:
        return "Текущий формат в настройках не является файлом", 400

    return _send_binary(result, f"{entity_type}_{code}.{report_type.slug}")


@api.route("/api/get_codes", methods=["GET"])
def get_codes():
    entity_type = (request.args.get("type") or "").strip().lower()
    supported = resolver.supported_types()

    def _items_for(t: str):
        return [
            {"name": getattr(m, "name", ""), "code": m.unique_code}
            for m in resolver.provider_for(t)()
        ]

    if entity_type:
        if entity_type not in supported:
            return (
                f"Неизвестный тип: {entity_type!r}. "
                f"Допустимые: {sorted(supported)}"
            ), 400
        return {
            "type": entity_type,
            "items": _items_for(entity_type),
        }

    return {t: _items_for(t) for t in supported}


@api.route("/api/get_formats", methods=["GET"])
def get_formats():
    """Возвращает список поддерживаемых форматов отчётов."""
    return [
        {"name": item.name, "slug": item.slug, "code": item.code, "mime": item.mime}
        for item in report_type_enum
    ]



@api.route("/api/<entity_type>/<code>", methods=["PUT"])
def create_entity_with_code(entity_type: str, code: str):
    supported = resolver.supported_types()
    if entity_type not in supported:
        return (
            f"Неизвестный тип: {entity_type!r}. "
            f"Допустимые: {sorted(supported)}"
        ), 400

    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return "Тело должно быть JSON-объектом", 400

    body_entity_type = body.pop("entity_type", None)
    if body_entity_type != entity_type:
        return (
            f"entity_type в теле ({body_entity_type!r}) "
            f"не совпадает с path ({entity_type!r})"
        ), 400

    storage = storage_manager()
    provider = resolver.provider_for(entity_type)
    existing = next(
        (m for m in provider() if m.unique_code == code),
        None,
    )
    if existing is not None:
        return (
            f"Сущность типа {entity_type!r} с кодом {code!r} уже существует",
            409,
        )

    try:
        factory = deserialize_factory()
        model = factory.deserialize({**body, "unique_code": code})

        if isinstance(model, dict):
            return (
                f"Тело не соответствует ни одной модели. "
                f"Передайте обязательные поля для {entity_type!r}"
            ), 400

        model.unique_code = code
    except arguments_exeption as e:
        return str(e), 400
    except Exception as e:
        return f"Ошибка создания сущности: {str(e)}", 400

    add = getattr(storage, f"add_{entity_type}", None)
    if add is None:
        return f"Хранилище не поддерживает add_{entity_type}", 500
    if not add(model):
        return (
            f"Не удалось добавить {entity_type!r}: конфликт уникальности",
            409,
        )

    return "", 201, {"Location": f"/api/{entity_type}/{code}"}


@api.route("/api/<entity_type>", methods=["POST"])
def create_entity(entity_type: str):
    supported = resolver.supported_types()
    if entity_type not in supported:
        return (
            f"Неизвестный тип: {entity_type!r}. "
            f"Допустимые: {sorted(supported)}"
        ), 400

    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return "Тело должно быть JSON-объектом", 400

    body_entity_type = body.pop("entity_type", None)
    if body_entity_type != entity_type:
        return (
            f"entity_type в теле ({body_entity_type!r}) "
            f"не совпадает с path ({entity_type!r})"
        ), 400

    try:
        factory = deserialize_factory()
        model = factory.deserialize(body)
        if isinstance(model, dict):
            return (
                f"Тело не соответствует ни одной модели. "
                f"Передайте обязательные поля для {entity_type!r}"
            ), 400
    except arguments_exeption as e:
        return str(e), 400
    except Exception as e:
        return f"Ошибка создания сущности: {str(e)}", 400

    storage = storage_manager()
    add = getattr(storage, f"add_{entity_type}", None)
    if add is None:
        return f"Хранилище не поддерживает add_{entity_type}", 500
    if not add(model):
        return (
            f"Не удалось добавить {entity_type!r}: конфликт уникальности",
            409,
        )

    return "", 201, {"Location": f"/api/{entity_type}/{model.unique_code}"}


@api.route("/api/delete/<code>", methods=["DELETE"])
def delete(code: str):
    """Удаляет сущность по уникальному коду, проверяя связи."""
    storage = storage_manager()

    all_collections = (
        storage.groups,
        storage.ranges,
        storage.nomenclatures,
        storage.warehouses,
        storage.recipes,
    )

    existing = None
    target_collection = None

    for collection in all_collections:
        for item in collection:
            if item.unique_code == code:
                existing = item
                target_collection = collection
                break
        if existing:
            break

    if existing is None:
        return f"Сущность с кодом {code!r} не найдена", 404

    ref_result = _find_references(existing, storage)

    if ref_result is not None:
        ref_entity, ref_attr = ref_result
        name = getattr(ref_entity, "name", ref_entity.unique_code)
        return (
            f"Нельзя удалить сущность (код: {code}): "
            f"на неё ссылается {type(ref_entity).__name__} '{name}' "
            f"(поле '{ref_attr}')",
            409,
        )

    try:
        target_collection.remove(existing)
    except ValueError:
        return "Ошибка удаления из хранилища", 500

    return "", 204


@api.route("/api/update/<code>", methods=["PATCH"])
def update(code: str):
    """Обновляет поля сущности по уникальному коду (PATCH)."""
    body = request.get_json(silent=True, force=True)
    if not isinstance(body, dict):
        return "Тело должно быть JSON-объектом", 400

    if "unique_code" in body:
        return "Изменение unique_code запрещено", 400
    body.pop("entity_type", None)

    storage = storage_manager()

    all_collections = (
        storage.groups,
        storage.ranges,
        storage.nomenclatures,
        storage.warehouses,
        storage.recipes,
    )

    existing = None
    target_collection = None

    for collection in all_collections:
        for item in collection:
            if item.unique_code == code:
                existing = item
                target_collection = collection
                break
        if existing:
            break

    if existing is None:
        return f"Сущность с кодом {code!r} не найдена", 404

    try:
        factory = deserialize_factory()

        from Src.Logics.convert_factory import convert_factory
        walker = convert_factory().create()
        current_data = walker.convert(existing)

        current_data.pop("unique_code", None)
        current_data.pop("item_type", None)
        current_data.pop("max_lenght", None)

        current_data.update(body)

        updated_model = factory.deserialize(current_data)
        updated_model.unique_code = code

        idx = target_collection.index(existing)
        target_collection[idx] = updated_model

    except arguments_exeption as e:
        return str(e), 400
    except Exception as e:
        return f"Ошибка обновления: {str(e)}", 400

    return "", 200


if __name__ == "__main__":
    api.add_api('openapi.yaml')
    api.run(host="0.0.0.0", port=1111)
from enum import Enum

"""Типы событий"""

class event_types(Enum):

    CHANGE_SETTINGS = "change_settings"
    LOAD_SETTINGS = "load_settings"
    SAVE_SETTINGS = "seve_seettings"
    CHANGE_STORAGE = "change_storage"
    LOAD_STORAGE = "load_storage"
    CREATE_OBJECT = "create_aobjscr"
    CREATE_OBJECT_WITH_CODE = "create_object_with_code"
    UPDATE_OBJECT = "update_object"
    DELETE_OBJECT = "delete_object"
    WAREHOUSE_INCOME = "warehouse_income"
    WAREHOUSE_OUTCOME = "warehouse_outcimne"
    WEB_REQUEST = "web_request"
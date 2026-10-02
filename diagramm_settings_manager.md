classDiagram
    class abstract_manager {
        <<abstract>>
        #_file_name: str
        #_is_loaded: bool
        #_data: dict
        +load(file_name: str) None
        +convert() bool
        +is_loaded: bool
    }

    class settings_manager {
        -__default_file_name: str = "settings.json"
        -_settings: settings_model
        +__new__() settings_manager
        +load(file_name: str) None
        +convert() bool
        +settings: settings_model
        +data: dict
    }

    class settings_model {
        -__organization: organization_model
        -__boss_name: str
        -__account_name: str
        -__first_launch_flag: bool
        +organization: organization_model
        +boss_name: str
        +account_name: str
        +first_launch_flag: bool
    }

    class organization_model {
        -__inn: str
        -__bic: str
        -__account: str
        -__owner: str
        +name: str
        +inn: str
        +bic: str
        +account: str
        +owner: str
    }

    class entity_model {
        <<abstract>>
        -__name: str
        -__max_length: int = 50
        +name: str
        +max_lenght: int
    }

    class abstact_model {
        <<abstract>>
        -__unique_code: str
        +unique_code: str
        +__eq__(value) bool
    }

    %% Наследование (полая треугольная стрелка) — "является"
    abstract_manager <|-- settings_manager : наследует
    abstact_model <|-- entity_model : наследует
    entity_model <|-- organization_model : наследует
    abstact_model <|-- settings_model : наследует

    %% Агрегация (полый ромб) — "содержит"
    settings_manager  o--  settings_model : содержит
    settings_model  o--  organization_model : содержит

from Src.Logics.reference_finder import reference_finder
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.technicalmap_model import technicalmap_model


def _create_technicalmap(name: str, ingredients: list = None) -> technicalmap_model:
    """Создаёт технологическую карту с минимальным набором полей.

    :param name: Наименование карты.
    :param ingredients: Состав карты.
    :return: Технологическая карта.
    """
    return technicalmap_model.create(
        ingredients=ingredients or [],
        preparation_method={},
        description=name,
        time="1 min",
        name=name,
    )


def test_valid_result_reference_finder_direct_field():
    """
    Проверяет поиск прямой ссылки на группу в поле модели.
    Ожидаемый результат: ссылка найдена в поле 'group' номенклатуры.
    """
    # Подготовка
    group = group_model.create("Dairy products")
    gram = range_model.create_gram()
    nom = nomenclature_model.create(
        full_name="Milk",
        name="Milk",
        group=group,
        range=gram,
        item_type="product",
    )

    finder = reference_finder(lambda: [group, gram, nom])

    # Действие
    result = finder.find(group)

    # Проверки
    assert result is not None
    assert result[0] is nom
    assert result[1] == "group"


def test_valid_result_reference_finder_nested_field():
    """
    Проверяет поиск ссылки во вложенном поле модели.
    Ожидаемый результат: ссылка найдена в поле 'base' единицы измерения.
    """
    # Подготовка
    gram = range_model.create_gram()
    kilogram = range_model.create_kilogram(base=gram)

    finder = reference_finder(lambda: [gram, kilogram])

    # Действие
    result = finder.find(gram)

    # Проверки
    assert result is not None
    assert result[0] is kilogram
    assert result[1] == "base"


def test_valid_result_reference_finder_list_item():
    """
    Проверяет поиск ссылки внутри списка.
    Ожидаемый результат: ссылка найдена в поле 'ingredients[0]'.
    """
    # Подготовка
    sauce = _create_technicalmap("Sauce")
    dish = _create_technicalmap("Dish", ingredients=[sauce])

    finder = reference_finder(lambda: [sauce, dish])

    # Действие
    result = finder.find(sauce)

    # Проверки
    assert result is not None
    assert result[0] is dish
    assert result[1] == "ingredients[0]"


def test_valid_result_reference_finder_nested_path():
    """
    Проверяет построение пути через несколько уровней вложенности.
    Ожидаемый результат: путь 'ingredients[0].ingredients[0]'.
    """
    # Подготовка
    sauce = _create_technicalmap("Sauce")
    dish = _create_technicalmap("Dish", ingredients=[sauce])
    menu = _create_technicalmap("Menu", ingredients=[dish])

    finder = reference_finder(lambda: [sauce, menu])

    # Действие
    result = finder.find(sauce)

    # Проверки
    assert result is not None
    assert result[0] is menu
    assert result[1] == "ingredients[0].ingredients[0]"


def test_invalid_result_reference_finder_no_references():
    """
    Проверяет отсутствие ссылок на модель.
    Ожидаемый результат: None.
    """
    # Подготовка
    group = group_model.create("Dairy products")
    other = group_model.create("Meat products")

    finder = reference_finder(lambda: [group, other])

    # Действие
    result = finder.find(group)

    # Проверки
    assert result is None


def test_valid_result_reference_finder_cyclic_references():
    """
    Проверяет, что поиск не зацикливается на взаимных ссылках.
    Ожидаемый результат: None, поиск завершается.
    """
    # Подготовка
    first = _create_technicalmap("First")
    second = _create_technicalmap("Second")
    first.ingredients = [second]
    second.ingredients = [first]

    target = group_model.create("Unreferenced group")
    finder = reference_finder(lambda: [first, second, target])

    # Действие
    result = finder.find(target)

    # Проверки
    assert result is None

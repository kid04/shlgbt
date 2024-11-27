import json


def save(data):
    """
    Функция сохранения данных
    :param data:
    :return: None
    """
    f = open('data.json', 'w')
    json.dump(data, f, indent=4, separators=(", ", " : "))
    f.close()
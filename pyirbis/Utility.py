# Разные полезняшки

# Коды для команды ReadRecord
READ_RECORD_CODES = [-201, -600, -602, -603]

# Коды для команды ReadTerms
READ_TERMS_CODES = [-202, -203, -204]


def iif(*args):
    """
    Выдает первый не пустой аргумент
    """
    for a in args:
        if a:
            return a
    return None

def throw_value_error() -> None:
    """
    Выдаёт исключение.

    :return: None
    """
    raise ValueError
# coding: utf-8

"""
Константы и утилитные функции.
"""

import asyncio
from typing import Union, Optional, SupportsInt, List

#############################################################################
# COMMON CONSTANTS
#############################################################################

# Max number of postings

MAX_POSTINGS = 32758

# Encodings

ANSI = 'cp1251'
UTF = 'utf-8'
OEM = 'cp866'

# Stop marker for menus

STOP_MARKER = '*****'

# Record status

LOGICALLY_DELETED = 1
PHYSICALLY_DELETED = 2
ABSENT = 4
NON_ACTUALIZED = 8
NEW_RECORD = 16
LAST = 32
LOCKED = 64
AUTOIN_ERROR = 128
FULL_TEXT_NOT_ACTUALIZED = 256

# Paths

SYSTEM = 0
DATA = 1
MASTER_FILE = 2
INVERTED_FILE = 3
PARAMETER_FILE = 10
FULL_TEXT = 11
INTERNAL_RESOURCE = 12

# Text delimiters

IRBIS_DELIMITER = '\x1F\x1E'
SHORT_DELIMITER = '\x1E'
OTHER_DELIMITER = '\x1F'
MSDOS_DELIMITER = '\r\n'

# Common formats

ALL = "&uf('+0')"
BRIEF = '@brief'
IBIS = '@ibiskw_h'
INFORMATIONAL = '@info_w'
OPTIMIZED = '@'

# Workstation codes

ADMINISTRATOR = 'A'
CATALOGER = 'C'
ACQUISITIONS = 'M'
COMPLECT = 'M'
READER = 'R'
CIRCULATION = 'B'
BOOKLAND = 'B'
PROVISION = 'K'
JAVA_APPLET = 'J'

# Error codes

# Клиент не подключен к серверу
NOT_CONNECTED = -100500

# Command codes

# Получение признака монопольной блокировки базы данных
EXCLUSIVE_DATABASE_LOCK = '#'

# Получение списка удаленных, неактуализированных
# и заблокированных записей
RECORD_LIST = '0'

# Получение версии сервера
SERVER_INFO = '1'

# Получение статистики по базе данных
DATABASE_STAT = '2'

# Глобальная корректировка
GLOBAL_CORRECTION = '5'

# Сохранение группы записей
SAVE_RECORD_GROUP = '6'

# Печать
PRINT = '7'

# Запись параметров в ini - файл, расположенный на сервере
UPDATE_INI_FILE = '8'

IMPORT_ISO = '9'

# Регистрация клиента на сервере
REGISTER_CLIENT = 'A'

# Разрегистрация клиента
UNREGISTER_CLIENT = 'B'

# Чтение записи, ее расформатирование
READ_RECORD = 'C'

# Сохранение записи
UPDATE_RECORD = 'D'

# Разблокировка записи
UNLOCK_RECORD = 'E'

# Актуализация записи
ACTUALIZE_RECORD = 'F'

# Форматирование записи или группы записей
FORMAT_RECORD = 'G'

# Получение терминов и ссылок словаря,
# форматирование записей
READ_TERMS = 'H'

# Получение ссылок для термина (списка терминов)
READ_POSTINGS = 'I'

# Глобальная корректировка виртуальной записи
CORRECT_VIRTUAL_RECORD = 'J'

# Поиск записей с опциональным форматированием
SEARCH = 'K'

# Получение / сохранение текстового файла,
# расположенного на сервере (группы текстовых файлов)
READ_DOCUMENT = 'L'

BACKUP = 'M'

# Пустая операция. Периодическое подтверждение
# соединения с сервером
NOP = 'N'

# Получение максимального MFN для базы данных
GET_MAX_MFN = 'O'

# Получение терминов и ссылок словаря в обратном порядке
READ_TERMS_REVERSE = 'P'

# Разблокирование записей
UNLOCK_RECORDS = 'Q'

# Полнотекстовый поиск
FULL_TEXT_SEARCH = 'R'

# Опустошение базы данных
EMPTY_DATABASE = 'S'

# Создание базы данных
CREATE_DATABASE = 'T'

# Разблокирование базы данных
UNLOCK_DATABASE = 'U'

# Чтение ссылок для заданного MFN
GET_RECORD_POSTINGS = 'V'

# Удаление базы данных
DELETE_DATABASE = 'W'

# Реорганизация мастер - файла
RELOAD_MASTER_FILE = 'X'

# Реорганизация словаря
RELOAD_DICTIONARY = 'Y'

# Создание поискового словаря заново
CREATE_DICTIONARY = 'Z'

# Получение статистики работы сервера
GET_SERVER_STAT = '+1'

# Получение списка запущенных процессов
GET_PROCESS_LIST = '+3'

# Сохранение списка пользователей
SET_USER_LIST = '+7'

# Перезапуск сервера
RESTART_SERVER = '+8'

# Получение списка пользователей
GET_USER_LIST = '+9'

# Получение списка файлов на сервере
LIST_FILES = '!'

# Codes for ReadRecord command
READ_RECORD_CODES = [-201, -600, -602, -603]

# Codes for ReadTerms command
READ_TERMS_CODES = [-202, -203, -204]

#############################################################################
# COMMON FUNCTIONS
#############################################################################


def same_string(first: Optional[str], second: Optional[str]) -> bool:
    """
    Строки совпадают с точностью до регистра?

    :param first: Первая строка
    :param second: Вторая строка
    :return: True, если совпадают
    """
    if first is None or second is None:
        return False
    return first.upper() == second.upper()


def safe_str(obj) -> str:
    """
    Простое избегание 'None' при выводе текстового представления объекта.

    :param obj: Объект
    :return: Текстовое представление
    """
    if obj is None:
        return ''
    return str(obj)


def safe_int(text: Union[str, bytes, SupportsInt]) -> int:
    """
    Безопасное превращение строки в целое.

    :param text: Текст
    :return: Целое число
    """
    try:
        result: int = int(text)
    except ValueError:
        result = 0
    return result


# noinspection PyUnreachableCode
def throw_value_error() -> str:
    """
    Simple raises ValueError.

    :return: None
    """
    if 1 > 0:
        raise ValueError()
    return ''


def irbis_to_dos(text: str) -> str:
    """
    Convert IRBIS text to MS-DOS text.

    :param text: Text to convert
    :return: Converted text
    """
    return text.replace(IRBIS_DELIMITER, '\n')


def irbis_to_lines(text: str) -> List[str]:
    """
    Convert IRBIS text to list of strings.

    :param text: Text to convert
    :return: List of strings
    """
    return text.split(IRBIS_DELIMITER)


def short_irbis_to_lines(text: str) -> List[str]:
    """
    Convert IRBIS with short delimiter text to list of strings.

    :param text: Text to convert
    :return: List of strings
    """
    return text.split(SHORT_DELIMITER)


def remove_comments(text: str) -> str:
    """
    Удаление комментариев из кода.

    :param text: Код для очистки
    :return: Очищенный код
    """

    if '/*' not in text:
        return text

    result = []
    state = ''
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if state in ("'", '"', '|'):
            if char == state:
                state = ''
            result.append(char)
        else:
            if char == '/':
                if index + 1 < length and text[index + 1] == '*':
                    while index < length:
                        char = text[index]
                        if char in ('\r', '\n'):
                            result.append(char)
                            break
                        index = index + 1
                else:
                    result.append(char)
            else:
                if char in ("'", '"', '|'):
                    state = char
                    result.append(char)
                else:
                    result.append(char)
        index = index + 1

    return ''.join(result)


def prepare_format(text: str) -> str:
    """
    Подготовка формата к отсылке на сервер.

    :param text: Неподготовленный формат
    :return: Подготовленный формат
    """
    text = remove_comments(text)
    length = len(text)
    if length == 0:
        return text

    flag = False
    for char in text:
        if char < ' ':
            flag = True
            break

    if not flag:
        return text

    result = []
    for char in text:
        if char >= ' ':
            result.append(char)

    return ''.join(result)


##############################################################################

# pylint: disable=invalid-name
irbis_event_loop = None


def init_async() -> None:
    """
    Инициализация асинхронной обработки цикла сообщений.

    :return: None.
    """
    global irbis_event_loop  # pylint: disable=global-statement
    if not irbis_event_loop:
        irbis_event_loop = asyncio.get_event_loop()


def close_async() -> None:
    """
    Завершение асинхронной обработки цикла сообщений.

    :return: None.
    """
    global irbis_event_loop  # pylint: disable=global-statement
    if irbis_event_loop:
        irbis_event_loop.close()
        irbis_event_loop = None


##############################################################################


class ObjectWithError:
    """
    Объект, хранящий код последней ошибки.
    """

    __slots__ = ('last_error',)

    def __init__(self):
        self.last_error: int = 0

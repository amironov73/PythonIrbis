# coding: utf-8

# Common stuff for pyirbis

import random
import socket
from typing import Union, Optional, SupportsInt, List, Iterable

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
LAST = 32
LOCKED = 64

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

###############################################################################

# Miscellaneous utilities

# Codes for ReadRecord command
READ_RECORD_CODES = [-201, -600, -602, -603]

# Codes for ReadTerms command
READ_TERMS_CODES = [-202, -203, -204]


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


def remove_comments(text: str):
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
        c = text[index]
        if state == "'" or state == '"' or state == '|':
            if c == state:
                state = ''
            result.append(c)
        else:
            if c == '/':
                if index + 1 < length and text[index + 1] == '*':
                    while index < length:
                        c = text[index]
                        if c == '\r' or c == '\n':
                            result.append(c)
                            break
                        index = index + 1
                else:
                    result.append(c)
            else:
                if c == "'" or c == '"' or c == '|':
                    state = c
                    result.append(c)
                else:
                    result.append(c)
        index = index + 1

    return ''.join(result)


def prepare_format(text: str):
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
    for c in text:
        if c < ' ':
            flag = True
            break

    if not flag:
        return text

    result = []
    for c in text:
        if c >= ' ':
            result.append(c)

    return ''.join(result)


###############################################################################

# Исключение - ошибка протокола

def get_error_description(code: int) -> str:
    """
    Получение описания ошибки.

    :param code: Код ошибки
    :return: Описание ошибки
    """

    errors = {
        -100: 'Заданный MFN вне пределов БД',
        -101: 'Ошибочный размер полки',
        -102: 'Ошибочный номер полки',
        -140: 'MFN вне пределов БД',
        -141: 'Ошибка чтения',
        -200: 'Указанное поле отсутствует',
        -201: 'Предыдущая версия записи отсутствует',
        -202: 'Заданный термин не найден (термин не существует)',
        -203: 'Последний термин в списке',
        -204: 'Первый термин в списке',
        -300: 'База данных монопольно заблокирована',
        -301: 'База данных монопольно заблокирована',
        -400: 'Ошибка при открытии файлов MST или XRF (ошибка файла данных)',
        -401: 'Ошибка при открытии файлов IFP (ошибка файла индекса)',
        -402: 'Ошибка при записи',
        -403: 'Ошибка при актуализации',
        -600: 'Запись логически удалена',
        -601: 'Запись физически удалена',
        -602: 'Запись заблокирована на ввод',
        -603: 'Запись логически удалена',
        -605: 'Запись физически удалена',
        -607: 'Ошибка autoin.gbl',
        -608: 'Ошибка версии записи',
        -700: 'Ошибка создания резервной копии',
        -701: 'Ошибка восстановления из резервной копии',
        -702: 'Ошибка сортировки',
        -703: 'Ошибочный термин',
        -704: 'Ошибка создания словаря',
        -705: 'Ошибка загрузки словаря',
        -800: 'Ошибка в параметрах глобальной корректировки',
        -801: 'ERR_GBL_REP',
        -801: 'ERR_GBL_MET',
        -1111: 'Ошибка исполнения сервера (SERVER_EXECUTE_ERROR)',
        -2222: 'Ошибка в протоколе (WRONG_PROTOCOL)',
        -3333: 'Незарегистрированный клиент (ошибка входа на сервер) (клиент не в списке)',
        -3334: 'Клиент не выполнил вход на сервер (клиент не используется)',
        -3335: 'Неправильный уникальный идентификатор клиента',
        -3336: 'Нет доступа к командам АРМ',
        -3337: 'Клиент уже зарегистрирован',
        -3338: 'Недопустимый клиент',
        -4444: 'Неверный пароль',
        -5555: 'Файл не существует',
        -6666: 'Сервер перегружен. Достигнуто максимальное число потоков обработки',
        -7777: 'Не удалось запустить/прервать поток администратора (ошибка процесса)',
        -8888: 'Общая ошибка',
    }

    if code >= 0:
        return 'Нормальное завершение'

    if code not in errors:
        return 'Неизвестная ошибка'

    return errors[code]


class IrbisError(Exception):
    """
    Исключнение - ошибка протокола
    """

    __slots__ = 'code'

    def __init__(self, code: int = 0) -> None:
        self.code = code

    def __str__(self):
        return f'{self.code}: {get_error_description(self.code)}'


###############################################################################

# Client query


class ClientQuery:
    """
    Клиентский запрос.
    """

    __slots__ = ('_memory',)

    def __init__(self, connection, command: str) -> None:
        self._memory = bytearray()
        self.ansi(command)
        self.ansi(connection.workstation)
        self.ansi(command)
        self.add(connection.client_id)
        self.add(connection.query_id)
        connection.query_id += 1
        self.ansi(connection.password)
        self.ansi(connection.username)
        self.new_line()
        self.new_line()
        self.new_line()

    def add(self, number: int):
        """
        Добавление целого числа.

        :param number: Число
        :return: Self
        """
        return self.ansi(str(number))

    def ansi(self, text: Optional[str]):
        """
        Добавление строки в кодировке ANSI.

        :param text: Добавляемая строка
        :return: Self
        """
        return self.append(text, ANSI)

    def append(self, text: Optional[str], encoding: str):
        """
        Добавление строки в указанной кодировке.

        :param text: Добавляемая строка
        :param encoding: Кодировка
        :return: Self
        """
        if text is not None:
            self._memory.extend(text.encode(encoding))
        self.new_line()
        return self

    def new_line(self):
        """
        Перевод строки.

        :return: Self
        """
        self._memory.append(0x0A)
        return self

    def utf(self, text: Optional[str]):
        """
        Добавление строки в кодировке UTF-8.

        :param text: Добавляемая строка
        :return: Self
        """
        return self.append(text, UTF)

    def encode(self):
        """
        Выдача, что получилось в итоге.

        :return: Закодированный запрос
        """
        prefix = (str(len(self._memory)) + '\n').encode(ANSI)
        return prefix + self._memory


###############################################################################

# File specification


class FileSpecification:
    """
    Путь на файл path.database.filename
    path – код путей:
    0 – общесистемный путь.
    1 – путь размещения сведений о базах данных сервера ИРБИС64
    2 – путь на мастер-файл базы данных.
    3 – путь на словарь базы данных.
    10 – путь на параметрию базы данных.
    database – имя базы данных
    filename – имя требуемого файла с расширением
    В случае чтения ресурса по пути 0 и 1 имя базы данных не задается.
    """

    __slots__ = 'binary', 'path', 'database', 'filename', 'content'

    def __init__(self, path: int, database: Optional[str], filename: str) -> None:
        self.binary: bool = False
        self.path: int = path
        self.database: Optional[str] = database
        self.filename: str = filename
        self.content: Optional[str] = None

    @staticmethod
    def system(filename: str):
        """
        Создание спецификации файла, лежащего в системной папке ИРБИС64.

        :param filename: Имя файла
        :return: Спецификация файла
        """
        return FileSpecification(SYSTEM, None, filename)

    @staticmethod
    def parse(text: str):
        """
        Разбор текстового представления спецификации.

        :param text: Текст
        :return: Спецификация
        """
        # TODO учитывать @ и &

        parts = text.split('.', 2)
        result = FileSpecification(int(parts[0]), parts[1], parts[2])
        return result

    def __str__(self):
        result = self.filename

        if self.binary:
            result = '@' + self.filename
        else:
            if self.content:
                result = '&' + self.filename

        if self.path == 0 or self.path == 1:
            result = str(self.path) + '..' + result
        else:
            result = str(self.path) + '.' + self.database + '.' + result

        if self.content:
            result = result + '&' + str(self.content)

        return result


###############################################################################

# Server response


class ServerResponse:
    """
    Ответ сервера.
    """

    __slots__ = '_memory', 'command', 'client_id', 'query_id', 'length', 'version', 'return_code'

    def __init__(self, sock: socket.socket) -> None:
        self._memory: bytearray = bytearray()
        while sock:
            buffer = sock.recv(4096)
            if not buffer:
                break
            self._memory.extend(buffer)
        sock.close()
        self.command: str = self.ansi()
        self.client_id: int = self.number()
        self.query_id: int = self.number()
        self.length: int = self.may_be_number()
        self.version: str = self.ansi()
        self.return_code: int = 0
        for i in range(5):
            self.read()

    def ansi(self) -> str:
        return self.read().decode(ANSI)

    def ansi_n(self, count: int) -> List[str]:
        """
        Считывание не менее указанного количества строк.

        :param count: Сколько строк надо
        :return: Список строк или None
        """
        result = []
        for i in range(count):
            line = self.ansi()
            if len(line) == 0:
                return []
            result.append(line)
        return result

    def ansi_remaining_text(self) -> str:
        return self._memory.decode(ANSI)

    def ansi_remaining_lines(self):
        result = []
        while True:
            line = self.ansi()
            if len(line) == 0:
                break
            result.append(line)
        return result

    def check_return_code(self, allowed=None):
        if allowed is None:
            allowed = []

        if self.get_return_code() < 0:
            if self.return_code not in allowed:
                raise IrbisError(self.return_code)

    def close(self) -> None:
        # Пока ничего не делаем
        pass

    def get_binary_file(self) -> Optional[bytearray]:
        preamble = bytearray(b'IRBIS_BINARY_DATA')
        index = self._memory.find(preamble)
        if index < 0:
            return None
        return self._memory[index + len(preamble):]

    def get_return_code(self) -> int:
        self.return_code = self.number()
        return self.return_code

    def nop(self):
        pass

    def may_be_number(self) -> int:
        result = 0
        try:
            result = int(self.ansi())
        except ValueError:
            pass
        return result

    def number(self) -> int:
        return int(self.ansi())

    def read(self) -> bytearray:
        """
        Считываем строку в сыром виде.

        :return: Считанная строка.
        """
        result = bytearray()
        while True:
            if not len(self._memory):
                break
            c = self._memory.pop(0)
            if c == 0x0D:
                if not len(self._memory):
                    break
                c = self._memory.pop(0)
                if c == 0x0A:
                    break
            result.append(c)
        return result

    def utf(self) -> str:
        return self.read().decode(UTF)

    def utf_n(self, count: int) -> List[str]:
        """
        Считывание не менее указанного количества строк.

        :param count: Сколько строк надо
        :return: Список строк или None
        """
        result = []
        for i in range(count):
            line = self.utf()
            if len(line) == 0:
                return []
            result.append(line)
        return result

    def utf_remaining_text(self) -> str:
        return self._memory.decode(UTF)

    def utf_remaining_lines(self):
        result = []
        while True:
            line = self.utf()
            if len(line) == 0:
                break
            result.append(line)
        return result

    def __str__(self):
        return str(self.return_code)

    def __enter__(self):
        # Пока не знаю, что делать
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return exc_type is None

###############################################################################

# Parameters for search request


class SearchParameters:
    """
    Параметры поискового запроса.
    """

    __slots__ = ('database', 'first', 'format', 'max_mfn', 'min_mfn',
                 'number', 'expression', 'sequential', 'filter', 'utf')

    def __init__(self, expression: Optional[str] = None, number: int = 0) -> None:
        self.database: Optional[str] = None
        self.first: int = 1
        self.format: Optional[str] = None
        self.max_mfn: int = 0
        self.min_mfn: int = 0
        self.number: int = number
        self.expression = expression
        self.sequential: Optional[str] = None
        self.filter: Optional[str] = None
        self.utf = False

    def __str__(self):
        return self.expression


###############################################################################

# MARC record subfield


class SubField:
    """
    Подполе с кодом и значением.
    """

    DEFAULT_CODE = '\0'

    __slots__ = 'code', 'value'

    def __init__(self, code: str = DEFAULT_CODE, value: Optional[str] = None) -> None:
        code = code or SubField.DEFAULT_CODE
        self.code: str = code.lower()
        self.value: Optional[str] = value

    def assign_from(self, other):
        self.code = other.code
        self.value = other.value

    def clone(self):
        return SubField(self.code, self.value)

    def __str__(self):
        if self.code == self.DEFAULT_CODE:
            return ''
        return '^' + self.code + (self.value or '')

    def __repr__(self):
        return self.__str__()

    def __bool__(self):
        return self.code != self.DEFAULT_CODE and bool(self.value)

###############################################################################

# MARC record field


class RecordField:
    """
    Поле с тегом, значением (до первого разделителя) и подполями.
    """

    DEFAULT_TAG = 0

    __slots__ = 'tag', 'value', 'subfields'

    def __init__(self, tag: Optional[int] = DEFAULT_TAG,
                 value: Union[SubField, str] = None,
                 *subfields: SubField) -> None:
        self.tag: int = tag or self.DEFAULT_TAG
        self.value: Optional[str] = None
        if isinstance(value, str):
            self.value = value
        self.subfields: List[SubField] = []
        if isinstance(value, SubField):
            self.subfields.append(value)
        self.subfields.extend(subfields)

    def add(self, code: str, value: str = ''):
        self.subfields.append(SubField(code, value))
        return self

    def all(self, code: str) -> List[SubField]:
        code = code.lower()
        return [sf for sf in self.subfields if sf.code == code]

    def all_values(self, code: str) -> List[str]:
        code = code.lower()
        return [sf.value for sf in self.subfields if sf.code == code if sf.value]

    def assign_from(self, other):
        self.value = other.value
        self.subfields = [sf.clone() for sf in other.subfields]

    def clear(self):
        self.value = None
        self.subfields = []
        return self

    def clone(self):
        result = RecordField(self.tag, self.value)
        for sf in self.subfields:
            result.subfields.append(sf.clone())
        return result

    def first(self, code: str) -> Optional[SubField]:
        """
        Находит первое подполе с указанным кодом.
        :param code: Код
        :return: Подполе или None
        """
        code = code.lower()
        for subfield in self.subfields:
            if subfield.code == code:
                return subfield
        return None

    def first_value(self, code: str) -> Optional[str]:
        """
        Находит первое подполе с указанным кодом.
        :param code: Код
        :return: Значение подполя или None
        """
        code = code.lower()
        for subfield in self.subfields:
            if subfield.code == code:
                return subfield.value
        return None

    def parse(self, line: str) -> None:
        if '#' not in line:
            if '^' not in line:
                self.value = line
            else:
                if line[0] != '^':
                    parts = line.split('^', 1)
                    self.value = parts[0]
                    parts = parts[1].split('^')
                else:
                    parts = line.split('^')
                for x in parts:
                    if x:
                        sub = SubField(x[:1], x[1:])
                        self.subfields.append(sub)
        else:
            parts = line.split('#', 1)
            self.tag = int(parts[0])
            if '^' not in parts[1]:
                self.value = parts[1]
            else:
                if parts[1][0] != '^':
                    parts = parts[1].split('^', 1)
                    self.value = parts[0]
                    parts = parts[1].split('^')
                else:
                    parts = parts[1].split('^')
                for x in parts:
                    if x:
                        sub = SubField(x[:1], x[1:])
                        self.subfields.append(sub)

    def __str__(self):
        if not self.tag:
            return ''
        buffer = [str(self.tag), '#', self.value or ''] + [str(sf) for sf in self.subfields]
        return ''.join(buffer)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        yield from self.subfields

    def __iadd__(self, other: Union[SubField, Iterable[SubField]]):
        if isinstance(other, SubField):
            self.subfields.append(other)
        else:
            self.subfields.extend(other)
        return self

    def __isub__(self, other: Union[SubField, Iterable[SubField]]):
        if isinstance(other, SubField):
            if other in self.subfields:
                self.subfields.remove(other)
        else:
            for one in other:
                if one in self.subfields:
                    self.subfields.remove(one)
        return self

    def __getitem__(self, item: Union[str, int]):
        if isinstance(item, int):
            return self.subfields[item]
        return self.first(item)

    def __setitem__(self, key: Union[str, int], value: Optional[str]):
        if isinstance(key, int):
            if value:
                self.subfields[key].value = value
            else:
                self.subfields.pop(key)
        else:
            found = self.first(key)
            if value:
                if found:
                    found.value = value
                else:
                    found = SubField(key, value)
                    self.subfields.append(found)
            else:
                if found:
                    self.subfields.remove(found)

    def __len__(self):
        return len(self.subfields)

    def __bool__(self):
        return bool(self.tag) and bool(self.value) or bool(self.subfields)

###############################################################################

# MARC record


class MarcRecord:
    """
    Запись с MFN, статусом, версией и полями.
    """

    __slots__ = 'database', 'mfn', 'version', 'status', 'fields'

    def __init__(self, *fields: RecordField):
        self.database: str = None
        self.mfn: int = 0
        self.version: int = 0
        self.status: int = 0
        self.fields: [RecordField] = []
        self.fields.extend(fields)

    def add(self, tag: int, value: Union[str, SubField] = None,
            *subfields: SubField):
        if isinstance(value, str):
            field = RecordField(tag, value)
        else:
            field = RecordField(tag)
            if isinstance(value, SubField):
                field.subfields.append(value)
        field.subfields.extend(subfields)
        self.fields.append(field)
        return self

    def all(self, tag: int) -> List[RecordField]:
        return [f for f in self.fields if f.tag == tag]

    def clear(self):
        self.fields.clear()
        return self

    def clone(self):
        result = MarcRecord()
        result.database = self.database
        result.mfn = self.mfn
        result.status = self.status
        result.version = self.version
        result.fields = [field.clone() for field in self.fields]
        return result

    def encode(self) -> List[str]:
        result = [str(self.mfn) + '#' + str(self.status),
                  '0#' + str(self.version)]
        for field in self.fields:
            result.append(str(field))
        return result

    def fm(self, tag: int, code: str = '') -> Optional[str]:
        """
        Текст первого поля с указанным тегом.
        :param tag: Тег
        :param code: Значение (опционально)
        :return: Текст или None
        """
        for field in self.fields:
            if field.tag == tag:
                if code:
                    return field.first_value(code)
                else:
                    return field.value
        return None

    def fma(self, tag: int, code: str = '') -> List[str]:
        result = []
        for field in self.fields:
            if field.tag == tag:
                if code:
                    one = field.first_value(code)
                    if one:
                        result.append(one)
                else:
                    one = field.value
                    if one:
                        result.append(one)
        return result

    def first(self, tag: int) -> Optional[RecordField]:
        for field in self.fields:
            if field.tag == tag:
                return field
        return None

    def is_deleted(self) -> bool:
        """
        Удалена ли запись?
        :return: True для удаленной записи
        """
        return (self.status & (LOGICALLY_DELETED | PHYSICALLY_DELETED)) != 0

    def parse(self, text: List[str]) -> None:
        if not text:
            return
        line = text[0]
        parts = line.split('#')
        self.mfn = int(parts[0])
        if len(parts) != 1 and parts[1]:
            self.status = int(parts[1])
        line = text[1]
        parts = line.split('#')
        self.version = int(parts[1])
        self.fields.clear()
        for line in text[2:]:
            field = RecordField()
            field.parse(line)
            self.fields.append(field)

    def __str__(self):
        result = [str(field) for field in self.fields]
        return '\n'.join(result)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        yield from self.fields

    def __iadd__(self, other: Union[RecordField, Iterable[RecordField]]):
        if isinstance(other, RecordField):
            self.fields.append(other)
        else:
            self.fields.extend(other)
        return self

    def __isub__(self, other: Union[RecordField, Iterable[RecordField]]):
        if isinstance(other, RecordField):
            if other in self.fields:
                self.fields.remove(other)
        else:
            for one in other:
                if one in self.fields:
                    self.fields.remove(one)
        return self

    def __getitem__(self, item: int):
        return self.fm(item)

    def __setitem__(self, key: int, value: Union[RecordField, SubField, str, None]):
        if value is None:
            found: List[RecordField] = self.all(key)
            for fld in found:
                self.fields.remove(fld)
            return

        field: Optional[RecordField] = self.first(key)
        if isinstance(value, str):
            if field is None:
                field = RecordField(key, value)
                self.fields.append(field)
            else:
                field.clear()
                # TODO need headless_parse() method
                field.parse(value)

        if isinstance(value, RecordField):
            if field is None:
                field = RecordField(key)
                self.fields.append(field)
            field.assign_from(value)

        if isinstance(value, SubField):
            if field is None:
                field = RecordField(key)
                self.fields.append(field)
            field.clear()
            field.subfields.append(value)

    def __len__(self):
        return len(self.fields)

    def __bool__(self):
        return bool(len(self.fields))

###############################################################################

# Server version


class IrbisVersion:
    """
    Информация о версии сервера, числе подключенных/разрешенных клиентов
    и организации, на которую зарегистрирован сервер.
    """

    def __init__(self):
        self.organization = ''
        self.version = ''
        self.max_clients = 0
        self.connected_clients = 0

    def parse(self, lines: List[str]):
        if len(lines) == 3:
            self.version = lines[0]
            self.connected_clients = int(lines[1])
            self.max_clients = int(lines[2])
        else:
            self.organization = lines[0]
            self.version = lines[1]
            self.connected_clients = int(lines[2])
            self.max_clients = int(lines[3])

    def __str__(self):
        buffer = [self.organization, self.version, str(self.connected_clients), str(self.max_clients)]
        return '\n'.join(buffer)

###############################################################################


class IniLine:
    """
    Строка INI-файла
    """

    __slots__ = 'key', 'value'

    def __init__(self, key: Optional[str] = None, value: Optional[str] = None) -> None:
        self.key = key
        self.value = value

    def __str__(self):
        return str(self.key) + '=' + str(self.value)

    def __repr__(self):
        return self.__str__()


def same_key(first: Optional[str], second: Optional[str]) -> bool:
    if not first or not second:
        return False
    return first.upper() == second.upper()


class IniSection:
    """
    Секция INI-файла.
    """

    __slots__ = 'name', 'lines'

    def __init__(self, name: Optional[str] = None) -> None:
        self.name: Optional[str] = name
        self.lines: List[IniLine] = []

    def find(self, key: str) -> Optional[IniLine]:
        for line in self.lines:
            if same_key(line.key, key):
                return line
        return None

    def get_value(self, key: str, default: Optional[str] = None) -> Optional[str]:
        found = self.find(key)
        return found.value if found else default

    def set_value(self, key: str, value: str) -> None:
        found = self.find(key)
        if found:
            found.value = value
        else:
            found = IniLine(key, value)
            self.lines.append(found)

    def remove(self, key: str) -> None:
        found = self.find(key)
        if found:
            self.lines.remove(found)

    def __str__(self):
        result = []
        if self.name:
            result.append('[' + self.name + ']')
        for line in self.lines:
            result.append(str(line))
        return '\n'.join(result)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        yield from self.lines

    def __getitem__(self, item: Union[str, int]):
        if isinstance(item, int):
            return self.lines[item]
        return self.get_value(item)

    def __len__(self):
        return len(self.lines)

    def __bool__(self):
        return bool(len(self.lines))


class IniFile:
    """
    INI-файл.
    """

    __slots__ = 'sections'

    def __init__(self):
        self.sections = []

    def find(self, name: str) -> Optional[IniSection]:
        for section in self.sections:
            if not name and not section.name:
                return section
            if same_key(section.name, name):
                return section
        return None

    def get_or_create(self, name: str) -> IniSection:
        result = self.find(name)
        if not result:
            result = IniSection(name)
            self.sections.append(result)
        return result

    def get_value(self, name: str, key: str, default: Optional[str] = None) -> Optional[str]:
        section = self.find(name)
        if section:
            return section.get_value(key, default)
        return default

    def set_value(self, name: str, key: str, value: str) -> None:
        section = self.get_or_create(name)
        if not section:
            section = IniSection(name)
            self.sections.append(section)
        section.set_value(key, value)

    def parse(self, text: List[str]) -> None:
        section = None
        for line in text:
            line = line.strip()
            if not line:
                continue
            if line.startswith('['):
                line = line[1:-1]
                section = IniSection(line)
                self.sections.append(section)
            else:
                parts = line.split('=', 1)
                key = parts[0]
                value = None
                if len(parts) > 1:
                    value = parts[1]
                item = IniLine(key, value)
                if section is None:
                    section = IniSection()
                    self.sections.append(section)
                section.lines.append(item)

    def __str__(self):
        result = []
        for section in self.sections:
            result.append(str(section))
        return '\n'.join(result)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        yield from self.sections

    def __getitem__(self, item: Union[str, int]):
        if isinstance(item, int):
            return self.sections[item]
        return self.find(item)

    def __len__(self):
        return len(self.sections)

    def __bool__(self):
        return bool(len(self.sections))

###############################################################################


class ServerProcess:
    """
    Информация о запущенном на сервере процессе.
    """

    __slots__ = ('number', 'ip', 'name', 'client_id', 'workstation',
                 'started', 'last_command', 'command_number',
                 'process_id', 'state')

    def __init__(self) -> None:
        self.number: str = ''
        self.ip: str = ''
        self.name: str = ''
        self.client_id: str = ''
        self.workstation: str = ''
        self.started: str = ''
        self.last_command: str = ''
        self.command_number: str = ''
        self.process_id: str = ''
        self.state: str = ''

    def __str__(self):
        buffer = [self.number, self.ip, self.name, self.client_id,
                  self.workstation, self.started, self.last_command,
                  self.command_number, self.process_id, self.state]
        return '\n'.join(x for x in buffer if x)


def parse_process_list(response: ServerResponse) -> List[ServerProcess]:
    result: List[ServerProcess] = []
    process_count = response.number()
    lines_per_process = response.number()
    if not process_count or not lines_per_process:
        return result
    for i in range(process_count):
        process = ServerProcess()
        process.number = response.ansi()
        process.ip = response.ansi()
        process.name = response.ansi()
        process.client_id = response.ansi()
        process.workstation = response.ansi()
        process.started = response.ansi()
        process.last_command = response.ansi()
        process.command_number = response.ansi()
        process.process_id = response.ansi()
        process.state = response.ansi()
        result.append(process)
    return result

###############################################################################

# Подключение к серверу


class IrbisConnection:
    """
    Подключение к серверу
    """

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 6666
    DEFAULT_DATABASE = 'IBIS'

    __slots__ = ('host', 'port', 'username', 'password', 'database', 'workstation',
                 'client_id', 'query_id', 'connected', '_stack', 'server_version',
                 'ini_file')

    def __init__(self, host: Optional[str] = None,
                 port: int = 0,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 database: Optional[str] = None,
                 workstation: str = 'C') -> None:
        self.host: str = host or IrbisConnection.DEFAULT_HOST
        self.port: int = port or IrbisConnection.DEFAULT_PORT
        self.username: Optional[str] = username
        self.password: Optional[str] = password
        self.database: str = database or IrbisConnection.DEFAULT_DATABASE
        self.workstation: str = workstation
        self.client_id: int = 0
        self.query_id: int = 0
        self.connected: bool = False
        self._stack: List[str] = []
        self.server_version: Optional[str] = None
        self.ini_file: IniFile = IniFile()

    def actualize_record(self, mfn: int, database: Optional[str] = None) -> None:
        """
        Актуализация записи с указанным MFN.

        :param mfn: MFN записи
        :param database: База данных
        :return: None
        """

        database = database or self.database or throw_value_error()

        assert isinstance(mfn, int)
        assert isinstance(database, str)

        query = ClientQuery(self, ACTUALIZE_RECORD).ansi(database).add(mfn)
        with self.execute(query) as response:
            response.check_return_code()

    def connect(self, host: Optional[str] = None,
                port: int = 0,
                username: Optional[str] = None,
                password: Optional[str] = None,
                database: Optional[str] = None) -> IniFile:
        """
        Подключение к серверу ИРБИС64.

        :return: INI-файл
        """
        if self.connected:
            return self.ini_file

        self.host = host or self.host or throw_value_error()
        self.port = port or self.port or int(throw_value_error())
        self.username = username or self.username or throw_value_error()
        self.password = password or self.password or throw_value_error()
        self.database = database or self.database or throw_value_error()

        assert isinstance(self.host, str)
        assert isinstance(self.port, int)
        assert isinstance(self.username, str)
        assert isinstance(self.password, str)

        # TODO Handle -3337

        self.query_id = 0
        self.client_id = random.randint(100000, 999999)
        query = ClientQuery(self, REGISTER_CLIENT).ansi(self.username).ansi(self.password)
        with self.execute(query) as response:
            response.check_return_code()
            self.server_version = response.version
            result = IniFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            line = text[0]
            text = line.splitlines()
            text = text[1:]
            result.parse(text)
            self.connected = True
            self.ini_file = result
            return result

    def create_database(self, database: Optional[str] = None,
                        description: Optional[str] = None,
                        reader_access: bool = True) -> None:
        """
        Создание базы данных.

        :param database: Имя создаваемой базы
        :param description: Описание в свободной форме
        :param reader_access: Читатель будет иметь доступ?
        :return: None
        """

        database = database or self.database or throw_value_error()
        description = description or ''

        assert isinstance(database, str)
        assert isinstance(description, str)

        query = ClientQuery(self, CREATE_DATABASE)
        query.ansi(database).ansi(description).add(int(reader_access))
        with self.execute(query) as response:
            response.check_return_code()

    def create_dictionary(self, database: Optional[str] = None) -> None:
        """
        Создание словаря в базе данных.

        :param database: База данных
        :return: None
        """

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        query = ClientQuery(self, CREATE_DICTIONARY).ansi(database)
        with self.execute(query) as response:
            response.check_return_code()

    def delete_database(self, database: Optional[str] = None) -> None:
        """
        Удаление базы данных.

        :param database: Имя удаляемой базы
        :return: None
        """

        assert isinstance(database, str)

        database = database or self.database or throw_value_error()
        query = ClientQuery(self, DELETE_DATABASE).ansi(database)
        with self.execute(query) as response:
            response.check_return_code()

    def delete_record(self, mfn: int) -> None:
        """
        Удаление записи по ее MFN.

        :param mfn: MFN удаляемой записи
        :return: None
        """

        assert mfn
        assert isinstance(mfn, int)

        record = self.read_record(mfn)
        if not record.is_deleted():
            record.status |= LOGICALLY_DELETED
            self.write_record(record, dont_parse=True)

    def disconnect(self) -> None:
        """
        Отключение от сервера.

        :return: None
        """

        if not self.connected:
            return

        query = ClientQuery(self, UNREGISTER_CLIENT)
        query.ansi(self.username)
        self.execute_forget(query)
        self.connected = False

    def execute(self, query: ClientQuery) -> ServerResponse:
        """
        Выполнение произвольного запроса к серверу.

        :param query: Запрос
        :return: Ответ сервера (не забыть закрыть!)
        """
        sock = socket.socket()
        sock.connect((self.host, self.port))
        packet = query.encode()
        sock.send(packet)
        return ServerResponse(sock)

    def execute_ansi(self, *commands) -> ServerResponse:
        """
        Простой запрос к серверу, когда все строки запроса
        в кодировке ANSI.

        :param commands: Команда и параметры запроса
        :return: Ответ сервера (не забыть закрыть!)
        """
        query = ClientQuery(self, commands[0])
        for x in commands[1:]:
            query.ansi(x)
        return self.execute(query)

    def execute_forget(self, query: ClientQuery) -> None:
        """
        Выполнение запроса к серверу, когда нам не важен результат
        (мы не собираемся его парсить).

        :param query: Клиентский запрос
        :return: None
        """
        with self.execute(query):
            pass

    def format_record(self, script: str, record: Union[MarcRecord, int],
                      use_utf: bool = False) -> str:
        """
        Форматирование записи с указанным MFN.

        :param script: Текст формата
        :param record: MFN записи либо сама запись
        :param use_utf: Формат содержит символы, не входящие в ANSI
        :return: Результат расформатирования
        """

        script = script or throw_value_error()
        if not record:
            raise ValueError()

        assert isinstance(script, str)
        assert isinstance(record, MarcRecord) or isinstance(record, int)

        script = prepare_format(script)
        if not script:
            return ''

        query = ClientQuery(self, FORMAT_RECORD).ansi(self.database)

        if use_utf:
            query.utf('!' + script)
        else:
            query.ansi(script)

        if isinstance(record, int):
            query.add(1).add(record)
        else:
            query.add(-2).utf(IRBIS_DELIMITER.join(record.encode()))

        with self.execute(query) as response:
            response.check_return_code()
            result = response.utf_remaining_text().strip('\r\n')
            return result

    def format_records(self, script: str, records: List[int], use_utf: bool = False) -> List[str]:
        """
        Форматирование группы записей по MFN.

        :param script: Текст формата
        :param records: Список MFN
        :param use_utf: Формат содержит символы, не входяшие в ANSI
        :return: Список строк
        """

        if not records:
            return []

        script = script or throw_value_error()

        assert isinstance(script, str)
        assert isinstance(records, list)

        script = prepare_format(script)
        if not script:
            return [''] * len(records)

        # TODO support long list of records

        if len(records) > MAX_POSTINGS:
            raise IrbisError()

        query = ClientQuery(self, FORMAT_RECORD).ansi(self.database)

        if use_utf:
            query.utf('!' + script)
        else:
            query.ansi(script)

        query.add(len(records))
        for mfn in records:
            query.add(mfn)

        with self.execute(query) as response:
            response.check_return_code()
            result = response.utf_remaining_lines()
            result = [line.split('#', 1)[1] for line in result]
            return result

    def get_max_mfn(self, database: Optional[str] = None) -> int:
        """
        Получение максимального MFN для указанной базы данных.

        :param database: База данных
        :return: MFN, который будет присвоен следующей записи
        """

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        with self.execute_ansi(GET_MAX_MFN, database) as response:
            response.check_return_code()
            result = response.return_code
            return result

    def get_server_version(self) -> IrbisVersion:
        """
        Получение версии сервера.

        :return: Версия сервера
        """

        query = ClientQuery(self, SERVER_INFO)
        with self.execute(query) as response:
            response.check_return_code()
            lines = response.ansi_remaining_lines()
            result = IrbisVersion()
            result.parse(lines)
            if not self.server_version:
                self.server_version = result.version
            return result

    def list_files(self, *specification: Union[FileSpecification, str]) -> List[str]:
        """
        Получение списка файлов с сервера.

        :param specification: Спецификация или маска имени файла (если нужны файлы, лежащие в папке текущей базы данных)
        :return: Список файлов
        """
        query = ClientQuery(self, LIST_FILES)

        ok = False
        for spec in specification:
            if isinstance(spec, str):
                spec = self.near_master(spec)
            query.ansi(str(spec))
            ok = True

        result: List[str] = []
        if not ok:
            return result

        with self.execute(query) as response:
            lines = response.ansi_remaining_lines()
            lines = [line for line in lines if line]
            for line in lines:
                result.extend(one for one in irbis_to_lines(line) if one)
        return result

    def list_processes(self) -> List[ServerProcess]:
        """
        Получение списка серверных процессов.

        :return: Список процессов
        """

        query = ClientQuery(self, GET_PROCESS_LIST)
        with self.execute(query) as response:
            response.check_return_code()
            result = parse_process_list(response)
            return result

    def monitor_operation(self, operation: str) -> str:
        import time
        client_id = str(self.client_id)
        while True:
            processes = self.list_processes()
            found = False
            for process in processes:
                if process.client_id == client_id and process.last_command == operation:
                    found = True
                    break
            if not found:
                break
            time.sleep(1)
        filename = str(self.client_id) + '.ibf'
        spec = FileSpecification.system(filename)
        result = self.read_text_file(spec)
        return result

    def near_master(self, filename: str) -> FileSpecification:
        return FileSpecification(MASTER_FILE, self.database, filename)

    def nop(self) -> None:
        """
        Пустая операция (используется для периодического
        подтверждения подключения клиента).

        :return: None
        """
        with self.execute_ansi(NOP):
            pass

    def parse_connection_string(self, text: str) -> None:
        """
        Разбор строки подключения.

        :param text: Строка подключения
        :return: None
        """

        for item in text.split(';'):
            if not item:
                continue
            parts = item.split('=', 1)
            name = parts[0].strip().lower()
            value = parts[1].strip()

            if name in ['host', 'server', 'address']:
                self.host = value

            if name == 'port':
                self.port = int(value)

            if name in ['user', 'username', 'name', 'login']:
                self.username = value

            if name in ['pwd', 'password']:
                self.password = value

            if name in ['db', 'database', 'catalog']:
                self.database = value

            if name in ['arm', 'workstation']:
                self.workstation = value

    def pop_database(self) -> str:
        """
        Восстановление подключения к прошлой базе данных,
        запомненной с помощью push_database.

        :return: Прошлая база данных
        """
        result = self.database
        self.database = self._stack.pop()
        return result

    def push_database(self, database: str) -> str:
        """
        Установка подключения к новой базе данных,
        с запоминанием предыдущей базы.

        :param database: Новая база данных
        :return: Предыдущая база данных
        """

        assert database and isinstance(database, str)

        result = self.database
        self._stack.append(result)
        self.database = database
        return result

    def read_binary_file(self, specification: Union[FileSpecification, str]) -> Optional[bytearray]:
        """
        Чтение двоичного файла с сервера.

        :param specification: Спецификация
        :return: Массив байт или None
        """
        if isinstance(specification, str):
            specification = self.near_master(specification)

        assert isinstance(specification, FileSpecification)

        specification.binary = True
        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        with self.execute(query) as response:
            result = response.get_binary_file()
            return result

    def read_ini_file(self, specification: Union[FileSpecification, str]) -> IniFile:
        """
        Чтение INI-файла с сервера.

        :param specification: Спецификация
        :return: INI-файл
        """

        if isinstance(specification, str):
            specification = self.near_master(specification)

        assert isinstance(specification, FileSpecification)

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        with self.execute(query) as response:
            result = IniFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            result.parse(text)
            return result

    def read_record(self, mfn: int, version: int = 0) -> MarcRecord:
        """
        Чтение записи с указанным MFN с сервера.

        :param mfn: MFN
        :param version: версия
        :return: Прочитанная запись
        """

        mfn = mfn or int(throw_value_error())

        assert isinstance(mfn, int)

        query = ClientQuery(self, READ_RECORD).ansi(self.database).add(mfn)
        if version:
            query.add(version)
        with self.execute(query) as response:
            response.check_return_code(READ_RECORD_CODES)
            text = response.utf_remaining_lines()
            result = MarcRecord()
            result.database = self.database
            result.parse(text)

        if version:
            self.unlock_records([mfn])

        return result

    def read_records(self, *mfns: int) -> List[MarcRecord]:
        """
        Чтение записей с указанными MFN с сервера.

        :param mfns: Перечень MFN
        :return: Список записей
        """

        array = list(mfns)

        if not array:
            return []

        if len(array) == 1:
            return [self.read_record(array[0])]

        lines = self.format_records(ALL, array)
        result = []
        for line in lines:
            parts = line.split(OTHER_DELIMITER)
            if parts:
                parts = [x for x in parts[1:] if x]
                record = MarcRecord()
                record.parse(parts)
                if record:
                    record.database = self.database
                    result.append(record)

        return result

    def read_text_file(self, specification: Union[FileSpecification, str]) -> str:
        """
        Получение текстового файла с сервера в виде потока.

        :param specification: Спецификация или имя файла (если он находится в папке текущей базы данных).
        :return: Текст файла или пустая строка, если файл не найден
        """

        with self.read_text_stream(specification) as response:
            result = response.ansi_remaining_text()
            result = irbis_to_dos(result)
            return result

    def read_text_stream(self, specification: Union[FileSpecification, str]) -> ServerResponse:
        if isinstance(specification, str):
            specification = self.near_master(specification)

        assert isinstance(specification, FileSpecification)

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        result = self.execute(query)
        return result

    def reload_dictionary(self, database: Optional[str] = None) -> None:
        """
        Пересоздание словаря.

        :param database: База данных
        :return: None
        """

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        with self.execute_ansi(RELOAD_DICTIONARY, database):
            pass

    def reload_master_file(self, database: Optional[str] = None) -> None:
        """
        Пересоздание мастер-файла.

        :param database: База данных
        :return: None
        """

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        with self.execute_ansi(RELOAD_MASTER_FILE, database):
            pass

    def restart_server(self) -> None:
        """
        Перезапуск сервера (без утери подключенных клиентов).

        :return: None
        """

        with self.execute_ansi(RESTART_SERVER):
            pass

    def search(self, parameters: Union[SearchParameters, str]) -> List:
        """
        Поиск записей.

        :param parameters: Параметры поиска (либо поисковый запрос)
        :return: Список найденных MFN
        """
        if isinstance(parameters, str):
            parameters = SearchParameters(parameters)

        assert isinstance(parameters, SearchParameters)

        # TODO support formatting
        # TODO support long results

        database = parameters.database or self.database or throw_value_error()
        query = ClientQuery(self, SEARCH)
        query.ansi(database)
        query.utf(parameters.expression)
        query.add(parameters.number)
        query.add(parameters.first)
        query.ansi(parameters.format)
        query.add(parameters.min_mfn)
        query.add(parameters.max_mfn)
        query.ansi(parameters.sequential)
        response = self.execute(query)
        response.check_return_code()
        expected = response.number()
        result = []
        for i in range(expected):
            line = response.ansi()
            mfn = int(line)
            result.append(mfn)
        return result

    def to_connection_string(self) -> str:
        """
        Выдача строки подключения для текущего соединения.

        :return: Строка подключения
        """

        return 'host=' + safe_str(self.host) + \
               ';port=' + str(self.port) + \
               ';username=' + safe_str(self.username) + \
               ';password=' + safe_str(self.password) + \
               ';database=' + safe_str(self.database) + \
               ';workstation=' + safe_str(self.workstation) + ';'

    def truncate_database(self, database: Optional[str] = None) -> None:
        """
        Опустошение базы данных.

        :param database: База данных
        :return: None
        """

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        with self.execute_ansi(EMPTY_DATABASE, database):
            pass

    def unlock_database(self, database: Optional[str] = None) -> None:
        """
        Разблокирование базы данных.

        :param database: Имя базы
        :return: None
        """

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        with self.execute_ansi(UNLOCK_DATABASE, database):
            pass

    def unlock_records(self, records: List[int], database: Optional[str] = None) -> None:
        """
        Разблокирование записей.

        :param records: Список MFN
        :param database: База данных
        :return: None
        """

        if not records:
            return

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        query = ClientQuery(self, UNLOCK_RECORDS).ansi(database)
        for mfn in records:
            query.add(mfn)
        with self.execute(query) as response:
            response.check_return_code()

    def update_ini_file(self, lines: List[str]) -> None:
        """
        Обновление строк серверного INI-файла.

        :param lines: Измененные строки
        :return: None
        """
        if not lines:
            return

        query = ClientQuery(self, UPDATE_INI_FILE)
        for line in lines:
            query.ansi(line)
        self.execute_forget(query)

    def write_record(self, record: MarcRecord,
                     lock: bool = False,
                     actualize: bool = True,
                     dont_parse: bool = False) -> int:
        """
        Сохранение записи на сервере.

        :param record: Запись
        :param lock: Оставить запись заблокированной?
        :param actualize: Актуализировать запись?
        :param dont_parse: Не разбирать ответ сервера?
        :return: Новый максимальный MFN
        """

        database = record.database or self.database or throw_value_error()
        if not record:
            raise ValueError()

        assert isinstance(record, MarcRecord)
        assert isinstance(database, str)

        assert isinstance(record, MarcRecord)
        assert isinstance(database, str)

        query = ClientQuery(self, UPDATE_RECORD).ansi(database).add(int(lock)).add(int(actualize))
        query.utf(IRBIS_DELIMITER.join(record.encode()))
        with self.execute(query) as response:
            response.check_return_code()
            result = response.return_code  # Новый максимальный MFN
            if not dont_parse:
                first_line = response.utf()
                text = short_irbis_to_lines(response.utf())
                text.insert(0, first_line)
                record.database = database
                record.parse(text)
            return result

    def write_text_file(self, *specification: FileSpecification) -> None:
        """
        Сохранение текстового файла на сервере.

        :param specification: Спецификация (включая текст для сохранения)
        :return: None
        """
        query = ClientQuery(self, READ_DOCUMENT)
        ok = False
        for spec in specification:
            assert isinstance(spec, FileSpecification)
            query.ansi(str(spec))
            ok = True
        if not ok:
            return

        with self.execute(query) as response:
            response.check_return_code()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return exc_type is None

    def __bool__(self):
        return self.connected

# Common stuff for pyirbis

import random
import socket
from typing import Union, Optional

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


def throw_value_error() -> None:
    """
    Simple raises ValueError.

    :return: None
    """
    raise ValueError()


def irbis_to_dos(text: str) -> str:
    """
    Convert IRBIS text to MS-DOS text.

    :param text: Text to convert
    :return: Converted text
    """
    return text.replace(IRBIS_DELIMITER, '\n')


def irbis_to_lines(text: str) -> [str]:
    """
    Convert IRBIS text to list of strings.

    :param text: Text to convert
    :return: List of strings
    """
    return text.split(IRBIS_DELIMITER)


def short_irbis_to_lines(text: str) -> [str]:
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

class IrbisError(Exception):
    """
    Исключнение - ошибка протокола
    """

    __slots__ = 'code'

    def __init__(self, code: int = 0):
        self.code = code

    def __str__(self):
        return str(self.code)


###############################################################################

# Client query


class ClientQuery:
    """
    Клиентский запрос.
    """

    def __init__(self, connection, command: str):
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
        :return: Себя
        """
        return self.ansi(str(number))

    def ansi(self, text: str):
        """
        Добавление строки в кодировке ANSI.

        :param text: Добавляемая строка
        :return: Себя
        """
        return self.append(text, ANSI)

    def append(self, text: str, encoding: str):
        """
        Добавление строки в указанной кодировке.

        :param text: Добавляемая строка
        :param encoding: Кодировка
        :return: Себя
        """
        if text is not None:
            self._memory.extend(text.encode(encoding))
        self.new_line()
        return self

    def new_line(self):
        self._memory.append(0x0A)
        return self

    def utf(self, text: str):
        """
        Добавление строки в кодировке UTF-8.

        :param text: Добавляемая строка
        :return: Себя
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

    def __init__(self, path: int, database: Optional[str], filename: str):
        self.binary: bool = False
        self.path: int = path
        self.database: str = database
        self.filename: str = filename
        self.content: str = None

    @staticmethod
    def system(filename: str):
        return FileSpecification(SYSTEM, None, filename)

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

    def __init__(self, sock: socket.socket):
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

    def ansi_n(self, count: int) -> [str]:
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
                raise IOError

    def close(self) -> None:
        # Пока ничего не делаем
        pass

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

    def utf_n(self, count: int) -> [str]:
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

    def __init__(self, expression: Optional[str] = None, number: int = 0):
        self.database: Optional[str] = None
        self.first: int = 1
        self.format: Optional[str] = None
        self.max_mfn: int = 0
        self.min_mfn: int = 0
        self.number: int = number
        self.expression = expression
        self.sequential: str = None
        self.filter: str = None
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

    def __init__(self, code: Optional[str] = DEFAULT_CODE, value: Optional[str] = None):
        self.code: str = code.lower()
        self.value: str = value

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

    def __init__(self, tag: Optional[int] = DEFAULT_TAG, value: Union[SubField, str] = None, *subfields: [SubField]):
        self.tag: int = tag or self.DEFAULT_TAG
        self.value: value = None
        if isinstance(value, str):
            self.value = value
        self.subfields: [SubField] = []
        if isinstance(value, SubField):
            self.subfields.append(value)
        self.subfields.extend(subfields)

    def add(self, code: str, value: str = ''):
        self.subfields.append(SubField(code, value))
        return self

    def all(self, code: str) -> [SubField]:
        code = code.lower()
        return [sf for sf in self.subfields if sf.code == code]

    def all_values(self, code: str) -> [str]:
        code = code.lower()
        return [sf.value for sf in self.subfields if sf.code == code]

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

    def __init__(self):
        self.database: str = None
        self.mfn: int = 0
        self.version: int = 0
        self.status: int = 0
        self.fields: [RecordField] = []

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

    def all(self, tag: int) -> [RecordField]:
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

    def encode(self) -> [str]:
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

    def fma(self, tag: int, code: str = '') -> [str]:
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

    def parse(self, text: [str]) -> None:
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

    def __getitem__(self, item: int):
        return self.fm(item)

    def __setitem__(self, key: int, value: Union[RecordField, SubField, str, None]):
        if value is None:
            found = self.all(key)
            for field in found:
                self.fields.remove(field)
            return

        found = self.first(key)
        if isinstance(value, str):
            if found is None:
                found = RecordField(key, value)
                self.fields.append(found)
            else:
                found.clear()
                found.parse(value)

        if isinstance(value, RecordField):
            if found is None:
                found = RecordField(key)
                self.fields.append(found)
            found.assign_from(value)

        if isinstance(value, SubField):
            if found is None:
                found = RecordField(key)
                self.fields.append(found)
            found.clear()
            found.subfields.append(value)

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

    def parse(self, lines: [str]):
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

    def __init__(self, key: Optional[str] = None, value: Optional[str] = None):
        self.key = key
        self.value = value

    @staticmethod
    def same_key(first: str, second: str) -> bool:
        if not first or not second:
            return False
        return first.upper() == second.upper()

    def __str__(self):
        return str(self.key) + '=' + str(self.value)

    def __repr__(self):
        return self.__str__()


class IniSection:
    """
    Секция INI-файла.
    """

    __slots__ = 'name', 'lines'

    def __init__(self, name: Optional[str] = None):
        self.name: str = name
        self.lines = []

    def find(self, key: str) -> Optional[IniLine]:
        for line in self.lines:
            if IniLine.same_key(line.key, key):
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
            if IniLine.same_key(section.name, name):
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

    def parse(self, text: [str]) -> None:
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

    def __init__(self, host: Optional[str] = DEFAULT_HOST, port: int = DEFAULT_PORT,
                 username: str = '', password: str = '', database: str = DELETE_DATABASE,
                 workstation: str = 'C'):
        self.host: str = host
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.database: str = database
        self.workstation: str = workstation
        self.client_id: int = 0
        self.query_id: int = 0
        self.connected: bool = False
        self._stack = []
        self.server_version: Optional[str] = None
        self.ini_file: Optional[IniFile] = None

    def actualize_record(self, mfn: int, database: Optional[str] = None) -> None:
        """
        Актуализация записи с указанным MFN.

        :param mfn: MFN записи
        :param database: База данных
        :return: None
        """
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, ACTUALIZE_RECORD).ansi(database).add(mfn)
        with self.execute(query) as response:
            response.check_return_code()

    def connect(self, host: Optional[str] = None, port: int = 0,
                username: Optional[str] = None, password: Optional[str] = None,
                database: Optional[str] = None) -> IniFile:
        """
        Подключение к серверу ИРБИС64.

        :return: INI-файл
        """
        if self.connected:
            return self.ini_file

        self.host = host or self.host or throw_value_error()
        self.port = port or self.port or throw_value_error()
        self.username = username or self.username or throw_value_error()
        self.password = password or self.password or throw_value_error()
        self.database = database or self.database or throw_value_error()

        # TODO Handle -3337

        self.query_id = 0
        self.client_id = random.randint(100000, 999999)
        query = ClientQuery(self, REGISTER_CLIENT).ansi(self.username).ansi(self.password)
        with self.execute(query) as response:
            response.check_return_code()
            self.server_version = response.version
            result = IniFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            text = text[0]
            text = text.splitlines()
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
        query = ClientQuery(self, CREATE_DICTIONARY).ansi(database)
        with self.execute(query) as response:
            response.check_return_code()

    def delete_database(self, database: Optional[str] = None) -> None:
        """
        Удаление базы данных.

        :param database: Имя удаляемой базы
        :return: None
        """
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

    def format_record(self, script: str, mfn: int) -> str:
        """
        Форматирование записи с указанным MFN.

        :param script: Текст формата
        :param mfn: MFN записи
        :return: Результат расформатирования
        """
        script = script or throw_value_error()
        mfn = mfn or throw_value_error()
        query = ClientQuery(self, FORMAT_RECORD).ansi(self.database).ansi(script).add(1).add(mfn)
        with self.execute(query) as response:
            response.check_return_code()
            result = response.utf_remaining_text()
            return result

    def get_max_mfn(self, database: Optional[str] = None) -> int:
        """
        Получение максимального MFN для указанной базы данных.

        :param database: База данных
        :return: MFN, который будет присвоен следующей записи
        """
        database = database or self.database or throw_value_error()
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

    def list_files(self, *specification: Union[FileSpecification, str]) -> [str]:
        """
        Получение списка файлов с сервера.

        :param specification: Спецификация или маска имени файла (если нужны файлы, лежащие в папке текущей базы данных)
        :return: Список файлов
        """
        query = ClientQuery(self, LIST_FILES)

        for spec in specification:
            if isinstance(spec, str):
                spec = self.near_master(spec)
            query.ansi(str(spec))

        result = []
        with self.execute(query) as response:
            lines = response.ansi_remaining_lines()
            lines = [line for line in lines if line]
            for line in lines:
                result.extend(one for one in irbis_to_lines(line) if one)
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
        result = self.database
        self._stack.append(result)
        self.database = database
        return result

    def read_ini_file(self, specification: Union[FileSpecification, str]) -> IniFile:
        """
        Чтение INI-файла с сервера.

        :param specification: Спецификация
        :return: INI-файл
        """

        if isinstance(specification, str):
            specification = self.near_master(specification)

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
        mfn = mfn or throw_value_error()
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

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        result = self.execute(query)
        return result

    def reload_dictionary(self, database: str = '') -> None:
        """
        Пересоздание словаря.

        :param database: База данных
        :return: None
        """
        database = database or self.database or throw_value_error()
        with self.execute_ansi(RELOAD_DICTIONARY, database):
            pass

    def reload_master_file(self, database: str = '') -> None:
        """
        Пересоздание мастер-файла.

        :param database: База данных
        :return: None
        """
        database = database or self.database or throw_value_error()
        with self.execute_ansi(RELOAD_MASTER_FILE, database):
            pass

    def restart_server(self) -> None:
        """
        Перезапуск сервера (без утери подключенных клиентов).

        :return: None
        """
        with self.execute_ansi(RESTART_SERVER):
            pass

    def search(self, parameters: Union[SearchParameters, str]) -> []:
        """
        Поиск записей.

        :param parameters: Параметры поиска (либо поисковый запрос)
        :return: Список найденных MFN
        """
        if isinstance(parameters, str):
            parameters = SearchParameters(parameters)

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
        return 'host=' + self.host + ';port=' + str(self.port) \
               + ';username=' + self.username + ';password=' \
               + self.password + ';database=' + self.database \
               + ';workstation=' + self.workstation + ';'

    def truncate_database(self, database: str = '') -> None:
        """
        Опустошение базы данных.

        :param database: База данных
        :return: None
        """
        database = database or self.database or throw_value_error()
        with self.execute_ansi(EMPTY_DATABASE, database):
            pass

    def unlock_database(self, database: Optional[str] = None) -> None:
        """
        Разблокирование базы данных.

        :param database: Имя базы
        :return: None
        """
        database = database or self.database or throw_value_error()
        with self.execute_ansi(UNLOCK_DATABASE, database):
            pass

    def unlock_records(self, records: [int], database: Optional[str] = None) -> None:
        """
        Разблокирование записей.

        :param records: Список MFN
        :param database: База данных
        :return: None
        """
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, UNLOCK_RECORDS).ansi(database)
        for mfn in records:
            query.add(mfn)
        with self.execute(query) as response:
            response.check_return_code()

    def update_ini_file(self, lines: [str]) -> None:
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

    def write_record(self, record: MarcRecord, lock: bool = False,
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

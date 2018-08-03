import re
import socket
from typing import Union, Optional

# Encodings

ANSI = 'cp1251'
UTF = 'utf-8'
OEM = 'cp866'

# Stop marker

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

# Разные полезняшки

# Коды для команды ReadRecord
READ_RECORD_CODES = [-201, -600, -602, -603]

# Коды для команды ReadTerms
READ_TERMS_CODES = [-202, -203, -204]


def throw_value_error() -> None:
    """
    Выдаёт исключение.

    :return: None
    """
    raise ValueError


def irbis_to_dos(text: str) -> str:
    return text.replace(IRBIS_DELIMITER, '\n')


def irbis_to_lines(text: str) -> [str]:
    return text.split(IRBIS_DELIMITER)

###############################################################################


class ClientQuery:
    """
    Клиентский запрос.
    """

    def __init__(self, connection, command: str):
        self._memory = bytearray()
        self.ansi(command)
        self.ansi(connection.workstation)
        self.ansi(command)
        self.add(connection.clientId)
        self.add(connection.queryId)
        connection.queryId += 1
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


class FileSpecification:
    """
    Путь на файл Αpath.Adbn.Afilename
    Αpath – код путей:
    0 – общесистемный путь.
    1 – путь размещения сведений о базах данных сервера ИРБИС64
    2 – путь на мастер-файл базы данных.
    3 – путь на словарь базы данных.
    10 – путь на параметрию базы данных.
    Adbn – имя базы данных
    Afilename – имя требуемого файла с расширением
    В случае чтения ресурса по пути 0 и 1 имя базы данных не задается.
    """

    def __init__(self, path: int, database: Optional[str], filename: str):
        self.binary = False
        self.path = path
        self.database = database
        self.filename = filename
        self.content = ''

    @staticmethod
    def system(filename: str):
        return FileSpecification(SYSTEM, None, filename)

    def __str__(self):
        result = self.filename

        if self.binary:
            result = '@' + self.filename
        else:
            if self.content != '':
                result = '&' + self.filename

        if self.path == 0 or self.path == 1:
            result = str(self.path) + '..' + result
        else:
            result = str(self.path) + '.' + self.database + '.' + result

        if self.content != '':
            result = result + '&' + self.content

        return result


class IrbisFormat:
    """
    Манипуляции с форматами.
    """

    ALL = "&uf('+0')"
    BRIEF = '@brief'
    IBIS = '@ibiskw_h'
    INFORMATIONAL = '@info_w'
    OPTIMIZED = '@'

    @staticmethod
    def remove_comments(text: str):
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

    @staticmethod
    def prepare(text: str):
        text = IrbisFormat.remove_comments(text)
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


class ServerResponse:
    """
    Ответ сервера.
    """

    def __init__(self, sock: socket.socket):
        self._memory = bytearray()
        while sock:
            buffer = sock.recv(4096)
            if not buffer:
                break
            self._memory.extend(buffer)
        sock.close()
        self.command = self.ansi()
        self.clientId = self.number()
        self.queryId = self.number()
        self.return_code = 0
        for i in range(7):
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
        # Пока не знаю, что делать
        return self


# class ProtocolText:
#     """
#     Кодирование записи в протокольное представление.
#     """
#
#     DELIMITER = '\x1F\x1E'
#
#     def __init__(self):
#         self._buffer = []
#
#     def subfield(self, subfield: SubField):
#         self._buffer.append('^' + subfield.code + subfield.value)
#
#     def field(self, field: RecordField):
#         self._buffer.append(str(field.tag) + '#' + field.value)
#         for sf in field.subfields:
#             self.subfield(sf)
#
#     def record(self, record: MarcRecord):
#         self._buffer.append(str(record.mfn) + '#' + str(record.status) + self.DELIMITER)
#         self._buffer.append('0#' + str(record.version) + self.DELIMITER)
#         for field in record.fields:
#             self.field(field)
#             self.DELIMITER
#
#     def __str__(self):
#         return ''.join(self._buffer)


class UserInfo:
    """
    Информация о зарегистрированном пользователе системы
    """

    __slots__ = ('number', 'name', 'password', 'cataloger',
                 'reader', 'circulation', 'acquisitions',
                 'provision', 'administrator')

    def __init__(self):
        self.number: str = ''
        self.name: str = ''
        self.password: str = ''
        self.cataloger: str = ''
        self.reader: str = ''
        self.circulation: str = ''
        self.acquisitions: str = ''
        self.provision: str = ''
        self.administrator: str = ''

    @staticmethod
    def parse(response: ServerResponse) -> []:
        result = []
        user_count = response.number()
        lines_per_user = response.number()
        if not user_count or not lines_per_user:
            return result
        for i in range(user_count):
            user = UserInfo()
            user.number = response.ansi()
            user.name = response.ansi()
            user.password = response.ansi()
            user.cataloger = response.ansi()
            user.reader = response.ansi()
            user.circulation = response.ansi()
            user.acquisitions = response.ansi()
            user.provision = response.ansi()
            user.administrator = response.ansi()
            result.append(user)
        return result

    def __str__(self):
        buffer = [self.number, self.name, self.password, self.cataloger,
                  self.reader, self.circulation, self.acquisitions,
                  self.provision, self.administrator]
        return ' '.join(x for x in buffer if x)


class IrbisProcessInfo:
    """
    Информация о запущенном на сервере процессе.
    """

    __slots__ = ('number', 'ip', 'name', 'client_id', 'workstation',
                 'started', 'last_command', 'command_number',
                 'process_id', 'state')

    @staticmethod
    def parse(response: ServerResponse):
        result = []
        process_count = response.number()
        lines_per_process = response.number()
        if not process_count or not lines_per_process:
            return result
        for i in range(process_count):
            process = IrbisProcessInfo()
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

    def __str__(self):
        buffer = [self.number, self.ip, self.name, self.client_id,
                  self.workstation, self.started, self.last_command,
                  self.command_number, self.process_id, self.state]
        return '\n'.join(x for x in buffer if x)


###############################################################################

# Меню

class MenuEntry:
    """
    Пара строк в меню.
    """

    __slots__ = 'code', 'comment'

    def __init__(self, code: str = '', comment: str = ''):
        self.code = code
        self.comment = comment

    def __str__(self):
        if self.comment:
            return self.code + ' - ' + self.comment
        return self.code

    def __repr__(self):
        return self.__str__()


class MenuFile:
    """
    Файл меню.
    """

    __slots__ = 'entries'

    def __init__(self):
        self.entries: [MenuEntry] = []

    def add(self, code: str, comment: str = ''):
        entry = MenuEntry(code, comment)
        self.entries.append(entry)
        return self

    def get_entry(self, code: str) -> Optional[MenuEntry]:
        code = code.lower()
        for entry in self.entries:
            if entry.code.lower() == code:
                return entry

        code = code.strip()
        for entry in self.entries:
            if entry.code.lower() == code:
                return entry

        code = MenuFile.trim_code(code)
        for entry in self.entries:
            if entry.code.lower() == code:
                return entry

        return None

    def get_value(self, code: str, default_value: Optional[str]=None) -> Optional[str]:
        entry = self.get_entry(code)
        result = entry and entry.comment or default_value
        return result

    def parse(self, response: ServerResponse) -> None:
        text = response.ansi()
        lines = irbis_to_lines(text)
        i = 0
        while i + 1 < len(lines):
            code = lines[i]
            comment = lines[i + 1]
            if code.startswith(STOP_MARKER):
                break
            self.add(code, comment)
            i += 2

    @staticmethod
    def trim_code(code: str) -> str:
        result = code.strip(' -=:')
        return result

    def __str__(self):
        result = []
        for entry in self.entries:
            result.append(entry.code)
            result.append(entry.comment)
        result.append(STOP_MARKER)
        return '\n'.join(result)


###############################################################################

# Оптимизация форматов

WILDCARD = '+'


class OptLine:
    """
    Строка в OPT-файле.
    """

    __slots__ = 'pattern', 'worksheet'

    def __init__(self):
        self.pattern: str = ''
        self.worksheet: str = ''

    def parse(self, text: str) -> None:
        parts = re.split('\s+', text.strip())
        self.pattern = parts[0]
        self.worksheet = parts[1]


class OptFile:
    """
    OPT-файл.
    """

    __slots__ = 'lines', 'length', 'tag'

    def __init__(self):
        self.lines: [OptLine] = []
        self.length: int = 5
        self.tag: int = 920

    def parse(self, text: [str]):
        self.tag = int(text[0])
        self.length = int(text[1])
        for line in text[2:]:
            if not line:
                continue
            line = line.strip()
            if not line:
                continue
            if line.startswith('*'):
                continue
            one = OptLine()
            one.parse(line)
            self.lines.append(one)

    @staticmethod
    def same_char(pattern: str, testable: str) -> bool:
        if pattern == WILDCARD:
            return True
        return pattern.lower() == testable.lower()

    def same_text(self, pattern: str, testable: str) -> bool:
        if not pattern:
            return False
        if not testable:
            return pattern[0] == WILDCARD
        pattern_index = 0
        testable_index = 0

        while True:
            pattern_char = pattern[pattern_index]
            testable_char = testable[testable_index]
            pattern_index += 1
            testable_index += 1
            pattern_next = pattern_index < len(pattern)
            testable_next = testable_index < len(testable)

            if pattern_next and not testable_next:
                if pattern_char == WILDCARD:
                    while pattern_index < len(pattern):
                        pattern_char = pattern[pattern_index]
                        pattern_index += 1
                        if pattern_char != WILDCARD:
                            return False
                    return True

            if pattern_next != testable_next:
                return False
            if not pattern_next:
                return True
            if not self.same_char(pattern_char, testable_char):
                return False

    def resolve_worksheet(self, tag: str) -> Optional[str]:
        for line in self.lines:
            if self.same_text(line.pattern, tag):
                return line.worksheet
        return None

    def __str__(self):
        result = [str(self.tag), str(self.length)]
        for line in self.lines:
            result.append(line.pattern.ljust(6) + line.worksheet)
        result.append(STOP_MARKER)
        return '\n'.join(result)


###############################################################################

# PAR-файл

class ParFile:
    """
    PAR-файл.
    """

    __slots__ = ('xrf', 'mst', 'cnt', 'n01', 'n02', 'l01', 'l02', 'ifp',
                 'any', 'pft', 'ext')

    def __init__(self, mst: str = ''):
        self.xrf: str = mst
        self.mst: str = mst
        self.cnt: str = mst
        self.n01: str = mst
        self.n02: str = mst
        self.l01: str = mst
        self.l02: str = mst
        self.ifp: str = mst
        self.any: str = mst
        self.pft: str = mst
        self.ext: str = mst

    @staticmethod
    def make_dict(text: [str]) -> dict:
        result = dict()
        for line in text:
            if not line:
                continue
            parts = line.split('=', 2)
            if len(parts) < 2:
                continue
            key = parts[0].strip()
            value = parts[1].strip()
            result[key] = value
        return result

    def parse(self, text: [str]) -> None:
        d = ParFile.make_dict(text)
        self.xrf = d['1']
        self.mst = d['2']
        self.cnt = d['3']
        self.n01 = d['4']
        self.n02 = d['5']
        self.l01 = d['6']
        self.l02 = d['7']
        self.ifp = d['8']
        self.any = d['9']
        self.pft = d['10']
        self.ext = d['11']

    def __str__(self):
        result = ['1=' + self.xrf,
                  '2=' + self.mst,
                  '3=' + self.cnt,
                  '4=' + self.n01,
                  '5=' + self.n02,
                  '6=' + self.l01,
                  '7=' + self.l02,
                  '8=' + self.ifp,
                  '9=' + self.any,
                  '10=' + self.pft,
                  '11=' + self.ext]
        return '\n'.join(result)


###############################################################################

# Информация о клиенте

class ClientInfo:
    """
    Информация о клиенте, подключенном к серверу ИРБИС
    (не обязательно о текущем)
    """

    __slots__ = ('number', 'ip', 'port', 'name', 'client_id',
                 'workstation', 'registered', 'acknowledged',
                 'last_command', 'command_number')

    def __init__(self):
        self.number: str = ''
        self.ip: str = ''
        self.port: str = ''
        self.name: str = ''
        self.client_id: str = ''
        self.workstation: str = ''
        self.registered: str = ''
        self.acknowledged: str = ''
        self.last_command: str = ''
        self.command_number: str = ''

    def __str__(self):
        return ' '.join([self.number, self.ip, self.port, self.name,
                         self.client_id, self.workstation,
                         self.registered, self.acknowledged,
                         self.last_command, self.command_number])

    def __repr__(self):
        return self.__str__()

###############################################################################

# Статистика работы ИРБИС-сервера


class ServerStat:
    """
    Статистика работы ИРБИС-сервера
    """

    __slots__ = 'running_clients', 'client_count', 'total_command_count'

    def __init__(self):
        self.running_clients: [ClientInfo] = []
        self.client_count: int = 0
        self.total_command_count: int = 0

    def parse(self, response: ServerResponse) -> None:
        self.total_command_count = response.number()
        self.client_count = response.number()
        lines_per_client = response.number()

        for i in range(self.client_count):
            client = ClientInfo()
            client.number = response.ansi()
            client.ip = response.ansi()
            client.port = response.ansi()
            client.name = response.ansi()
            client.client_id = response.ansi()
            client.workstation = response.ansi()
            client.registered = response.ansi()
            client.acknowledged = response.ansi()
            client.last_command = response.ansi()
            client.command_number = response.ansi()
            self.running_clients.append(client)

    def __str__(self):
        return str(self.client_count) + ', ' + str(self.total_command_count)

###############################################################################

# Информация о базе данных ИРБИС


class DatabaseInfo:
    """
    Информация о базе данных ИРБИС.
    """

    __slots__ = ('name', 'description', 'max_mfn', 'logically_deleted',
                 'physically_deleted', 'nonactualized', 'locked_records',
                 'database_locked', 'read_only')

    def __init__(self, name: Optional[str] = None, description: Optional[str] = None):
        self.name: str = name
        self.description: str = description
        self.max_mfn: int = 0
        self.logically_deleted: [int] = []
        self.physically_deleted: [int] = []
        self.nonactualized: [int] = []
        self.locked_records: [int] = []
        self.database_locked: bool = False
        self.read_only: bool = False

    @staticmethod
    def _parse(line: str) -> [int]:
        if not line:
            return []
        return [int(x) for x in line.split(SHORT_DELIMITER) if x]

    def parse(self, response: ServerResponse) -> None:
        self.logically_deleted = self._parse(response.ansi())
        self.physically_deleted = self._parse(response.ansi())
        self.nonactualized = self._parse(response.ansi())
        self.locked_records = self._parse(response.ansi())
        self.max_mfn = int(response.ansi())
        self.database_locked = bool(int(response.ansi()))

    def __str__(self):
        if not self.description:
            return self.name or '(none)'
        return self.name + ' - ' + self.description


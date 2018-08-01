import socket

# Encodings

ANSI = 'cp1251'
UTF = 'utf-8'
OEM = 'cp866'

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

    def __init__(self, path, database, filename):
        self.binary = False
        self.path = path
        self.database = database
        self.filename = filename
        self.content = ''

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

    def __init__(self):
        self.number = ''
        self.name = ''
        self.password = ''
        self.cataloger = ''
        self.reader = ''
        self.circulation = ''
        self.acquisitions = ''
        self.provision = ''
        self.administrator = ''

    def parse(self, response: ServerResponse):
        pass

    def __str__(self):
        buffer = [self.number, self.name, self.password, self.cataloger,
                  self.reader, self.circulation, self.acquisitions,
                  self.provision, self.administrator]
        return '\n'.join(buffer)


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
        if process_count == 0 or lines_per_process == 0:
            return result
        for i in range(process_count):
            lines = response.ansi_n(lines_per_process + 1)
            if not lines:
                break
            process = IrbisProcessInfo()
            process.number = lines[0]
            process.ip = lines[1]
            process.name = lines[2]
            process.client_id = lines[3]
            process.workstation = lines[4]
            process.started = lines[5]
            process.last_command = lines[6]
            process.command_number = lines[7]
            process.process_id = lines[8]
            process.state = lines[9]
            result.append(process)
        return result

    def __str__(self):
        buffer = [self.number, self.ip, self.name, self.client_id,
                  self.workstation, self.started, self.last_command,
                  self.command_number, self.process_id, self.state]
        return '\n'.join(buffer)


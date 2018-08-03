import random
from typing import Union, Tuple, Optional

from pyirbis.infrastructure import *
from pyirbis.search import *


###############################################################################


# Запись с полями и подполями


class SubField:
    """
    Подполе с кодом и значением.
    """

    __slots__ = "code", "value"

    def __init__(self, code: str = '\0', value: str = ''):
        self.code: str = code.lower()
        self.value: str = value

    def assign_from(self, other):
        self.code = other.code
        self.value = other.value

    def clone(self):
        return SubField(self.code, self.value)

    def __str__(self):
        return '^' + self.code + self.value

    def __repr__(self):
        return '^' + self.code + self.value


class RecordField:
    """
    Поле с тегом, значением (до первого разделителя) и подполями.
    """

    __slots__ = "tag", "value", "subfields"

    def __init__(self, tag: int = 0, value: str = ''):
        self.tag: int = tag
        self.value: value = value
        self.subfields: [SubField] = []

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
        parts = line.split('#', 2)
        self.tag = int(parts[0])
        if '^' not in parts[1]:
            self.value = parts[1]
        else:
            if parts[1][0] != '^':
                parts = parts[1].split('^', 2)
                self.value = parts[0]
                parts = parts[1].split('^')
            else:
                parts = parts[1].split('^')
            for x in parts:
                sub = SubField(x[:1], x[1:])
                self.subfields.append(sub)

    def to_text(self) -> str:
        buffer = [str(self.tag), '#', self.value] + [str(sf) for sf in self.subfields]
        return ''.join(buffer)

    def __str__(self):
        return self.to_text()

    def __repr__(self):
        return self.to_text()


class MarcRecord:
    """
    Запись с MFN, статусом, версией и полями.
    """

    __slots__ = 'database', 'mfn', 'version', 'status', 'fields'

    def __init__(self):
        self.database: str = ''
        self.mfn: int = 0
        self.version: int = 0
        self.status: int = 0
        self.fields: [RecordField] = []

    def add(self, tag: int, value='', *subfields: SubField):
        field = RecordField(tag, value)
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
        for f in self.fields:
            result.fields.append(f.clone())
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

    def to_text(self) -> str:
        result = [str(field) for field in self.fields]
        return '\n'.join(result)

    def __str__(self):
        return self.to_text()

    def __repr__(self):
        return self.to_text()


###############################################################################

# Подключение к серверу

class IrbisConnection:

    def __init__(self):
        self.host = 'localhost'
        self.port = 6666
        self.username = ''
        self.password = ''
        self.database = 'IBIS'
        self.workstation = 'C'
        self.clientId = 0
        self.queryId = 0
        self.connected = False
        self._stack = []

    def actualize_record(self, mfn: int, database: str = '') -> None:
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, ACTUALIZE_RECORD)
        query.ansi(database).add(mfn)
        with self.execute(query) as response:
            response.check_return_code()

    def connect(self):
        """
        Подключение к серверу.

        :return: INI-файл
        """
        if self.connected:
            return

        self.queryId = 0
        self.clientId = random.randint(100000, 900000)
        query = ClientQuery(self, REGISTER_CLIENT)
        query.ansi(self.username)
        query.ansi(self.password)
        with self.execute(query) as response:
            response.check_return_code()
        self.connected = True
        return ''

    def create_database(self, database: Optional[str] = None, description: str = '', reader_access: bool = True) -> None:
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, CREATE_DATABASE)
        query.ansi(database).ansi(description).add(int(reader_access))
        with self.execute(query) as response:
            response.check_return_code()

    def create_dictionary(self, database: Optional[str] = None) -> None:
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, CREATE_DICTIONARY)
        query.ansi(database)
        with self.execute(query) as response:
            response.check_return_code()

    def delete_database(self, database: str = '') -> None:
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, DELETE_DATABASE)
        query.ansi(database)
        with self.execute(query) as response:
            response.check_return_code()

    def disconnect(self) -> None:
        """
        Отключение от сервера.
        """
        if not self.connected:
            return
        query = ClientQuery(self, UNREGISTER_CLIENT)
        query.ansi(self.username)
        self.execute_forget(query)
        self.connected = False

    def execute(self, query: ClientQuery) -> ServerResponse:
        sock = socket.socket()
        sock.connect((self.host, self.port))
        packet = query.encode()
        sock.send(packet)
        return ServerResponse(sock)

    def execute_ansi(self, commands: []) -> ServerResponse:
        query = ClientQuery(self, commands[0])
        for x in commands[1:]:
            query.ansi(x)
        return self.execute(query)

    def execute_forget(self, query: ClientQuery) -> None:
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
        query = ClientQuery(self, FORMAT_RECORD)
        query.ansi(self.database).ansi(script).add(1).add(mfn)
        with self.execute(query) as response:
            response.check_return_code()
            result = response.utf_remaining_text()
            return result

    def get_database_info(self, database: Optional[str] = None) -> DatabaseInfo:
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, RECORD_LIST).ansi(database)
        with self.execute(query) as response:
            response.check_return_code()
            result = DatabaseInfo()
            result.parse(response)
            result.name = database
            return result

    def get_max_mfn(self, database='') -> int:
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, GET_MAX_MFN)
        query.ansi(database)
        with self.execute(query) as response:
            response.check_return_code()
            result = response.return_code
            return result

    def get_server_stat(self) -> ServerStat:
        query = ClientQuery(self, GET_SERVER_STAT)
        with self.execute(query) as response:
            response.check_return_code()
            result = ServerStat()
            result.parse(response)
            return result

    def get_server_version(self) -> IrbisVersion:
        query = ClientQuery(self, SERVER_INFO)
        with self.execute(query) as response:
            response.check_return_code()
            lines = response.ansi_remaining_lines()
            result = IrbisVersion()
            result.parse(lines)
            return result

    def get_user_list(self) -> [UserInfo]:
        query = ClientQuery(self, GET_USER_LIST)
        with self.execute(query) as response:
            response.check_return_code()
            result = UserInfo.parse(response)
            return result

    def list_files(self, specification: FileSpecification) -> [str]:
        query = ClientQuery(self, LIST_FILES)
        query.ansi(str(specification))
        result = []
        with self.execute(query) as response:
            lines = response.ansi_remaining_lines()
            result.extend(lines)
        return result

    def list_processes(self):
        query = ClientQuery(self, GET_PROCESS_LIST)
        with self.execute(query) as response:
            response.check_return_code()
            result = IrbisProcessInfo.parse(response)
            return result

    def nop(self) -> None:
        with self.execute_ansi([NOP]):
            pass

    def parse_connection_string(self, text: str) -> None:
        for item in text.split(';'):
            parts = item.split('=', 2)
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
        result = self.database
        self.database = self._stack.pop()
        return result

    def push_database(self, database: str) -> str:
        result = self.database
        self._stack.append(result)
        self.database = database
        return result

    def read_binary_file(self, specification: FileSpecification):
        pass

    def read_menu(self, specification: Union[FileSpecification, str]) -> MenuFile:
        if isinstance(specification, str):
            specification = FileSpecification(MASTER_FILE, self.database, specification)

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        with self.execute(query) as response:
            result = MenuFile()
            result.parse(response)
            return result

    def read_opt(self, specification: Union[FileSpecification, str]) -> OptFile:
        if isinstance(specification, str):
            specification = FileSpecification(MASTER_FILE, self.database, specification)

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        with self.execute(query) as response:
            result = OptFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            result.parse(text)
            return result

    def read_par(self, specification: Union[FileSpecification, str]) -> ParFile:
        if isinstance(specification, str):
            specification = FileSpecification(DATA, None, specification)

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        with self.execute(query) as response:
            result = ParFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            result.parse(text)
            return result

    def read_postings(self, parameters) -> [TermPosting]:
        pass

    def read_record(self, mfn: int, version: int = 0) -> MarcRecord:
        mfn = mfn or throw_value_error()
        query = ClientQuery(self, READ_RECORD)
        query.ansi(self.database).add(mfn)
        if version:
            query.add(version)
        result = MarcRecord()
        with self.execute(query) as response:
            response.check_return_code(READ_RECORD_CODES)
            text = response.utf_remaining_lines()
            result.database = self.database
            result.parse(text)
        if version:
            self.unlock_records([mfn])
        return result

    def read_terms(self, parameters: Union[TermParameters, str, Tuple[str, int]]) -> []:
        if isinstance(parameters, tuple):
            parameters2 = TermParameters(parameters[0])
            parameters2.number = parameters[1]
            return self.read_terms(parameters2)

        if isinstance(parameters, str):
            parameters2 = TermParameters(parameters)
            parameters2.number = 10
            return self.read_terms(parameters2)

        database = parameters.database or self.database or throw_value_error()
        command = READ_TERMS_REVERSE if parameters.reverse else READ_TERMS
        query = ClientQuery(self, command)
        query.ansi(database).utf(parameters.start)
        query.add(parameters.number).ansi(parameters.format)
        with self.execute(query) as response:
            response.check_return_code(READ_TERMS_CODES)
            lines = response.utf_remaining_lines()
            result = TermInfo.parse(lines)
            return result

    def read_text_file(self, specification: Union[FileSpecification, str]) -> str:
        if isinstance(specification, str):
            specification2 = FileSpecification(MASTER_FILE, self.database, specification)
            return self.read_text_file(specification2)

        query = ClientQuery(self, READ_DOCUMENT)
        query.ansi(str(specification))
        with self.execute(query) as response:
            result = response.ansi_remaining_text()
        return result

    def reload_dictionary(self, database: str = '') -> None:
        database = database or self.database or throw_value_error()
        with self.execute_ansi([RELOAD_DICTIONARY, database]):
            pass

    def reload_master_file(self, database: str = '') -> None:
        database = database or self.database or throw_value_error()
        with self.execute_ansi([RELOAD_MASTER_FILE, database]):
            pass

    def restart_server(self) -> None:
        with self.execute_ansi([RESTART_SERVER]):
            pass

    def search(self, parameters: Union[SearchParameters, str]) -> []:
        if isinstance(parameters, str):
            parameters2 = SearchParameters(parameters)
            return self.search(parameters2)

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
        return 'host=' + self.host + ';port=' + str(self.port) \
                + ';username=' + self.username + ';password=' + self.password \
                + ';database=' + self.database + ';workstation=' + self.workstation + ';'

    def truncate_database(self, database: str = '') -> None:
        database = database or self.database or throw_value_error()
        with self.execute_ansi([EMPTY_DATABASE, database]):
            pass

    def unlock_database(self, database: str = '') -> None:
        database = database or self.database or throw_value_error()
        with self.execute_ansi([UNLOCK_DATABASE, database]):
            pass

    def unlock_records(self, records: [int], database: str = '') -> None:
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, UNLOCK_RECORDS)
        query.ansi(database)
        for mfn in records:
            query.add(mfn)
        with self.execute(query) as response:
            response.check_return_code()

    def update_ini_file(self, lines: [str]) -> None:
        pass

    def write_record(self, record: MarcRecord, lock: bool = False, actualize: bool = True, dont_parse=False):
        pass

    def write_text_file(self, specification: FileSpecification) -> None:
        pass


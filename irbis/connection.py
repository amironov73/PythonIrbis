# coding: utf-8

"""
Подключение к серверу ИРБИС64.
"""

import asyncio
import socket
import random
import time
from typing import Any, List, Optional, Tuple, Union

from ._common import ACTUALIZE_RECORD, ALL, CREATE_DATABASE, \
    CREATE_DICTIONARY, DATA, DELETE_DATABASE, EMPTY_DATABASE, FORMAT_RECORD, \
    GET_MAX_MFN, GET_PROCESS_LIST, GET_SERVER_STAT, GET_USER_LIST, \
    IRBIS_DELIMITER, irbis_to_dos, irbis_to_lines, irbis_event_loop, \
    LIST_FILES, LOGICALLY_DELETED, MASTER_FILE, MAX_POSTINGS, NOP, \
    NOT_CONNECTED, ObjectWithError, OTHER_DELIMITER, PRINT, READ_RECORD, \
    READ_RECORD_CODES, READ_DOCUMENT, READ_POSTINGS, READ_TERMS, \
    READ_TERMS_REVERSE, READ_TERMS_CODES, RECORD_LIST, REGISTER_CLIENT, \
    RELOAD_DICTIONARY, RELOAD_MASTER_FILE, RESTART_SERVER, safe_str, \
    SEARCH, SERVER_INFO, SET_USER_LIST, short_irbis_to_lines, SYSTEM, \
    throw_value_error, UNREGISTER_CLIENT, UNLOCK_DATABASE, UNLOCK_RECORDS, \
    UPDATE_INI_FILE, UPDATE_RECORD

from .alphabet import AlphabetTable, UpperCaseTable
from .database import DatabaseInfo
from .error import IrbisError, IrbisFileNotFoundError
from .ini import IniFile
from .menus import MenuFile
from .opt import OptFile
from .par import ParFile
from .process import Process
from .query import ClientQuery
from .record import RawRecord, Record
from .response import ServerResponse
from .search import FoundLine, SearchParameters, SearchScenario
from .specification import FileSpecification
from .stat import ServerStat
from .table import TableDefinition
from .terms import PostingParameters, TermInfo, TermPosting, TermParameters
from .tree import TreeFile
from .version import ServerVersion
from .user import UserInfo


class Connection(ObjectWithError):
    """
    Подключение к серверу
    """

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 6666
    DEFAULT_DATABASE = 'IBIS'

    __slots__ = ('host', 'port', 'username', 'password', 'database',
                 'workstation', 'client_id', 'query_id', 'connected',
                 '_stack', 'server_version', 'ini_file')

    def __init__(self, host: Optional[str] = None,
                 port: int = 0,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 database: Optional[str] = None,
                 workstation: str = 'C') -> None:
        super().__init__()
        self.host: str = host or Connection.DEFAULT_HOST
        self.port: int = port or Connection.DEFAULT_PORT
        self.username: Optional[str] = username
        self.password: Optional[str] = password
        self.database: str = database or Connection.DEFAULT_DATABASE
        self.workstation: str = workstation
        self.client_id: int = 0
        self.query_id: int = 0
        self.connected: bool = False
        self._stack: List[str] = []
        self.server_version: Optional[str] = None
        self.ini_file: IniFile = IniFile()
        self.last_error = 0

    def actualize_record(self, mfn: int,
                         database: Optional[str] = None) -> bool:
        """
        Актуализация записи с указанным MFN.

        :param mfn: MFN записи.
        :param database: База данных.
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        database = database or self.database or throw_value_error()

        assert isinstance(mfn, int)
        assert isinstance(database, str)

        query = ClientQuery(self, ACTUALIZE_RECORD).ansi(database).add(mfn)
        with self.execute(query) as response:
            if not response.check_return_code():
                return False

        return True

    def check_connection(self) -> bool:
        """
        Проверяет, подключен ли клиент.
        Устанавливает код ошибки, если не подключен.

        :return: Состояние подключения.
        """
        if not self.connected:
            self.last_error = NOT_CONNECTED

        return self.connected

    def _connect(self, response: ServerResponse) -> IniFile:
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

        while True:
            self.query_id = 0
            self.client_id = random.randint(100000, 999999)
            query = ClientQuery(self, REGISTER_CLIENT)
            query.ansi(self.username).ansi(self.password)
            with self.execute(query) as response:
                if response.get_return_code() == -3337:
                    continue

                return self._connect(response)

    async def connect_async(self) -> IniFile:
        """
        Асинхронное подключение к серверу ИРБИС64.

        :return: INI-файл
        """
        if self.connected:
            return self.ini_file

        while True:
            self.query_id = 0
            self.client_id = random.randint(100000, 999999)
            query = ClientQuery(self, REGISTER_CLIENT)
            query.ansi(self.username).ansi(self.password)
            response = await self.execute_async(query)
            if response.get_return_code() == -3337:
                response.close()
                continue

            result = self._connect(response)
            response.close()
            return result

    def create_database(self, database: Optional[str] = None,
                        description: Optional[str] = None,
                        reader_access: bool = True) -> bool:
        """
        Создание базы данных.

        :param database: Имя создаваемой базы.
        :param description: Описание в свободной форме.
        :param reader_access: Читатель будет иметь доступ?
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        database = database or self.database or throw_value_error()
        description = description or ''

        assert isinstance(database, str)
        assert isinstance(description, str)

        query = ClientQuery(self, CREATE_DATABASE)
        query.ansi(database).ansi(description).add(int(reader_access))
        with self.execute(query) as response:
            if not response.check_return_code():
                return False

        return True

    def create_dictionary(self, database: Optional[str] = None) -> bool:
        """
        Создание словаря в базе данных.

        :param database: Имя базы данных.
        :return: Признау успешности операции.
        """
        if not self.check_connection():
            return False

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        query = ClientQuery(self, CREATE_DICTIONARY).ansi(database)
        with self.execute(query) as response:
            if not response.check_return_code():
                return False

        return True

    def delete_database(self, database: Optional[str] = None) -> bool:
        """
        Удаление базы данных.

        :param database: Имя удаляемой базы.
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        assert isinstance(database, str)

        database = database or self.database or throw_value_error()
        query = ClientQuery(self, DELETE_DATABASE).ansi(database)
        with self.execute(query) as response:
            if not response.check_return_code():
                return False

        return True

    def delete_record(self, mfn: int) -> bool:
        """
        Удаление записи по ее MFN.

        :param mfn: MFN удаляемой записи
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        assert mfn
        assert isinstance(mfn, int)

        record = self.read_record(mfn)
        if not record:
            return False
        if not record.is_deleted():
            record.status |= LOGICALLY_DELETED
            return bool(self.write_record(record, dont_parse=True))
        return True

    def disconnect(self) -> None:
        """
        Отключение от сервера.

        :return: None.
        """
        if not self.connected:
            return

        query = ClientQuery(self, UNREGISTER_CLIENT)
        query.ansi(self.username)
        self.execute_forget(query)
        self.connected = False

    async def disconnect_async(self) -> None:
        """
        Асинхронное отключение от сервера.

        :return: None.
        """
        if not self.connected:
            return

        query = ClientQuery(self, UNREGISTER_CLIENT)
        query.ansi(self.username)
        response = await self.execute_async(query)
        response.close()
        self.connected = False

    def execute(self, query: ClientQuery) -> ServerResponse:
        """
        Выполнение произвольного запроса к серверу.

        :param query: Запрос
        :return: Ответ сервера (не забыть закрыть!)
        """
        self.last_error = 0
        sock = socket.socket()
        sock.connect((self.host, self.port))
        packet = query.encode()
        sock.send(packet)
        result = ServerResponse(self)
        result.read_data(sock)
        result.initial_parse()
        return result

    def execute_ansi(self, *commands) -> ServerResponse:
        """
        Простой запрос к серверу, когда все строки запроса
        в кодировке ANSI.

        :param commands: Команда и параметры запроса
        :return: Ответ сервера (не забыть закрыть!)
        """
        query = ClientQuery(self, commands[0])
        for line in commands[1:]:
            query.ansi(line)
        return self.execute(query)

    async def execute_async(self, query: ClientQuery) -> ServerResponse:
        """
        Асинхронное исполнение запроса.
        ВНИМАНИЕ: сначала должна быть выполнена инициализация init_async()!

        :param query: Запрос.
        :return: Ответ сервера.
        """
        self.last_error = 0
        reader, writer = await asyncio.open_connection(self.host,
                                                       self.port,
                                                       loop=irbis_event_loop)
        packet = query.encode()
        writer.write(packet)
        result = ServerResponse(self)
        await result.read_data_async(reader)
        result.initial_parse()
        writer.close()
        return result

    def execute_forget(self, query: ClientQuery) -> None:
        """
        Выполнение запроса к серверу, когда нам не важен результат
        (мы не собираемся его парсить).

        :param query: Клиентский запрос
        :return: None
        """
        with self.execute(query):
            pass

    # noinspection DuplicatedCode
    def format_record(self, script: str, record: Union[Record, int]) -> str:
        """
        Форматирование записи с указанным MFN.

        :param script: Текст формата
        :param record: MFN записи либо сама запись
        :return: Результат расформатирования
        """
        if not self.check_connection():
            return ''

        script = script or throw_value_error()
        if not record:
            raise ValueError()

        assert isinstance(script, str)
        assert isinstance(record, (Record, int))

        if not script:
            return ''

        query = ClientQuery(self, FORMAT_RECORD).ansi(self.database)
        query.format(script)

        if isinstance(record, int):
            query.add(1).add(record)
        else:
            query.add(-2).utf(IRBIS_DELIMITER.join(record.encode()))

        with self.execute(query) as response:
            if not response.check_return_code():
                return ''

            result = response.utf_remaining_text().strip('\r\n')
            return result

    # noinspection DuplicatedCode
    async def format_record_async(self, script: str,
                                  record: Union[Record, int]) -> str:
        """
        Асинхронное форматирование записи с указанным MFN.

        :param script: Текст формата
        :param record: MFN записи либо сама запись
        :return: Результат расформатирования
        """
        if not self.check_connection():
            return ''

        if not script:
            return ''

        if not record:
            raise ValueError()

        assert isinstance(script, str)
        assert isinstance(record, (Record, int))

        query = ClientQuery(self, FORMAT_RECORD).ansi(self.database)
        query.format(script)
        if isinstance(record, int):
            query.add(1).add(record)
        else:
            query.add(-2).utf(IRBIS_DELIMITER.join(record.encode()))

        response = await self.execute_async(query)
        if not response.check_return_code():
            return ''

        result = response.utf_remaining_text().strip('\r\n')
        response.close()
        return result

    def format_records(self, script: str, records: List[int]) -> List[str]:
        """
        Форматирование группы записей по MFN.

        :param script: Текст формата
        :param records: Список MFN
        :return: Список строк
        """
        if not self.check_connection():
            return []

        if not records:
            return []

        script = script or throw_value_error()

        assert isinstance(script, str)
        assert isinstance(records, list)

        if not script:
            return [''] * len(records)

        if len(records) > MAX_POSTINGS:
            raise IrbisError()

        query = ClientQuery(self, FORMAT_RECORD).ansi(self.database)
        query.format(script)
        query.add(len(records))
        for mfn in records:
            query.add(mfn)

        with self.execute(query) as response:
            if not response.check_return_code():
                return []

            result = response.utf_remaining_lines()
            result = [line.split('#', 1)[1] for line in result]
            return result

    def get_database_info(self, database: Optional[str] = None) \
            -> DatabaseInfo:
        """
        Получение информации о базе данных.

        :param database: Имя базы
        :return: Информация о базе
        """
        if not self.check_connection():
            return DatabaseInfo()

        database = database or self.database or throw_value_error()
        query = ClientQuery(self, RECORD_LIST).ansi(database)
        with self.execute(query) as response:
            result = DatabaseInfo()
            if not response.check_return_code():
                return result

            result.parse(response)
            result.name = database
            return result

    def get_max_mfn(self, database: Optional[str] = None) -> int:
        """
        Получение максимального MFN для указанной базы данных.

        :param database: База данных.
        :return: MFN, который будет присвоен следующей записи.
        """
        if not self.check_connection():
            return 0

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        with self.execute_ansi(GET_MAX_MFN, database) as response:
            if not response.check_return_code():
                return 0
            result = response.return_code
            return result

    async def get_max_mfn_async(self, database: Optional[str] = None) -> int:
        """
        Асинхронное получение максимального MFN.

        :param database: База данных.
        :return: MFN, который будет присвоен следующей записи.
        """
        database = database or self.database or throw_value_error()
        assert isinstance(database, str)
        query = ClientQuery(self, GET_MAX_MFN)
        query.ansi(database)
        response = await self.execute_async(query)
        response.check_return_code()
        result = response.return_code
        response.close()
        return result

    def get_server_stat(self) -> ServerStat:
        """
        Получение статистики с сервера.

        :return: Полученная статистика
        """
        if not self.check_connection():
            return ServerStat()

        query = ClientQuery(self, GET_SERVER_STAT)
        with self.execute(query) as response:
            result = ServerStat()
            if not response.check_return_code():
                return result
            result.parse(response)
            return result

    def get_server_version(self) -> ServerVersion:
        """
        Получение версии сервера.

        :return: Версия сервера
        """
        if not self.check_connection():
            return ServerVersion()

        query = ClientQuery(self, SERVER_INFO)
        with self.execute(query) as response:
            result = ServerVersion()
            if not response.check_return_code():
                return result
            lines = response.ansi_remaining_lines()
            result.parse(lines)
            if not self.server_version:
                self.server_version = result.version
            return result

    def list_databases(self, specification: str) \
            -> List[DatabaseInfo]:
        """
        Получение списка баз данных.

        :param specification: Спецификация файла, например, '1..dbnam2.mnu'
        :return: Список баз данных
        """
        if not self.check_connection():
            return []

        menu = self.read_menu(specification)
        result: List[DatabaseInfo] = []
        for entry in menu.entries:
            db_info: DatabaseInfo = DatabaseInfo()
            db_info.name = entry.code
            if db_info.name[0] == '-':
                db_info.name = db_info.name[1:]
                db_info.read_only = True
            db_info.description = entry.comment
            result.append(db_info)

        return result

    def list_files(self,
                   *specification: Union[FileSpecification, str]) -> List[str]:
        """
        Получение списка файлов с сервера.

        :param specification: Спецификация или маска имени файла
        (если нужны файлы, лежащие в папке текущей базы данных)
        :return: Список файлов
        """
        if not self.check_connection():
            return []

        query = ClientQuery(self, LIST_FILES)

        is_ok = False
        for spec in specification:
            if isinstance(spec, str):
                spec = self.near_master(spec)
            query.ansi(str(spec))
            is_ok = True

        result: List[str] = []
        if not is_ok:
            return result

        with self.execute(query) as response:
            lines = response.ansi_remaining_lines()
            lines = [line for line in lines if line]
            for line in lines:
                result.extend(one for one in irbis_to_lines(line) if one)
        return result

    # noinspection DuplicatedCode
    def list_processes(self) -> List[Process]:
        """
        Получение списка серверных процессов.

        :return: Список процессов
        """
        if not self.check_connection():
            return []

        query = ClientQuery(self, GET_PROCESS_LIST)
        with self.execute(query) as response:
            response.check_return_code()
            result: List[Process] = []
            process_count = response.number()
            lines_per_process = response.number()

            if not process_count or not lines_per_process:
                return result

            for _ in range(process_count):
                process = Process()
                process.number = response.ansi()
                process.ip_address = response.ansi()
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

    def list_users(self) -> List[UserInfo]:
        """
        Получение списка пользователей с сервера.

        :return: Список пользователей
        """
        if not self.check_connection():
            return []

        query = ClientQuery(self, GET_USER_LIST)
        with self.execute(query) as response:
            if not response.check_return_code():
                return []
            result = UserInfo.parse(response)
            return result

    def monitor_operation(self, operation: str) -> str:
        """
        Мониторинг операции (ждем завершения указанной операции).

        :param operation: Какую операцию ждем
        :return: Серверный лог-файл (результат выполнения операции)
        """
        if not self.check_connection():
            return ''

        client_id = str(self.client_id)
        while True:
            processes = self.list_processes()
            found = False
            for process in processes:
                if process.client_id == client_id \
                        and process.last_command == operation:
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
        """
        Файл рядом с мастер-файлом текущей базы данных.

        :param filename: Имя файла
        :return: Спецификация файла
        """

        return FileSpecification(MASTER_FILE, self.database, filename)

    def nop(self) -> bool:
        """
        Пустая операция (используется для периодического
        подтверждения подключения клиента).

        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        with self.execute_ansi(NOP):
            return True

    async def nop_async(self) -> bool:
        """
        Асинхронная пустая операция.

        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        query = ClientQuery(self, NOP)
        response = await self.execute_async(query)
        response.close()
        return True

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

    def print_table(self, definition: TableDefinition) -> str:
        """
        Расформатирование таблицы.

        :param definition: Определение таблицы
        :return: Результат расформатирования
        """
        if not self.check_connection():
            return ''

        database = definition.database or self.database or throw_value_error()
        query = ClientQuery(self, PRINT)
        query.ansi(database).ansi(definition.table)
        query.ansi('')  # instead of the headers
        query.ansi(definition.mode).utf(definition.search)
        query.add(definition.min_mfn).add(definition.max_mfn)
        query.utf(definition.sequential)
        query.ansi('')  # instead of the MFN list
        with self.execute(query) as response:
            result = response.utf_remaining_text()
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

    def read_alphabet_table(self,
                            specification: Optional[FileSpecification] =
                            None) \
            -> AlphabetTable:
        """
        Чтение алфавитной таблицы с сервера.

        :param specification: Спецификация
        :return: Таблица
        """
        if not self.check_connection():
            return AlphabetTable.get_default()

        if specification is None:
            specification = FileSpecification(SYSTEM, None,
                                              AlphabetTable.FILENAME)

        with self.read_text_stream(specification) as response:
            text = response.ansi_remaining_text()
            if text:
                result = AlphabetTable()
                result.parse(text)
            else:
                result = AlphabetTable.get_default()
            return result

    def read_binary_file(self, specification: Union[FileSpecification, str]) \
            -> Optional[bytearray]:
        """
        Чтение двоичного файла с сервера.

        :param specification: Спецификация файла.
        :return: Массив байт или None.
        """
        if not self.check_connection():
            return None

        if isinstance(specification, str):
            specification = self.near_master(specification)

        assert isinstance(specification, FileSpecification)

        specification.binary = True
        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        with self.execute(query) as response:
            result = response.get_binary_file()
            return result

    def read_ini_file(self, specification: Union[FileSpecification, str]) \
            -> IniFile:
        """
        Чтение INI-файла с сервера.

        :param specification: Спецификация
        :return: INI-файл
        """
        if not self.check_connection():
            return IniFile()

        if isinstance(specification, str):
            specification = self.near_master(specification)

        assert isinstance(specification, FileSpecification)

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        with self.execute(query) as response:
            result = IniFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            result.parse(text)
            return result

    def read_menu(self, specification: Union[FileSpecification, str]) \
            -> MenuFile:
        """
        Чтение меню с сервера.

        :param specification: Спецификация файла
        :return: Меню
        """
        if not self.check_connection():
            return MenuFile()

        with self.read_text_stream(specification) as response:
            result = MenuFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            result.parse(text)
            return result

    def read_opt_file(self, specification: Union[FileSpecification, str]) \
            -> OptFile:
        """
        Получение файла оптимизации рабочих листов с сервера.

        :param specification: Спецификация
        :return: Файл оптимизации
        """
        if not self.check_connection():
            return OptFile()

        with self.read_text_stream(specification) as response:
            result = OptFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            result.parse(text)
            return result

    def read_par_file(self, specification: Union[FileSpecification, str]) \
            -> ParFile:
        """
        Получение PAR-файла с сервера.

        :param specification: Спецификация или имя файла (если он в папке DATA)
        :return: Полученный файл
        """
        if not self.check_connection():
            return ParFile()

        if isinstance(specification, str):
            specification = FileSpecification(DATA, None, specification)

        with self.read_text_stream(specification) as response:
            result = ParFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            result.parse(text)
            return result

    def read_postings(self, parameters: Union[PostingParameters, str],
                      fmt: Optional[str] = None) -> List[TermPosting]:
        """
        Считывание постингов для указанных термов из поискового словаря.

        :param parameters: Параметры постингов или терм
        :param fmt: Опциональный формат
        :return: Список постингов
        """
        if not self.check_connection():
            return []

        if isinstance(parameters, str):
            parameters = PostingParameters(parameters)
            parameters.fmt = fmt

        database = parameters.database or self.database or throw_value_error()
        query = ClientQuery(self, READ_POSTINGS)
        query.ansi(database).add(parameters.number)
        query.add(parameters.first).ansi(parameters.fmt)
        for term in parameters.terms:
            query.utf(term)
        with self.execute(query) as response:
            result: List[TermPosting] = []
            if not response.check_return_code(READ_TERMS_CODES):
                return result

            while True:
                line = response.utf()
                if not line:
                    break
                posting = TermPosting()
                posting.parse(line)
                result.append(posting)
            return result

    def read_raw_record(self, mfn: int) -> Optional[RawRecord]:
        """
        Чтение сырой записи с сервера.

        :param mfn: MFN записи.
        :return: Загруженная с сервера запись.
        """
        if not self.check_connection():
            return None

        mfn = mfn or int(throw_value_error())

        query = ClientQuery(self, READ_RECORD)
        query.ansi(self.database).add(mfn)
        with self.execute(query) as response:
            if not response.check_return_code(READ_RECORD_CODES):
                return None

            text = response.utf_remaining_lines()
            result = RawRecord()
            result.database = self.database
            result.parse(text)

        return result

    def read_record(self, mfn: int, version: int = 0) -> Optional[Record]:
        """
        Чтение записи с указанным MFN с сервера.

        :param mfn: MFN
        :param version: версия
        :return: Прочитанная запись
        """
        if not self.check_connection():
            return None

        mfn = mfn or int(throw_value_error())

        assert isinstance(mfn, int)

        query = ClientQuery(self, READ_RECORD).ansi(self.database).add(mfn)
        if version:
            query.add(version)
        with self.execute(query) as response:
            if not response.check_return_code(READ_RECORD_CODES):
                return None

            text = response.utf_remaining_lines()
            result = Record()
            result.database = self.database
            result.parse(text)

        if version:
            self.unlock_records([mfn])

        return result

    async def read_record_async(self, mfn: int) -> Optional[Record]:
        """
        Асинхронное чтение записи.

        :param mfn: MFN считываемой записи.
        :return: Прочитанная запись.
        """
        if not self.check_connection():
            return None

        mfn = mfn or int(throw_value_error())
        assert isinstance(mfn, int)
        query = ClientQuery(self, READ_RECORD).ansi(self.database).add(mfn)

        response = await self.execute_async(query)
        if not response.check_return_code(READ_RECORD_CODES):
            return None

        text = response.utf_remaining_lines()
        result = Record()
        result.database = self.database
        result.parse(text)
        response.close()
        return result

    def read_record_postings(self, mfn: int, prefix: str) -> List[TermPosting]:
        """
        Получение постингов для указанных записи и префикса.

        :param mfn: MFN записи.
        :param prefix: Префикс в виде "A=$".
        :return: Список постингов.
        """
        if not self.check_connection():
            return []

        assert mfn > 0

        query = ClientQuery(self, 'V')
        query.ansi(self.database).add(mfn).utf(prefix)
        result: List[TermPosting] = []
        with self.execute(query) as response:
            if not response.check_return_code():
                return result

            lines = response.utf_remaining_lines()
            for line in lines:
                one: TermPosting = TermPosting()
                one.parse(line)
                result.append(one)
        return result

    def read_records(self, *mfns: int) -> List[Record]:
        """
        Чтение записей с указанными MFN с сервера.

        :param mfns: Перечень MFN
        :return: Список записей
        """
        if not self.check_connection():
            return []

        array = list(mfns)

        if not array:
            return []

        if len(array) == 1:
            record = self.read_record(array[0])
            return [record] if record else []

        lines = self.format_records(ALL, array)
        result: List[Record] = []
        for line in lines:
            parts = line.split(OTHER_DELIMITER)
            if parts:
                parts = [x for x in parts[1:] if x]
                record = Record()
                record.parse(parts)
                if record:
                    record.database = self.database
                    result.append(record)

        return result

    def read_search_scenario(self,
                             specification: Union[FileSpecification, str]) \
            -> List[SearchScenario]:
        """
        Read search scenario from the server.

        :param specification: File which contains the scenario
        :return: List of the scenarios (possibly empty)
        """
        if not self.check_connection():
            return []

        if isinstance(specification, str):
            specification = self.near_master(specification)

        with self.read_text_stream(specification) as response:
            ini = IniFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            ini.parse(text)
            result = SearchScenario.parse(ini)
            return result

    def read_terms(self,
                   parameters: Union[TermParameters, str, Tuple[str, int]]) \
            -> List[TermInfo]:
        """
        Получение термов поискового словаря.

        :param parameters: Параметры термов или терм
            или кортеж "терм, количество"
        :return: Список термов
        """
        if not self.check_connection():
            return []

        if isinstance(parameters, tuple):
            parameters2 = TermParameters(parameters[0])
            parameters2.number = parameters[1]
            parameters = parameters2

        if isinstance(parameters, str):
            parameters = TermParameters(parameters)
            parameters.number = 10

        assert isinstance(parameters, TermParameters)

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

    def read_text_file(self, specification: Union[FileSpecification, str]) \
            -> str:
        """
        Получение содержимого текстового файла с сервера.

        :param specification: Спецификация или имя файла
        (если он находится в папке текущей базы данных).
        :return: Текст файла или пустая строка, если файл не найден
        """
        if not self.check_connection():
            return ''

        with self.read_text_stream(specification) as response:
            result = response.ansi_remaining_text()
            result = irbis_to_dos(result)
            return result

    async def read_text_file_async(self,
                                   specification: Union[FileSpecification,
                                                        str]) -> str:
        """
        Асинхронное получение содержимого текстового файла с сервера.

        :param specification: Спецификация или имя файла
            (если он находится в папке текущей базы данных).
        :return: Текст файла или пустая строка, если файл не найден
        """
        if not self.check_connection():
            return ''

        if isinstance(specification, str):
            specification = self.near_master(specification)
        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        response = await self.execute_async(query)
        result = response.ansi_remaining_text()
        result = irbis_to_dos(result)
        response.close()
        return result

    def read_text_stream(self, specification: Union[FileSpecification, str]) \
            -> ServerResponse:
        """
        Получение текстового файла с сервера в виде потока.

        :param specification: Спецификация или имя файла
        (если он находится в папке текущей базы данных).
        :return: ServerResponse, из которого можно считывать строки
        """

        if isinstance(specification, str):
            specification = self.near_master(specification)

        assert isinstance(specification, FileSpecification)

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        result = self.execute(query)
        return result

    def read_tree_file(self, specification: Union[FileSpecification, str]) \
            -> TreeFile:
        """
        Чтение TRE-файла с сервера.

        :param specification:  Спецификация
        :return: Дерево
        """
        if not self.check_connection():
            return TreeFile()

        with self.read_text_stream(specification) as response:
            text = response.ansi_remaining_text()
            text = [line for line in irbis_to_lines(text) if line]
            result = TreeFile()
            result.parse(text)
            return result

    def read_uppercase_table(self,
                             specification: Optional[FileSpecification] =
                             None) \
            -> UpperCaseTable:
        """
        Чтение таблицы преобразования в верхний регистр с сервера.

        :param specification: Спецификация
        :return: Таблица
        """
        if not self.check_connection():
            return UpperCaseTable.get_default()

        if specification is None:
            specification = FileSpecification(SYSTEM,
                                              None,
                                              UpperCaseTable.FILENAME)

        with self.read_text_stream(specification) as response:
            text = response.ansi_remaining_text()
            if text:
                result = UpperCaseTable()
                result.parse(text)
            else:
                result = UpperCaseTable.get_default()
            return result

    def reload_dictionary(self, database: Optional[str] = None) -> bool:
        """
        Пересоздание словаря.

        :param database: База данных
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        with self.execute_ansi(RELOAD_DICTIONARY, database):
            return True

    def reload_master_file(self, database: Optional[str] = None) -> bool:
        """
        Пересоздание мастер-файла.

        :param database: База данных
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        with self.execute_ansi(RELOAD_MASTER_FILE, database):
            return True

    def restart_server(self) -> bool:
        """
        Перезапуск сервера (без утери подключенных клиентов).

        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        with self.execute_ansi(RESTART_SERVER):
            return True

    async def restart_server_async(self) -> bool:
        """
        Асинхронный перезапуск сервера (без утери подключенных клиентов).
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        query = ClientQuery(self, RESTART_SERVER)
        response = await self.execute_async(query)
        response.close()
        return True

    def require_alphabet_table(self,
                               specification: Optional[FileSpecification] =
                               None) \
            -> AlphabetTable:
        """
        Чтение алфавитной таблицы с сервера.
        :param specification: Спецификация
        :return: Таблица
        """
        if specification is None:
            specification = FileSpecification(SYSTEM,
                                              None,
                                              AlphabetTable.FILENAME)

        with self.read_text_stream(specification) as response:
            text = response.ansi_remaining_text()
            if not text:
                raise IrbisFileNotFoundError(specification)
            if text:
                result = AlphabetTable()
                result.parse(text)
            else:
                result = AlphabetTable.get_default()
            return result

    def require_menu(self,
                     specification: Union[FileSpecification, str]) -> MenuFile:
        """
        Чтение меню с сервера.

        :param specification: Спецификация файла
        :return: Меню
        """
        with self.read_text_stream(specification) as response:
            result = MenuFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            if not text:
                raise IrbisFileNotFoundError(specification)
            result.parse(text)
            return result

    def require_opt_file(self,
                         specification: Union[FileSpecification, str]) \
            -> OptFile:
        """
        Получение файла оптимизации рабочих листов с сервера.

        :param specification: Спецификация
        :return: Файл оптимизации
        """
        with self.read_text_stream(specification) as response:
            result = OptFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            if not text:
                raise IrbisFileNotFoundError(specification)
            result.parse(text)
            return result

    def require_par_file(self,
                         specification: Union[FileSpecification, str]) \
            -> ParFile:
        """
        Получение PAR-файла с сервера.

        :param specification: Спецификация или имя файла (если он в папке DATA)
        :return: Полученный файл
        """
        if isinstance(specification, str):
            specification = FileSpecification(DATA, None, specification)

        with self.read_text_stream(specification) as response:
            result = ParFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            if not text:
                raise IrbisFileNotFoundError(specification)
            result.parse(text)
            return result

    def require_text_file(self,
                          specification: FileSpecification) -> str:
        """
        Чтение текстового файла с сервера.

        :param specification: Спецификация
        :return: Содержимое файла
        """
        result = self.read_text_file(specification)
        if not result:
            raise IrbisFileNotFoundError(specification)

        return result

    def require_tree_file(self,
                          specification: Union[FileSpecification, str]) \
            -> TreeFile:
        """
        Чтение TRE-файла с сервера.

        :param specification: Спецификация файла.
        :return: Дерево
        """
        with self.read_text_stream(specification) as response:
            text = response.ansi_remaining_text()
            if not text:
                raise IrbisFileNotFoundError(specification)
            text = [line for line in irbis_to_lines(text) if line]
            result = TreeFile()
            result.parse(text)
            return result

    # noinspection DuplicatedCode
    def search(self, parameters: Any) -> List[int]:
        """
        Поиск записей.

        :param parameters: Параметры поиска (либо поисковый запрос).
        :return: Список найденных MFN.
        """
        if not self.check_connection():
            return []

        if not isinstance(parameters, SearchParameters):
            parameters = SearchParameters(str(parameters))

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
        if not response.check_return_code():
            return []

        _ = response.number()  # Число найденных записей
        result: List[int] = []
        while 1:
            line = response.ansi()
            if not line:
                break
            mfn = int(line)
            result.append(mfn)
        return result

    def search_all(self, expression: Any) -> List[int]:
        """
        Поиск всех записей (даже если их окажется больше 32 тыс.).
        :param expression: Поисковый запрос.
        :return: Список найденных MFN
        """
        if not self.check_connection():
            return []

        assert expression
        expression = str(expression)

        result: List[int] = []
        first: int = 1
        expected: int = 0

        while 1:
            query = ClientQuery(self, SEARCH)
            query.ansi(self.database)
            query.utf(expression)
            query.add(10000)
            query.add(first)
            query.new_line()
            query.add(0)
            query.add(0)

            response = self.execute(query)
            if not response.check_return_code():
                return result

            if first == 1:
                expected = response.number()
                if expected == 0:
                    break
            else:
                _ = response.number()

            while 1:
                line = response.ansi()
                if not line:
                    break
                mfn = int(line)
                result.append(mfn)
                first = first + 1

            if first >= expected:
                return result

        return result

    # noinspection DuplicatedCode
    async def search_async(self, parameters: Any) -> List[int]:
        """
        Асинхронный поиск записей.

        :param parameters: Параметры поиска.
        :return: Список найденных MFN.
        """
        if not self.check_connection():
            return []

        if not isinstance(parameters, SearchParameters):
            parameters = SearchParameters(str(parameters))

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

        response = await self.execute_async(query)
        if not response.check_return_code():
            return []

        _ = response.number()  # Число найденных записей
        result: List[int] = []
        while 1:
            line = response.ansi()
            if not line:
                break
            mfn = int(line)
            result.append(mfn)
        response.close()
        return result

    # noinspection DuplicatedCode
    def search_count(self, expression: Any) -> int:
        """
        Количество найденных записей.

        :param expression: Поисковый запрос.
        :return: Количество найденных записей.
        """
        if not self.check_connection():
            return 0

        expression = str(expression)

        query = ClientQuery(self, SEARCH)
        query.ansi(self.database)
        query.utf(expression)
        query.add(0)
        query.add(0)

        response = self.execute(query)
        if not response.check_return_code():
            return 0

        return response.number()

    # noinspection DuplicatedCode
    async def search_count_async(self, expression: Any) -> int:
        """
        Асинхронное получение количества найденных записей.

        :param expression: Поисковый запрос.
        :return: Количество найденных записей.
        """
        if not self.check_connection():
            return 0

        expression = str(expression)

        query = ClientQuery(self, SEARCH)
        query.ansi(self.database)
        query.utf(expression)
        query.add(0)
        query.add(0)

        response = await self.execute_async(query)
        if not response.check_return_code():
            return 0

        result = response.number()
        response.close()
        return result

    # noinspection DuplicatedCode
    def search_ex(self, parameters: Any) -> List[FoundLine]:
        """
        Расширенный поиск записей.

        :param parameters: Параметры поиска (либо поисковый запрос)
        :return: Список найденных записей
        """
        if not self.check_connection():
            return []

        if not isinstance(parameters, SearchParameters):
            parameters = SearchParameters(str(parameters))

        database = parameters.database or self.database or throw_value_error()
        query = ClientQuery(self, SEARCH)
        query.ansi(database)
        query.utf(parameters.expression)
        query.add(parameters.number)
        query.add(parameters.first)
        query.format(parameters.format)
        query.add(parameters.min_mfn)
        query.add(parameters.max_mfn)
        query.ansi(parameters.sequential)

        response = self.execute(query)
        if not response.check_return_code():
            return []

        _ = response.number()  # Число найденных записей
        result = []
        while 1:
            line = response.utf()
            if not line:
                break
            item = FoundLine()
            item.parse_line(line)
            result.append(item)
        return result

    # noinspection DuplicatedCode
    def search_format(self, expression: Any,
                      format_specification: Any, limit: int = 0) -> List[str]:
        """
        Поиск записей с одновременным их расформатированием.

        :param expression: Поисковое выражение.
        :param format_specification: Спецификация формата.
        :param limit: Ограничение на количество выдаваемых записей.
        :return: Список расформатированных записей.
        """
        if not self.check_connection():
            return []

        assert isinstance(limit, int)

        expression = str(expression)
        format_specification = str(format_specification)

        query = ClientQuery(self, SEARCH)
        query.ansi(self.database)
        query.utf(expression)
        query.add(0)
        query.add(1)
        query.format(format_specification)
        query.add(0)
        query.add(0)

        response = self.execute(query)
        if not response.check_return_code():
            return []

        _ = response.number()
        result: List[str] = []
        while 1:
            line = response.utf()
            if not line:
                break
            parts = line.split('#', 2)
            if len(parts) > 1:
                text = parts[1]
                if text:
                    result.append(text)
            if limit and len(result) >= limit:
                break

        return result

    # noinspection DuplicatedCode
    def search_read(self, expression: Any, limit: int = 0) -> List[Record]:
        """
        Поиск и считывание записей.

        :param expression: Поисковый запрос.
        :param limit: Лимит считываемых записей (0 - нет).
        :return: Список найденных записей.
        """
        if not self.check_connection():
            return []

        assert isinstance(limit, int)

        expression = str(expression)

        query = ClientQuery(self, SEARCH)
        query.ansi(self.database)
        query.utf(expression)
        query.add(0)
        query.add(1)
        query.ansi(ALL)
        query.add(0)
        query.add(0)

        response = self.execute(query)
        if not response.check_return_code():
            return []

        _ = response.number()
        result: List[Record] = []
        while 1:
            line = response.utf()
            if not line:
                break
            lines = line.split("\x1F")
            lines = lines[1:]
            record = Record()
            record.parse(lines)
            result.append(record)
            if limit and len(result) >= limit:
                break
        return result

    def throw_on_error(self) -> None:
        """
        Бросает исключение, если произошла ошибка
        при выполнении последней операции.

        :return: None
        """
        if self.last_error < 0:
            raise IrbisError(self.last_error)

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

    def truncate_database(self, database: Optional[str] = None) -> bool:
        """
        Опустошение базы данных.

        :param database: Имя опустошаемой базы данных.
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        with self.execute_ansi(EMPTY_DATABASE, database):
            return True

    def undelete_record(self, mfn: int) -> bool:
        """
        Восстановление записи по ее MFN.

        :param mfn: MFN восстанавливаемой записи.
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        assert mfn
        assert isinstance(mfn, int)

        record = self.read_record(mfn)
        if not record:
            return False

        if record.is_deleted():
            record.status &= ~LOGICALLY_DELETED
            return bool(self.write_record(record, dont_parse=True))

        return True

    def unlock_database(self, database: Optional[str] = None) -> bool:
        """
        Разблокирование базы данных.

        :param database: Имя базы
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        with self.execute_ansi(UNLOCK_DATABASE, database):
            return True

    def unlock_records(self, records: List[int],
                       database: Optional[str] = None) -> bool:
        """
        Разблокирование записей.

        :param records: Список MFN.
        :param database: База данных.
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        if not records:
            return True

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        query = ClientQuery(self, UNLOCK_RECORDS).ansi(database)
        for mfn in records:
            query.add(mfn)
        with self.execute(query) as response:
            if not response.check_return_code():
                return False

        return True

    def update_ini_file(self, lines: List[str]) -> bool:
        """
        Обновление строк серверного INI-файла.

        :param lines: Измененные строки.
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        if not lines:
            return True

        query = ClientQuery(self, UPDATE_INI_FILE)
        for line in lines:
            query.ansi(line)
        self.execute_forget(query)

        return True

    def update_user_list(self, users: List[UserInfo]) -> bool:
        """
        Обновление списка пользователей на сервере.

        :param users:  Список пользователей
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        assert isinstance(users, list) and users

        query = ClientQuery(self, SET_USER_LIST)
        for user in users:
            query.ansi(user.encode())
        self.execute_forget(query)

        return True

    # noinspection DuplicatedCode
    def write_raw_record(self, record: RawRecord,
                         lock: bool = False,
                         actualize: bool = True) -> int:
        """
        Сохранение записи на сервере.

        :param record: Запись
        :param lock: Оставить запись заблокированной?
        :param actualize: Актуализировать запись?
        :return: Новый максимальный MFN.
        """
        if not self.check_connection():
            return 0

        database = record.database or self.database or throw_value_error()
        if not record:
            raise ValueError()

        assert isinstance(record, RawRecord)
        assert isinstance(database, str)

        query = ClientQuery(self, UPDATE_RECORD)
        query.ansi(database).add(int(lock)).add(int(actualize))
        query.utf(IRBIS_DELIMITER.join(record.encode()))
        with self.execute(query) as response:
            if not response.check_return_code():
                return 0

            result = response.return_code  # Новый максимальный MFN
            return result

    # noinspection DuplicatedCode
    def write_record(self, record: Record,
                     lock: bool = False,
                     actualize: bool = True,
                     dont_parse: bool = False) -> int:
        """
        Сохранение записи на сервере.

        :param record: Запись.
        :param lock: Оставить запись заблокированной?
        :param actualize: Актуализировать запись?
        :param dont_parse: Не разбирать ответ сервера?
        :return: Новый максимальный MFN.
        """
        if not self.check_connection():
            return 0

        database = record.database or self.database or throw_value_error()
        if not record:
            raise ValueError()

        assert isinstance(record, Record)
        assert isinstance(database, str)

        query = ClientQuery(self, UPDATE_RECORD)
        query.ansi(database).add(int(lock)).add(int(actualize))
        query.utf(IRBIS_DELIMITER.join(record.encode()))
        with self.execute(query) as response:
            if not response.check_return_code():
                return 0

            result = response.return_code  # Новый максимальный MFN
            if not dont_parse:
                first_line = response.utf()
                text = short_irbis_to_lines(response.utf())
                text.insert(0, first_line)
                record.database = database
                record.parse(text)
            return result

    # noinspection DuplicatedCode
    async def write_record_async(self, record: Record,
                                 lock: bool = False,
                                 actualize: bool = True,
                                 dont_parse: bool = False) -> int:
        """
        Асинхронное сохранение записи на сервере.

        :param record: Запись.
        :param lock: Оставить запись заблокированной?
        :param actualize: Актуализировать запись?
        :param dont_parse: Не разбирать ответ сервера?
        :return: Новый максимальный MFN.
        """
        if not self.check_connection():
            return 0

        database = record.database or self.database or throw_value_error()
        if not record:
            raise ValueError()

        assert isinstance(record, Record)
        assert isinstance(database, str)

        assert isinstance(record, Record)
        assert isinstance(database, str)

        query = ClientQuery(self, UPDATE_RECORD)
        query.ansi(database).add(int(lock)).add(int(actualize))
        query.utf(IRBIS_DELIMITER.join(record.encode()))
        response = await self.execute_async(query)
        response.check_return_code()
        result = response.return_code  # Новый максимальный MFN
        if not dont_parse:
            first_line = response.utf()
            text = short_irbis_to_lines(response.utf())
            text.insert(0, first_line)
            record.database = database
            record.parse(text)
        response.close()
        return result

    def write_records(self, records: List[Record]) -> bool:
        """
        Сохранение нескольких записей на сервере.
        Записи могут принадлежать разным базам.

        :param records: Записи для сохранения.
        :return: Результат.
        """
        if not self.check_connection():
            return False

        if not records:
            return True

        if len(records) == 1:
            return bool(self.write_record(records[0]))

        query = ClientQuery(self, "6")
        query.add(0).add(1)

        for record in records:
            database = record.database or self.database
            line = database + IRBIS_DELIMITER + \
                IRBIS_DELIMITER.join(record.encode())
            query.utf(line)

        with self.execute(query) as response:
            response.check_return_code()

        return True

    def write_text_file(self, *specification: FileSpecification) -> bool:
        """
        Сохранение текстового файла на сервере.

        :param specification: Спецификация (включая текст для сохранения).
        :return: Признак успешности операции.
        """
        if not self.check_connection():
            return False

        query = ClientQuery(self, READ_DOCUMENT)
        is_ok = False
        for spec in specification:
            assert isinstance(spec, FileSpecification)
            query.ansi(str(spec))
            is_ok = True
        if not is_ok:
            return False

        with self.execute(query) as response:
            if not response.check_return_code():
                return False

        return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return exc_type is None

    def __bool__(self):
        return self.connected


__all__ = ['Connection', 'NOT_CONNECTED']

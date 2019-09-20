# coding: utf-8

"""
Подключение к серверу ИРБИС64.
"""

import asyncio
import socket
from typing import Any, List, Optional, Union

from ._common import ACTUALIZE_RECORD, CREATE_DATABASE, CREATE_DICTIONARY, \
    DELETE_DATABASE, GET_MAX_MFN, FORMAT_RECORD, IRBIS_DELIMITER, \
    irbis_to_lines, irbis_event_loop, LIST_FILES, LOGICALLY_DELETED, \
    MASTER_FILE, NOP, ObjectWithError, READ_RECORD, READ_RECORD_CODES, \
    REGISTER_CLIENT, safe_str, SEARCH, SERVER_INFO, short_irbis_to_lines, \
    throw_value_error, UNREGISTER_CLIENT, UNLOCK_RECORDS, UPDATE_RECORD

from .ini import IniFile
from .query import ClientQuery
from .response import ServerResponse
from .version import ServerVersion
from .record import Record
from .search import SearchParameters
from .specification import FileSpecification


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
                         database: Optional[str] = None) -> None:
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

        import random

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
        import random

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

    def get_max_mfn(self, database: Optional[str] = None) -> int:
        """
        Получение максимального MFN для указанной базы данных.

        :param database: База данных.
        :return: MFN, который будет присвоен следующей записи.
        """

        database = database or self.database or throw_value_error()

        assert isinstance(database, str)

        with self.execute_ansi(GET_MAX_MFN, database) as response:
            response.check_return_code()
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

    def get_server_version(self) -> ServerVersion:
        """
        Получение версии сервера.

        :return: Версия сервера
        """
        query = ClientQuery(self, SERVER_INFO)
        with self.execute(query) as response:
            response.check_return_code()
            lines = response.ansi_remaining_lines()
            result = ServerVersion()
            result.parse(lines)
            if not self.server_version:
                self.server_version = result.version
            return result

    def format_record(self, script: str,
                      record: Union[Record, int]) -> str:
        """
        Форматирование записи с указанным MFN.

        :param script: Текст формата
        :param record: MFN записи либо сама запись
        :return: Результат расформатирования
        """

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
            response.check_return_code()
            result = response.utf_remaining_text().strip('\r\n')
            return result

    def list_files(self,
                   *specification: Union[FileSpecification, str]) -> List[str]:
        """
        Получение списка файлов с сервера.

        :param specification: Спецификация или маска имени файла
        (если нужны файлы, лежащие в папке текущей базы данных)
        :return: Список файлов
        """
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

    def near_master(self, filename: str) -> FileSpecification:
        """
        Файл рядом с мастер-файлом текущей базы данных.

        :param filename: Имя файла
        :return: Спецификация файла
        """

        return FileSpecification(MASTER_FILE, self.database, filename)

    def nop(self) -> None:
        """
        Пустая операция (используется для периодического
        подтверждения подключения клиента).

        :return: None
        """
        with self.execute_ansi(NOP):
            pass

    async def nop_async(self) -> None:
        """
        Асинхронная пустая операция.

        :return: None.
        """
        query = ClientQuery(self, NOP)
        response = await self.execute_async(query)
        response.close()

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

    def read_record(self, mfn: int, version: int = 0) -> Record:
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
            result = Record()
            result.database = self.database
            result.parse(text)

        if version:
            self.unlock_records([mfn])

        return result

    async def read_record_async(self, mfn: int) -> Record:
        """
        Асинхронное чтение записи.

        :param mfn: MFN считываемой записи.
        :return: Прочитанная запись.
        """
        mfn = mfn or int(throw_value_error())
        assert isinstance(mfn, int)
        query = ClientQuery(self, READ_RECORD).ansi(self.database).add(mfn)
        response = await self.execute_async(query)
        response.check_return_code(READ_RECORD_CODES)
        text = response.utf_remaining_lines()
        result = Record()
        result.database = self.database
        result.parse(text)
        response.close()
        return result

    def search(self, parameters: Any) -> List[int]:
        """
        Поиск записей.

        :param parameters: Параметры поиска (либо поисковый запрос)
        :return: Список найденных MFN
        """
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
        response.check_return_code()
        _ = response.number()  # Число найденных записей
        result = []
        while 1:
            line = response.ansi()
            if not line:
                break
            mfn = int(line)
            result.append(mfn)
        return result

    def search_count(self, expression: Any) -> int:
        """
        Количество найденных записей.

        :param expression: Поисковый запрос.
        :return: Количество найденных записей.
        """
        expression = str(expression)

        query = ClientQuery(self, SEARCH)
        query.ansi(self.database)
        query.utf(expression)
        query.add(0)
        query.add(0)
        response = self.execute(query)
        response.check_return_code()
        return response.number()

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

    def unlock_records(self, records: List[int],
                       database: Optional[str] = None) -> None:
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

    def write_record(self, record: Record,
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

        assert isinstance(record, Record)
        assert isinstance(database, str)

        assert isinstance(record, Record)
        assert isinstance(database, str)

        query = ClientQuery(self, UPDATE_RECORD)
        query.ansi(database).add(int(lock)).add(int(actualize))
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


__all__ = ['Connection']

import socket
import random

from pyirbis import *
from pyirbis.MarcRecord import MarcRecord
from pyirbis.FileSpecification import FileSpecification
from pyirbis.ClientQuery import ClientQuery
from pyirbis.ServerResponse import ServerResponse
from pyirbis.SearchParameters import SearchParameters
from pyirbis.TermInfo import TermInfo
from pyirbis.TermParameters import TermParameters
from pyirbis.Utility import iif, READ_TERMS_CODES


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

    def actualize_record(self, mfn: int, database: str = '') -> None:
        database = iif(database, self.database)
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

    def create_database(self, database: str, description: str = '', reader_access: bool = True) -> None:
        database = iif(database, self.database)
        query = ClientQuery(self, CREATE_DATABASE)
        query.ansi(database).ansi(description).add(int(reader_access))
        with self.execute(query) as response:
            response.check_return_code()

    def create_dictionary(self, database: str = '') -> None:
        database = iif(database, self.database)
        query = ClientQuery(self, CREATE_DICTIONARY)
        query.ansi(database)
        with self.execute(query) as response:
            response.check_return_code()

    def delete_database(self, database: str = '') -> None:
        database = iif(database, self.database)
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

    def format_record(self, script: str, mfn) -> str:
        """
        Форматирование записи с указанным MFN.

        :param script: Текст формата
        :param mfn: MFN записи
        :return: Результат расформатирования
        """
        query = ClientQuery(self, FORMAT_RECORD)
        query.ansi(self.database).ansi(script).add(1).add(mfn)
        with self.execute(query) as response:
            response.check_return_code()
            result = response.utf_remaining_text()
        return result

    def get_max_mfn(self, database='') -> int:
        database = iif(database, self.database)
        query = ClientQuery(self, GET_MAX_MFN)
        query.ansi(database)
        with self.execute(query) as response:
            response.check_return_code()
            result = response.return_code
        return result

    def get_server_stat(self):
        pass

    def get_server_version(self):
        pass

    def get_user_list(self):
        pass

    def list_files(self, specification: FileSpecification) -> [str]:
        query = ClientQuery(self, LIST_FILES)
        query.ansi(str(specification))
        result = []
        with self.execute(query) as response:
            lines = response.ansi_remaining_lines()
            result.extend(lines)
        return result

    def list_processes(self):
        pass

    def nop(self) -> None:
        with self.execute_ansi(NOP):
            pass

    def read_binary_file(self, specification: FileSpecification):
        pass

    def read_postings(self, parameters):
        pass

    def read_record(self, mfn: int):
        pass

    def read_terms(self, parameters: TermParameters) -> []:
        database = iif(parameters.database, self.database)
        command = READ_TERMS_REVERSE if parameters.reverse else READ_TERMS
        query = ClientQuery(self, command)
        query.ansi(database).utf(parameters.start)
        query.add(parameters.number).ansi(parameters.format)
        with self.execute(query) as response:
            response.check_return_code(READ_TERMS_CODES)
            result = TermInfo.parse(response)
            return result

    def read_text_file(self, specification: FileSpecification) -> str:
        query = ClientQuery(self, READ_DOCUMENT)
        query.ansi(str(specification))
        with self.execute(query) as response:
            result = response.ansi_remaining_text()
        return result

    def reload_dictionary(self, database: str = '') -> None:
        database = iif(database, self.database)
        with self.execute_ansi([RELOAD_DICTIONARY, database]):
            pass

    def reload_master_file(self, database: str = '') -> None:
        database = iif(database, self.database)
        with self.execute_ansi([RELOAD_MASTER_FILE, database]):
            pass

    def restart_server(self) -> None:
        with self.execute_ansi([RESTART_SERVER]):
            pass

    def search(self, parameters: SearchParameters) -> []:
        database = parameters.database
        if not database:
            database = self.database
        query = ClientQuery(self, SEARCH)
        query.ansi(database)
        query.utf(parameters.expression)
        query.add(parameters.number)
        query.add(parameters.first_record)
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

    def truncate_database(self, database: str = '') -> None:
        database = iif(database, self.database)
        with self.execute_ansi([EMPTY_DATABASE, database]):
            pass

    def unlock_database(self, database: str = '') -> None:
        database = iif(database, self.database)
        with self.execute_ansi([UNLOCK_DATABASE, database]):
            pass

    def unlock_records(self, records: [int], database: str = '') -> None:
        database = iif(database, self.database)
        query = ClientQuery(self, UNLOCK_RECORDS)
        query.ansi(database)
        for mfn in records:
            query.add(mfn)
        with self.execute(query) as response:
            response.check_return_code()

    def update_ini_file(self, lines):
        pass

    def write_record(self, record: MarcRecord, lock=False, actualize=True, dont_parse=False):
        pass

    def write_text_file(self, specification: FileSpecification):
        pass


__all__ = [IrbisConnection]

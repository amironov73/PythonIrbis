import socket
import random

from pyirbis import *
from pyirbis.MarcRecord import MarcRecord
from pyirbis.FileSpecification import FileSpecification
from pyirbis.ClientQuery import ClientQuery
from pyirbis.ServerResponse import ServerResponse
from pyirbis.SearchParameters import SearchParameters


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

    def actualize_record(self, mfn: int):
        pass

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
        response = self.execute(query)
        response.check_return_code()
        self.connected = True
        return ''

    def create_database(self, database: str, description: str, reader_access: bool):
        pass

    def create_dictionary(self, database: str):
        pass

    def delete_database(self, database: str):
        pass

    def disconnect(self):
        """
        Отключение от сервера.

        :return: Себя
        """
        if not self.connected:
            return
        query = ClientQuery(self, UNREGISTER_CLIENT)
        query.ansi(self.username)
        self.execute(query)
        self.connected = False
        return self

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
        response = self.execute(query)
        response.nop()

    def format_record(self, script: str, mfn):
        pass

    def get_max_mfn(self, database='') -> int:
        if not database:
            database = self.database
        query = ClientQuery(self, GET_MAX_MFN)
        query.ansi(database)
        response = self.execute(query)
        response.check_return_code()
        return response.return_code

    def get_server_stat(self):
        pass

    def get_server_version(self):
        pass

    def get_user_list(self):
        pass

    def list_files(self, specification: FileSpecification):
        pass

    def list_processes(self):
        pass

    def nop(self):
        self.execute_ansi(NOP)

    def read_binary_file(self, specification: FileSpecification):
        pass

    def read_postings(self, parameters):
        pass

    def read_record(self, mfn: int):
        pass

    def read_terms(self, parameters):
        pass

    def read_text_file(self, specification: FileSpecification):
        pass

    def reload_dictionary(self, database: str):
        pass

    def reload_master_file(self, database: str):
        pass

    def restart_server(self):
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

    def truncate_database(self, database: str):
        pass

    def unlock_database(self, database: str):
        pass

    def unlock_records(self, records):
        pass

    def update_ini_file(self, lines):
        pass

    def write_record(self, record: MarcRecord, lock=False, actualize=True, dont_parse=False):
        pass

    def write_text_file(self, specification: FileSpecification):
        pass


__all__ = [IrbisConnection]

import socket
import random

from pyirbis.MarcRecord import MarcRecord
from pyirbis.FileSpecification import FileSpecification
from pyirbis.ClientQuery import ClientQuery


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
        query = ClientQuery(self,'A')
        query.ansi(self.username)
        query.ansi(self.password)
        self.execute(query)
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
        query = ClientQuery(self, 'B')
        query.ansi(self.username)
        self.execute(query)
        self.connected = False
        return self

    def execute(self, query: ClientQuery):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        packet = query.encode()
        sock.send(packet)
        answer = sock.recv(32*1000)
        sock.close()

    def format_record(self, script: str, mfn):
        pass

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
        pass

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

    def search(self, parameters):
        pass

    def truncate_database(self, database: str):
        pass

    def unlock_database(self, database: str):
        pass

    def unlock_records(self, records):
        pass

    def update_ini_file(self, lines):
        pass

    def write_record(self, record: MarcRecord, lock = False, actualize = True, dont_parse = False):
        pass

    def write_text_file(self, specification: FileSpecification):
        pass

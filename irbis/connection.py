# coding: utf-8

"""
Подключение к серверу ИРБИС64.
"""

import socket
from typing import Any, List, Optional
from .query import ClientQuery
from .response import ServerResponse


class Connection:
    """
    Подключение к серверу
    """

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 6666
    DEFAULT_DATABASE = 'IBIS'

    # TODO Do we need slots here?

    __slots__ = ('host', 'port', 'username', 'password', 'database',
                 'workstation', 'client_id', 'query_id', 'connected',
                 '_stack', 'server_version', 'ini_file', 'last_error')

    def __init__(self, host: Optional[str] = None,
                 port: int = 0,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 database: Optional[str] = None,
                 workstation: str = 'C') -> None:
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
        self.ini_file: Any = None
        # self.ini_file: IniFile = IniFile()
        self.last_error = 0

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


__all__ = ['Connection']

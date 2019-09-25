# coding: utf-8

"""
Статистика работы сервера.
"""

from typing import Optional
from .response import ServerResponse


class ClientInfo:
    """
    Информация о клиенте, подключенном к серверу ИРБИС
    (не обязательно о текущем)
    """

    __slots__ = ('number', 'ip_address', 'port', 'name', 'client_id',
                 'workstation', 'registered', 'acknowledged',
                 'last_command', 'command_number')

    def __init__(self):
        self.number: Optional[str] = None
        self.ip_address: Optional[str] = None
        self.port: Optional[str] = None
        self.name: Optional[str] = None
        self.client_id: Optional[str] = None
        self.workstation: Optional[str] = None
        self.registered: Optional[str] = None
        self.acknowledged: Optional[str] = None
        self.last_command: Optional[str] = None
        self.command_number: Optional[str] = None

    def __str__(self):
        return ' '.join([self.number, self.ip_address, self.port, self.name,
                         self.client_id, self.workstation,
                         self.registered, self.acknowledged,
                         self.last_command, self.command_number])


class ServerStat:
    """
    Статистика работы ИРБИС-сервера
    """

    __slots__ = 'running_clients', 'client_count', 'total_command_count'

    def __init__(self):
        self.running_clients: [ClientInfo] = []
        self.client_count: int = 0
        self.total_command_count: int = 0

    # noinspection DuplicatedCode
    def parse(self, response: ServerResponse) -> None:
        """
        Parse the server response for the stat.

        :param response: Server response
        :return: None
        """

        self.total_command_count = response.number()
        self.client_count = response.number()
        lines_per_client = response.number()
        if not lines_per_client:
            return

        for _ in range(self.client_count):
            client = ClientInfo()
            client.number = response.ansi()
            client.ip_address = response.ansi()
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


__all__ = ['ClientInfo', 'ServerStat']

# coding: utf-8

"""
Версия сервера.
"""

from typing import List


class ServerVersion:
    """
    Информация о версии сервера, числе подключенных/разрешенных клиентов
    и организации, на которую зарегистрирован сервер.
    """

    def __init__(self):
        self.organization = ''
        self.version = ''
        self.max_clients = 0
        self.connected_clients = 0

    def parse(self, lines: List[str]) -> None:
        """
        Parse the text.

        :param lines: Text to parse
        :return: None
        """
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
        buffer = [self.organization,
                  self.version,
                  str(self.connected_clients),
                  str(self.max_clients)]
        return '\n'.join(buffer)


__all__ = ['ServerVersion']

# coding: utf-8

"""
Серверные процессы.
"""


class Process:
    """
    Информация о запущенном на сервере процессе.
    """

    __slots__ = ('number', 'ip_address', 'name', 'client_id', 'workstation',
                 'started', 'last_command', 'command_number',
                 'process_id', 'state')

    def __init__(self) -> None:
        self.number: str = ''
        self.ip_address: str = ''
        self.name: str = ''
        self.client_id: str = ''
        self.workstation: str = ''
        self.started: str = ''
        self.last_command: str = ''
        self.command_number: str = ''
        self.process_id: str = ''
        self.state: str = ''

    def __str__(self):
        buffer = [self.number, self.ip_address, self.name, self.client_id,
                  self.workstation, self.started, self.last_command,
                  self.command_number, self.process_id, self.state]
        return '\n'.join(x for x in buffer if x)


__all__ = ['Process']

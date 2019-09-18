# coding: utf-8

"""
Клиентский запрос.
"""

from typing import Union, Optional
from ._common import ANSI, UTF, prepare_format


class ClientQuery:
    """
    Клиентский запрос.
    """

    __slots__ = ('_memory',)

    def __init__(self, connection, command: str) -> None:
        self._memory: bytearray = bytearray()
        self.ansi(command)
        self.ansi(connection.workstation)
        self.ansi(command)
        self.add(connection.client_id)
        self.add(connection.query_id)
        connection.query_id += 1
        self.ansi(connection.password)
        self.ansi(connection.username)
        self.new_line()
        self.new_line()
        self.new_line()

    def add(self, number: int) -> 'ClientQuery':
        """
        Добавление целого числа.

        :param number: Число
        :return: Self
        """
        return self.ansi(str(number))

    def ansi(self, text: Optional[str]) -> 'ClientQuery':
        """
        Добавление строки в кодировке ANSI.

        :param text: Добавляемая строка
        :return: Self
        """
        return self.append(text, ANSI)

    def append(self, text: Optional[str], encoding: str) -> 'ClientQuery':
        """
        Добавление строки в указанной кодировке.

        :param text: Добавляемая строка
        :param encoding: Кодировка
        :return: Self
        """
        if text is not None:
            self._memory.extend(text.encode(encoding))
        self.new_line()
        return self

    def format(self, format_specification: Optional[str]) \
            -> Union['ClientQuery', bool]:
        """
        Добавление строки формата, предварительно подготовив её.
        Также добавляется перевод строки.

        :param format_specification: Добавляемая строка формата.
            Может быть пустой.
        :return: Self
        """
        if format_specification is None:
            self.new_line()
            return False

        prepared = prepare_format(format_specification)
        if format_specification[0] == '@':
            self.ansi(prepared)
        elif format_specification[0] == '!':
            self.utf(prepared)
        else:
            self.utf('!' + prepared)
        return self

    def new_line(self) -> 'ClientQuery':
        """
        Перевод строки.

        :return: Self
        """
        self._memory.append(0x0A)
        return self

    def utf(self, text: Optional[str]) -> 'ClientQuery':
        """
        Добавление строки в кодировке UTF-8.

        :param text: Добавляемая строка
        :return: Self
        """
        return self.append(text, UTF)

    def encode(self) -> bytes:
        """
        Выдача, что получилось в итоге.

        :return: Закодированный запрос
        """
        prefix = (str(len(self._memory)) + '\n').encode(ANSI)
        return prefix + self._memory


__all__ = ['ClientQuery']

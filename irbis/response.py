# coding: utf-8

"""
Ответ сервера.
"""

import socket
from typing import Any, List, Optional
from ._common import ANSI, ObjectWithError, UTF


class ServerResponse:
    """
    Ответ сервера.
    """

    __slots__ = ('_memory', '_view', '_pos', 'command', 'client_id',
                 'query_id', 'length', 'version', 'return_code', '_conn')

    def __init__(self, conn: ObjectWithError) -> None:
        self._conn: ObjectWithError = conn
        self._memory: bytearray = bytearray()
        self._view: memoryview = memoryview(bytearray())
        self._pos: int = 0  # Текущая позиция при чтении
        self.command: str = ''
        self.client_id: int = 0
        self.query_id: int = 0
        self.length: int = 0
        self.version: str = ''
        self.return_code: int = 0

    def read_data(self, sock: socket.socket) -> None:
        """
        Считывание ответа сервера из сокета.

        :param sock: Сокет для чтения.
        :return: None.
        """
        while sock:
            buffer = sock.recv(4096)
            if not buffer:
                break
            self._memory.extend(buffer)
        sock.close()
        self._view = memoryview(self._memory)

    async def read_data_async(self, sock: Any) -> None:
        """
        Асинхронное считывание ответа из сокета.

        :param sock: Сокет для чтения.
        :return: None.
        """
        while True:
            buffer = await sock.read(4096)
            if not buffer:
                break
            self._memory.extend(buffer)
        self._view = memoryview(self._memory)

    def initial_parse(self) -> None:
        """
        Разбор постоянной начальной части ответа от сервера.

        :return: None.
        """
        self.command = self.ansi()
        self.client_id = self.number()
        self.query_id = self.number()
        self.length = self.may_be_number()
        self.version = self.ansi()
        self.return_code = 0
        for _ in range(5):
            self.read()

    def ansi(self) -> str:
        """
        Считывание одной строки в кодировке ANSI.

        :return: Строка (возможно, пустая)
        """
        # noinspection PyTypeChecker
        return str(self.read(), ANSI)  # type: ignore

    def ansi_n(self, count: int) -> List[str]:
        """
        Считывание не менее указанного количества строк
        в кодировке ANSI.

        :param count: Сколько строк надо
        :return: Список строк или None
        """
        result = []
        for _ in range(count):
            line = self.ansi()
            if not line:
                return []
            result.append(line)
        return result

    def ansi_remaining_text(self) -> str:
        """
        Получение всего оставшегося текста ответа сервера
        как строки в кодировке ANSI.

        :return: Строка (возможно, пустая)
        """
        # noinspection PyTypeChecker
        return str(self._view[self._pos:], ANSI)  # type: ignore

    def ansi_remaining_lines(self) -> List[str]:
        """
        Получение всего оставшегося текста ответа сервера
        как списка строк в кодировке ANSI.

        :return: Список строк (возможно, пустой)
        """
        result = []
        while True:
            line = self.ansi()
            if not line:
                break
            result.append(line)
        return result

    def check_return_code(self, allowed: List[int] = None) -> bool:
        """
        Проверка кода возврата. Если код меньше нуля,
        генерируется IrbisError.
        Можно указать допустимые значения кода.

        :param allowed: Допустимые отрицательные значения (опционально).
        :return: Результат проверки кода возврата.
        """
        if allowed is None:
            allowed = []

        if self.get_return_code() < 0:
            if self.return_code not in allowed:
                #  raise IrbisError(self.return_code)
                return False

        return True

    def close(self) -> None:
        """
        Закрытие сокета.

        :return: None
        """

        # Пока ничего не делаем

    def get_binary_file(self) -> Optional[bytearray]:
        """
        Получение двоичного файла с сервера.

        :return: Содержимое файла или None
        """

        preamble = bytearray(b'IRBIS_BINARY_DATA')
        index = self._memory.find(preamble)
        if index < 0:
            return None
        return self._memory[index + len(preamble):]

    def get_return_code(self) -> int:
        """
        Считывание кода возврата без его проверки.

        :return: Код возврата
        """

        self.return_code = self.number()
        if self.return_code < 0:
            self._conn.last_error = self.return_code
        return self.return_code

    def nop(self) -> None:
        """
        Пустая операция (не нужна).

        :return: None
        """

    def may_be_number(self) -> int:
        """
        Считывание строки, в которой может быть число,
        но может быть и что-нибудь иное.

        :return: Считанное число либо 0, если строку
        не удалось интерпретировать как число.
        """

        result = 0
        try:
            result = int(self.ansi())
        except ValueError:
            pass
        return result

    def number(self) -> int:
        """
        Считывание строки, в которой ожидается число (возможно,
        со знаком) в десятеричной системе счисления.

        :return: Считанное число
        """
        # noinspection PyTypeChecker
        return int(self.read())  # type: ignore

    def read(self) -> memoryview:
        """
        Считываем строку в сыром виде.

        :return: memoryview на сырые байты строки.
        """

        length = len(self._memory)
        start = self._pos
        if self._pos >= length:
            return self._view[0:0]

        while True:
            position = self._memory.find(0x0D, start)
            if position < 0:
                result = self._view[self._pos:]
                self._pos = length
                return result

            plus1 = position + 1
            if plus1 < length:
                if self._memory[plus1] == 0x0A:
                    result = self._view[self._pos:position]
                    self._pos = plus1 + 1
                    return result
                start = plus1

    def utf(self) -> str:
        """
        Считывание одной строки в кодировке UTF-8.

        :return: Строка (возможно, пустая)
        """
        # noinspection PyTypeChecker
        return str(self.read(), UTF)  # type: ignore

    def utf_n(self, count: int) -> List[str]:
        """
        Считывание не менее указанного количества строк
        в кодировке UTF-8.

        :param count: Сколько строк надо
        :return: Список строк или None
        """
        result = []
        for _ in range(count):
            line = self.utf()
            if not line:
                return []
            result.append(line)
        return result

    def utf_remaining_text(self) -> str:
        """
        Получение всего оставшегося текста ответа сервера
        как строки в кодировке UTF-8.

        :return: Строка (возможно, пустая)
        """
        # noinspection PyTypeChecker
        return str(self._view[self._pos:], UTF)  # type: ignore

    def utf_remaining_lines(self) -> List[str]:
        """
        Получение всего оставшегося текста ответа сервера
        как списка строк в кодировке UTF-8.

        :return: Список строк (возможно, пустой)
        """

        result = []
        while True:
            line = self.utf()
            if not line:
                break
            result.append(line)
        return result

    def __str__(self):
        return str(self.return_code)

    def __enter__(self):
        # Пока не знаю, что делать
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return exc_type is None


__all__ = ['ServerResponse']

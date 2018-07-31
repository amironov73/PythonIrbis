import socket

from pyirbis import ANSI, UTF


class ServerResponse:
    """
    Ответ сервера.
    """

    def __init__(self, sock: socket.socket):
        self._memory = bytearray()
        while sock:
            buffer = sock.recv(4096)
            if not buffer:
                break
            self._memory.extend(buffer)
        sock.close()
        self.command = self.ansi()
        self.clientId = self.number()
        self.queryId = self.number()
        self.return_code = 0
        for i in range(7):
            self.read()

    def ansi(self) -> str:
        return self.read().decode(ANSI)

    def ansi_n(self, count: int) -> [str]:
        """
        Считывание не менее указанного количества строк.

        :param count: Сколько строк надо
        :return: Список строк или None
        """
        result = []
        for i in range(count):
            line = self.ansi()
            if len(line) == 0:
                return None
            result.append(line)
        return result

    def ansi_remaining_text(self) -> str:
        return self._memory.decode(ANSI)

    def ansi_remaining_lines(self):
        result = []
        while True:
            line = self.ansi()
            if len(line) == 0:
                break
            result.append(line)
        return result

    def check_return_code(self, allowed=[]):
        if self.get_return_code() < 0:
            if self.return_code not in allowed:
                raise IOError

    def close(self) -> None:
        # Пока ничего не делаем
        pass

    def get_return_code(self) -> int:
        self.return_code = self.number()
        return self.return_code

    def nop(self):
        pass

    def number(self) -> int:
        return int(self.ansi())

    def read(self) -> bytearray:
        """
        Считываем строку в сыром виде.

        :return: Считанная строка.
        """
        result = bytearray()
        while True:
            if not len(self._memory):
                break
            c = self._memory.pop(0)
            if c == 0x0D:
                if not len(self._memory):
                    break
                c = self._memory.pop(0)
                if c == 0x0A:
                    break
            result.append(c)
        return result

    def utf(self) -> str:
        return self.read().decode(UTF)

    def utf_n(self, count: int) -> [str]:
        """
        Считывание не менее указанного количества строк.

        :param count: Сколько строк надо
        :return: Список строк или None
        """
        result = []
        for i in range(count):
            line = self.utf()
            if len(line) == 0:
                return None
            result.append(line)
        return result

    def utf_remaining_text(self) -> str:
        return self._memory.decode(UTF)

    def utf_remaining_lines(self):
        result = []
        while True:
            line = self.utf()
            if len(line) == 0:
                break
            result.append(line)
        return result

    def __str__(self):
        return str(self.return_code)

    def __enter__(self):
        # Пока не знаю, что делать
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Пока не знаю, что делать
        return self


__all__ = [ServerResponse]
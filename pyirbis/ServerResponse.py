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

    def check_return_code(self, allowed=[]):
        if self.get_return_code() < 0:
            if self.return_code not in allowed:
                raise IOError

    def close(self) -> None:
        self.socket.close()

    def get_return_code(self) -> int:
        self.return_code = self.number()
        return self.return_code

    def nop(self):
        pass

    def number(self) -> int:
        return int(self.ansi())

    def read(self) -> bytearray:
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

    def __str__(self):
        return str(self.return_code)


__all__ = [ServerResponse]
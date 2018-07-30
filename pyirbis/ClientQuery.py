from pyirbis import ANSI, UTF


class ClientQuery:
    """
    Клиентский запрос.
    """

    def __init__(self, connection, command: str):
        self._memory = bytearray()
        self.ansi(command)
        self.ansi(connection.workstation)
        self.ansi(command)
        self.add(connection.clientId)
        self.add(connection.queryId)
        connection.queryId += 1
        self.ansi(connection.password)
        self.ansi(connection.username)
        self.new_line()
        self.new_line()
        self.new_line()

    def add(self, number: int):
        """
        Добавление целого числа.

        :param number: Число
        :return: Себя
        """
        return self.ansi(str(number))

    def ansi(self, text: str):
        """
        Добавление строки в кодировке ANSI.

        :param text: Добавляемая строка
        :return: Себя
        """
        return self.append(text, ANSI)

    def append(self, text: str, encoding: str):
        """
        Добавление строки в указанной кодировке.

        :param text: Добавляемая строка
        :param encoding: Кодировка
        :return: Себя
        """
        self._memory.extend(text.encode(encoding))
        self.new_line()
        return self

    def new_line(self):
        self._memory.append(0x0A)
        return self

    def utf(self, text: str):
        """
        Добавление строки в кодировке UTF-8.

        :param text: Добавляемая строка
        :return: Себя
        """
        return self.append(text, UTF)

    def encode(self):
        """
        Выдача, что получилось в итоге.

        :return: Закодированный запрос
        """
        prefix = (str(len(self._memory)) + '\n').encode(ANSI)
        return prefix + self._memory

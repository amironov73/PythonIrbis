# coding: utf-8

"""
Работа с MNU-файлами.
"""

from typing import List, Optional
from ._common import ANSI, STOP_MARKER


class MenuEntry:
    """
    Пара строк в меню.
    """

    __slots__ = 'code', 'comment'

    def __init__(self, code: str = '', comment: str = '') -> None:
        self.code: str = code
        self.comment: str = comment

    def __str__(self):
        if self.comment:
            return self.code + ' - ' + self.comment
        return self.code

    def __repr__(self):
        return self.__str__()


class MenuFile:
    """
    Файл меню.
    """

    __slots__ = ('entries',)

    def __init__(self) -> None:
        self.entries: List[MenuEntry] = []

    def add(self, code: str, comment: str = ''):
        """
        Add an entry to the menu.

        :param code: Code
        :param comment: Comment
        :return: Self
        """
        entry = MenuEntry(code, comment)
        self.entries.append(entry)
        return self

    def get_entry(self, code: str) -> Optional[MenuEntry]:
        """
        Get an entry for the specified code.

        :param code: Code to search
        :return: Found entry or None
        """

        code = code.lower()
        for entry in self.entries:
            if entry.code.lower() == code:
                return entry

        code = code.strip()
        for entry in self.entries:
            if entry.code.lower() == code:
                return entry

        code = MenuFile.trim_code(code)
        for entry in self.entries:
            if entry.code.lower() == code:
                return entry

        return None

    def get_value(self, code: str,
                  default_value: Optional[str] = None) -> Optional[str]:
        """
        Get value for the specified code.

        :param code: Code to search
        :param default_value: Default value
        :return: Found or default value
        """

        entry = self.get_entry(code)
        result = entry.comment if entry else default_value
        return result

    def parse(self, lines: List[str]) -> None:
        """
        Parse the text for menu entries.

        :param lines: Text to parse
        :return: None
        """

        i = 0
        while i + 1 < len(lines):
            code = lines[i]
            comment = lines[i + 1]
            if code.startswith(STOP_MARKER):
                break
            self.add(code, comment)
            i += 2

    def save(self, filename: str) -> None:
        """
        Save the menu to the specified file.

        :param filename: Name of the file
        :return: None
        """

        with open(filename, 'wt', encoding=ANSI) as stream:
            for entry in self.entries:
                stream.write(entry.code + '\n')
                stream.write(entry.comment + '\n')
            stream.write(STOP_MARKER + '\n')

    @staticmethod
    def trim_code(code: str) -> str:
        """
        Trim the code.

        :param code: code to process
        :return: Trimmed code
        """

        result = code.strip(' -=:')
        return result

    def __str__(self):
        result = []
        for entry in self.entries:
            result.append(entry.code)
            result.append(entry.comment)
        result.append(STOP_MARKER)
        return '\n'.join(result)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        yield from self.entries

    def __getitem__(self, item: str):
        return self.get_value(item)


def load_menu(filename: str) -> MenuFile:
    """
    Чтение меню из файла.

    :param filename: Имя файла
    :return: Меню
    """
    with open(filename, 'rt', encoding=ANSI) as stream:
        result = MenuFile()
        lines = stream.readlines()
        result.parse(lines)
        return result


__all__ = ['load_menu', 'MenuEntry', 'MenuFile']

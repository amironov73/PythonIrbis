# coding: utf-8

"""
Класс, умеющий сохранять свое содержимое
в текстовом файле.
"""

from irbis._common import ANSI


class Saveable:
    """
    A class that can store its content in a text file.
    """

    def save(self, filename: str) -> None:
        """
        Save the instance to the specified file.

        :param filename: Name of the file
        :return: None
        """

        with open(filename, 'wt', encoding=ANSI) as stream:
            text = str(self)
            stream.write(text)

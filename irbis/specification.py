# coding: utf-8

"""
Спецификация файла.
"""

from typing import Optional
from ._common import SYSTEM


class FileSpecification:
    """
    Путь на файл path.database.filename
    path – код путей:
    0 – общесистемный путь.
    1 – путь размещения сведений о базах данных сервера ИРБИС64
    2 – путь на мастер-файл базы данных.
    3 – путь на словарь базы данных.
    10 – путь на параметрию базы данных.
    database – имя базы данных
    filename – имя требуемого файла с расширением
    В случае чтения ресурса по пути 0 и 1 имя базы данных не задается.

    В общем случае может выглядеть так:

    path.database.@filename
    или
    path.database.&filename&content

    где @ означает двоичный файл
    & означает наличие содержимого и отделяет имя файла от его содержимого

    """

    __slots__ = 'binary', 'path', 'database', 'filename', 'content'

    def __init__(self, path: int, database: Optional[str],
                 filename: str) -> None:
        self.binary: bool = False
        self.path: int = path
        self.database: Optional[str] = database
        self.filename: str = filename
        self.content: Optional[str] = None

    @staticmethod
    def system(filename: str) -> 'FileSpecification':
        """
        Создание спецификации файла, лежащего в системной папке ИРБИС64.

        :param filename: Имя файла
        :return: Спецификация файла
        """
        return FileSpecification(SYSTEM, None, filename)

    @staticmethod
    def parse(text: str) -> 'FileSpecification':
        """
        Разбор текстового представления спецификации.

        :param text: Текст для разбора.
        :return: Спецификация.
        """
        parts = text.split('.', 2)
        result = FileSpecification(int(parts[0]), parts[1], parts[2])
        if result.filename.startswith('@'):
            result.filename = result.filename[1:]
            result.binary = True
        if result.filename.startswith('&'):
            parts = result.filename[1:].split('&', 1)
            result.filename = parts[0]
            result.content = parts[1]
        return result

    def __str__(self):
        result = self.filename

        if self.binary:
            result = '@' + self.filename
        else:
            if self.content:
                result = '&' + self.filename

        if self.path == 0 or self.path == 1:
            result = str(self.path) + '..' + result
        else:
            result = str(self.path) + '.' + self.database + '.' + result

        if self.content:
            result = result + '&' + str(self.content)

        return result


__all__ = ['FileSpecification']

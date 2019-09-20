# coding: utf-8

"""
Информация о базах данных.
"""

from typing import List, Optional
from ._common import SHORT_DELIMITER
from .response import ServerResponse


class DatabaseInfo:
    """
    Информация о базе данных ИРБИС.
    """

    __slots__ = ('name', 'description', 'max_mfn', 'logically_deleted',
                 'physically_deleted', 'nonactualized', 'locked_records',
                 'database_locked', 'read_only')

    def __init__(self, name: Optional[str] = None,
                 description: Optional[str] = None) -> None:
        self.name: Optional[str] = name
        self.description: Optional[str] = description
        self.max_mfn: int = 0
        self.logically_deleted: List[int] = []
        self.physically_deleted: List[int] = []
        self.nonactualized: List[int] = []
        self.locked_records: List[int] = []
        self.database_locked: bool = False
        self.read_only: bool = False

    @staticmethod
    def _parse(line: str) -> List[int]:
        if not line:
            return []
        return [int(x) for x in line.split(SHORT_DELIMITER) if x]

    def parse(self, response: ServerResponse) -> None:
        """
        Parse the server response for database info.

        :param response: Response to parse
        :return: None
        """
        self.logically_deleted = self._parse(response.ansi())
        self.physically_deleted = self._parse(response.ansi())
        self.nonactualized = self._parse(response.ansi())
        self.locked_records = self._parse(response.ansi())
        self.max_mfn = int(response.ansi())
        self.database_locked = bool(int(response.ansi()))

    def __str__(self):
        if not self.description:
            return self.name or '(none)'
        return self.name + ' - ' + self.description


__all__ = ['DatabaseInfo']

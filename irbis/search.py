# coding: utf-8

"""
Всё, связанное с поиском.
"""

from typing import Optional
from ._common import safe_int


class FoundLine:
    """
    Found item in search answer.
    """

    __slots__ = ('mfn', 'description')

    def __init__(self) -> None:
        self.mfn: int = 0
        self.description: Optional[str] = None

    def parse_line(self, line: str) -> None:
        """
        Разбор серверного представления найденной записи.

        :param line: Строка с найденной записью.
        :return: None.
        """
        parts = line.split('#', 2)
        self.mfn = safe_int(parts[0])
        if len(parts) > 1:
            self.description = parts[1]

    def __str__(self):
        return f"{self.mfn}#{self.description}"


class SearchParameters:
    """
    Parameters for search request.
    """

    __slots__ = ('database', 'first', 'format', 'max_mfn', 'min_mfn',
                 'number', 'expression', 'sequential', 'filter', 'utf')

    def __init__(self, expression: Optional[str] = None,
                 number: int = 0) -> None:
        self.database: Optional[str] = None
        self.first: int = 1
        self.format: Optional[str] = None
        self.max_mfn: int = 0
        self.min_mfn: int = 0
        self.number: int = number
        self.expression = expression
        self.sequential: Optional[str] = None
        self.filter: Optional[str] = None
        self.utf = False

    def __str__(self):
        return self.expression


__all__ = ['FoundLine', 'SearchParameters']

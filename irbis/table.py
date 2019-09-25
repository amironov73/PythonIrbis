# coding: utf-8

"""
Печать таблиц.
"""

from typing import Optional


class TableDefinition:
    """
    Определение таблицы, данные для команды TableCommand
    """

    __slots__ = ('database', 'table', 'headers', 'mode', 'search',
                 'min_mfn', 'max_mfn', 'sequential', 'mfn_list')

    def __init__(self):
        self.database: Optional[str] = None
        self.table: Optional[str] = None
        self.headers: [str] = []
        self.mode: Optional[str] = None
        self.search: Optional[str] = None
        self.min_mfn: int = 0
        self.max_mfn: int = 0
        self.sequential: Optional[str] = None
        self.mfn_list: [int] = []


__all__ = ['TableDefinition']

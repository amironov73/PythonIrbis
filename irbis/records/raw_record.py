# coding: utf-8

"""
Модуль реализующий объектно-ориентированное представление записи
с нераскодированными полями/подполями.
"""

from typing import TYPE_CHECKING
from irbis.records.abstract import AbstractRecord
if TYPE_CHECKING:
    from typing import List


class RawRecord(AbstractRecord):
    """
    Запись с нераскодированными полями/подполями.
    """
    __slots__ = 'database', 'mfn', 'status', 'version', 'fields'
    fields: 'List[str]'

    def __init__(self, *fields: str) -> None:
        self.field_type = str
        super().__init__(*fields)

    def clone_fields(self) -> 'List[str]':
        return self.fields.copy()

    def parse_line(self, line: str) -> None:
        self.fields.append(line)

    def __iter__(self):
        yield from self.fields

# coding: utf-8

"""
Работа с подполями.
"""

from typing import TYPE_CHECKING
from irbis.abstract import Hashable
if TYPE_CHECKING:
    from typing import Dict, List, Optional

    SubFieldList = List['SubField']
    SubFieldDict = Dict[str, str]


class SubField(Hashable):
    """
    MARC record subfield with code and text value.
    """

    DEFAULT_CODE = '\0'

    __slots__ = 'code', 'value'

    def __init__(self, code: str = DEFAULT_CODE,
                 value: 'Optional[str]' = None) -> None:
        code = code or SubField.DEFAULT_CODE
        self.code: str = code.lower()
        self.value: 'Optional[str]' = value

    def assign_from(self, other: 'SubField') -> None:
        """
        Присваивание от другого поля: код и значение
        берутся от другого подполя.

        :param other: Другое подполе
        :return: None
        """
        self.code = other.code
        self.value = other.value

    def clone(self) -> 'SubField':
        """
        Клонирование подполя.

        :return: Клон подполя
        """
        return SubField(self.code, self.value)

    @property
    def data(self):
        return self.value

    def __str__(self):
        if self.code == self.DEFAULT_CODE:
            return ''
        return '^' + self.code + (self.value or '')

    def __bool__(self):
        return self.code != self.DEFAULT_CODE and bool(self.value)

    def __hash__(self):
        return hash((self.code, self.value))

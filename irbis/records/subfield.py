# coding: utf-8

"""
Работа с подполями.
"""

from typing import TYPE_CHECKING
from irbis.abstract import Hashable
from irbis.records.abstract import ValueMixin
if TYPE_CHECKING:
    from typing import List, Optional

    Value = Optional[str]
    SubFieldList = List['SubField']


class SubField(Hashable, ValueMixin):
    """
    MARC record subfield with code and text value.
    """

    DEFAULT_CODE = '\0'

    __slots__ = 'code', 'value'

    def __init__(self, code: str = DEFAULT_CODE,
                 value: 'Value' = None) -> None:
        self.code: str = self.validate_code(code) or SubField.DEFAULT_CODE
        self.value: 'Value' = self.validate_value(value)

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
        """
        Динамическое свойство извлечения данных в представлении стандартных
        типов данных Python.

        :return: строка со значением подполя
        """
        return self.value

    def __str__(self):
        if self.code == self.DEFAULT_CODE:
            return ''
        return '^' + self.code + (self.value or '')

    def __bool__(self):
        return self.code != self.DEFAULT_CODE and bool(self.value)

    def __hash__(self):
        return hash((self.code, self.value))

    @staticmethod
    def validate_code(code: str) -> str:
        """
        Валидация кода подполя на тип (строка) и длинну (1 символ)

        :code: код подполя
        :return: код подполя
        """
        if isinstance(code, str) is False:
            raise ValueError('Код подполя должен быть строкой')
        if len(code) != 1:
            raise ValueError('Код подполя должен быть односимвольным')
        return code.lower()

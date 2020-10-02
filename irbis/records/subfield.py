# coding: utf-8

"""
Работа с подполями.
"""

from typing import TYPE_CHECKING
from irbis.abstract import Hashable
if TYPE_CHECKING:
    from typing import Dict, List, Optional, Union

    SubFieldList = List['SubField']
    SubFieldDict = Dict[str, Union[str, List[str]]]


class SubField(Hashable):
    """
    MARC record subfield with code and text value.
    """

    DEFAULT_CODE = '\0'

    __slots__ = 'code', 'value'

    def __init__(self, code: str = DEFAULT_CODE,
                 value: 'Optional[str]' = None) -> None:
        self.code: str = self.validate_code(code) or SubField.DEFAULT_CODE
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

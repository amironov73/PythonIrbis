# coding: utf-8

"""
Модуль реализующий абстрактные классы пакета irbis.records
"""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING
from irbis._common import LOGICALLY_DELETED, PHYSICALLY_DELETED
if TYPE_CHECKING:
    from typing import Any, List, Optional


class ValueMixin:
    """
    Примесь для проверки атрибута value
    """
    @staticmethod
    def validate_value(value: 'Optional[str]') -> 'Optional[bool]':
        """
        Валидация Field.value и SubField.value

        :value: значение
        """
        if value is None:
            return True
        if isinstance(value, str) and value:
            return True
        message = 'value должно быть непустой строкой или None'
        raise TypeError(message)


class AbstractRecord:
    """
    Абстрактный класс с общими свойствами и методами для классов Record
    и RawRecord.
    """
    __metaclass__ = ABCMeta
    field_type: 'Any'

    @abstractmethod
    def __init__(self, *args: 'Any'):
        self.database: 'Optional[str]' = None
        self.mfn = 0
        self.version = 0
        self.status = 0
        self.fields: 'Any' = []
        self.set_values(*args)

    def clear(self) -> 'AbstractRecord':
        """
        Очистка записи (удаление всех полей).

        :return: Self
        """
        self.fields.clear()
        return self

    def clone(self) -> 'AbstractRecord':
        """
        Клонирование записи.

        :return: Полный клон записи
        """
        result = self.__class__()
        result.database = self.database
        result.mfn = self.mfn
        result.status = self.status
        result.version = self.version
        result.fields = self.clone_fields()
        return result

    @abstractmethod
    def clone_fields(self) -> 'List[Any]':
        """
        Абстрактный метод клонирования полей записи
        :return: список полей
        """

    def encode(self) -> 'List[str]':
        """
        Кодирование записи в серверное представление.

        :return: Список строк
        """
        result = [str(self.mfn) + '#' + str(self.status),
                  '0#' + str(self.version)]
        for field in self.fields:
            result.append(str(field))
        return result

    def is_deleted(self) -> bool:
        """
        Удалена ли запись?
        :return: True для удаленной записи
        """
        return (self.status & (LOGICALLY_DELETED | PHYSICALLY_DELETED)) != 0

    def parse(self, text: 'List[str]') -> None:
        """
        Разбор текстового представления записи (в серверном формате).

        :param text: Список строк
        :return: None
        """
        if text:
            line = text[0]
            parts = line.split('#')
            self.mfn = int(parts[0])
            if len(parts) != 1 and parts[1]:
                self.status = int(parts[1])
            line = text[1]
            parts = line.split('#')
            self.version = int(parts[1])
            self.fields.clear()
            for line in text[2:]:
                if line:
                    self.parse_line(line)
        else:
            raise ValueError('text argument is empty')

    @abstractmethod
    def parse_line(self, line: str) -> None:
        """
        Абстрактный метод разбора строки из текстового представления записи
        (в серверном формате). Реализуется у дочерних классов Record
        и RawRecord.

        :param line: строка
        :return: None
        """

    def remove_at(self, index: int) -> 'AbstractRecord':
        """
        Удаление поля в указанной позиции.

        :param index: Позиция для удаления.
        :return: self
        """
        assert 0 <= index < len(self.fields)

        self.fields.remove(self.fields[index])
        return self

    def reset(self) -> 'AbstractRecord':
        """
        Сбрасывает состояние записи, отвязывая её от базы данных.
        Поля при этом остаются нетронутыми.
        :return: Self.
        """
        self.mfn = 0
        self.status = 0
        self.version = 0
        self.database = None
        return self

    @abstractmethod
    def set_values(self, *args):
        """
        Абстрактный метод, установливающий self.fields. Реализуется
        у дочерних классов.

        :param args: Аргументы для [пере]создания полей
        :return: ничего
        """

    def __bool__(self):
        return bool(len(self.fields))

    def __len__(self):
        return len(self.fields)

    def __str__(self):
        result = [str(field) for field in self.fields]
        return '\n'.join(result)

# coding: utf-8

"""
Работа с записями, полями, подполями.
"""

from abc import ABCMeta, abstractmethod
from typing import cast, TYPE_CHECKING
from irbis._common import LOGICALLY_DELETED, PHYSICALLY_DELETED
from irbis.abstract import DictLike, Hashable
from irbis.records.field import Field
from irbis.records.subfield import SubField
if TYPE_CHECKING:
    from typing import Any, List, Optional, Set, Union, Type
    from irbis.records.field import FieldList, FieldValue

    RecordValue = Union[Field, FieldList, FieldValue, List[str]]


class AbstractRecord:
    """
    Абстрактный класс с общими свойствами и методами для классов Record
    и RawRecord.
    """
    __metaclass__ = ABCMeta
    field_type: 'Any'

    @abstractmethod
    def __init__(self, *fields: 'Union[Field, str]'):
        self.database: 'Optional[str]' = None
        self.mfn = 0
        self.version = 0
        self.status = 0
        self.fields: 'Any' = []
        if all((isinstance(f, self.field_type) for f in fields)):
            self.fields += list(fields)
        else:
            message = f'All args must be {self.field_type.__name__} type'
            raise TypeError(message)

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
        result = RawRecord()
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

    def __bool__(self):
        return bool(len(self.fields))

    def __len__(self):
        return len(self.fields)

    def __str__(self):
        result = [str(field) for field in self.fields]
        return '\n'.join(result)


class Record(AbstractRecord, DictLike, Hashable):
    """
    MARC record with MFN, status, version and fields.
    """
    __slots__ = 'database', 'mfn', 'version', 'status', 'fields'
    fields: 'List[Field]'

    def __init__(self, *fields: 'Field') -> None:
        self.field_type: 'Type[Field]' = Field
        super().__init__(*fields)

    def add(self, tag: int, value: 'Union[str, SubField]' = None) \
            -> 'Field':
        """
        Добавление поля (возможно, с значением и подполями) к записи.

        :param tag: Метка поля.
        :param value: Значение поля (опционально)
        :return: Свежедобавленное поле
        """
        assert tag > 0
        field = self.field_type(tag, value)

        if field in self.fields:
            raise ValueError(f'Field "{field}" already added')
        self.fields.append(field)
        return field

    def add_non_empty(self, tag: int,
                      value: 'Union[str, SubField]') -> 'Record':
        """
        Добавление поля, если его значение не пустое.

        :param tag: Метка поля.
        :param value: Значение поля (опционально).
        :return: Self
        """
        assert tag > 0

        if value:
            if isinstance(value, str):
                field = self.field_type(tag, value)
            else:
                field = self.field_type(tag)
                if isinstance(value, SubField):
                    field.subfields.append(value)

            self.fields.append(field)

        return self

    def all(self, tag: int) -> 'FieldList':
        """
        Список полей с указанной меткой.

        :param tag: Тег
        :return: Список полей (возможно, пустой)
        """
        assert tag > 0

        return [f for f in self.fields if f.tag == tag]

    def all_as_dict(self, tag: int) -> 'List[dict]':
        """
        Список полей с указанной меткой, каждое поле в виде словаря
        "код - значение".
        :param tag:
        :return:
        """
        assert tag > 0

        return [f.to_dict() for f in self.fields if f.tag == tag]

    def clone_fields(self) -> 'FieldList':
        return [field.clone() for field in self.fields]

    def fm(self, tag: int, code: str = '') -> 'Optional[str]':
        """
        Текст первого поля с указанной меткой.
        :param tag: Искомая метка поля
        :param code: Код (опционально)
        :return: Текст или None
        """
        assert tag > 0

        for field in self.fields:
            if field.tag == tag:
                if code:
                    return field.first_value(code)
                return field.value
        return None

    def fma(self, tag: int, code: str = '') -> 'List[str]':
        """
        Спосок значений полей с указанной меткой.
        Пустые значения в список не включаются.

        :param tag: Искомая метка поля
        :param code: Код (опционально)
        :return: Список с текстами (м. б. пустой)
        """
        assert tag > 0

        result = []
        for field in self.fields:
            if field.tag == tag:
                if code:
                    one = field.first_value(code)
                    if one:
                        result.append(one)
                else:
                    one = field.value
                    if one:
                        result.append(one)
        return result

    def first(self, tag: int) -> 'Optional[Field]':
        """
        Первое из полей с указанной меткой.

        :param tag: Искомая метка поля
        :return: Поле либо None
        """
        assert tag > 0

        for field in self.fields:
            if field.tag == tag:
                return field
        return None

    def first_as_dict(self, tag: int) -> dict:
        """
        Первое из полей с указанной меткой в виде словаря
        "код - значение".
        """
        assert tag > 0

        for field in self.fields:
            if field.tag == tag:
                return field.to_dict()
        return {}

    def have_field(self, tag: int) -> bool:
        """
        Есть ли в записи поле с указанной меткой?

        :param tag: Искомая метка поля.
        :return: True или False.
        """
        if not isinstance(tag, int):
            raise ValueError('tag argument must be int type')
        if tag <= 0:
            raise ValueError('tag argument must be greater than 0')
        return tag in self.keys()

    def insert_at(self, index: int, tag: int, value: 'Optional[str]' = None) \
            -> 'Field':
        """
        Вставка поля в указанной позиции.

        :param index: Позиция для вставки.
        :param tag: Метка поля.
        :param value: Значение поля до первого разделитея (опционально).
        :return: Self
        """
        assert 0 <= index < len(self.fields)
        assert tag > 0

        result = self.field_type(tag, value)
        self.fields.insert(index, result)
        return result

    def keys(self) -> 'Set[int]':
        """
        Получение множества меток полей

        :return: множество меток
        """
        return set(field.tag for field in self.fields)

    def parse_line(self, line: str) -> None:
        field = self.field_type()
        field.parse(line)
        self.fields.append(field)

    def remove_field(self, tag: int) -> 'Record':
        """
        Удаление полей с указанной меткой.

        :param tag: Метка поля.
        :return: Self.
        """
        self.__delitem__(tag)
        return self

    def set_field(self, tag: int, value: 'Optional[str]') -> 'Record':
        """
        Устанавливает значение первого повторения указанного поля.
        Если указанное значение пустое, поле удаляется из записи.

        :param tag: Метка поля.
        :param value: Значение поля до первого разделителя (может быть None).
        :return: Self.
        """
        assert tag > 0

        found = self.first(tag)
        if value:
            if not found:
                found = self.field_type(tag)
                self.fields.append(found)
            found.value = value
        else:
            if found:
                self.fields.remove(found)

        return self

    def set_subfield(self, tag: int, code: str,
                     value: 'Optional[str]') -> 'Record':
        """
        Устанавливает значение подполя в первом повторении указанного поля.
        Если указанное значение пустое, подполе удаляется из поля.

        :param tag: Метка поля.
        :param code: Код подполя.
        :param value: Значение подполя (может быть None).
        :return: Self.
        """
        assert tag > 0
        assert len(code) == 1

        found = self.first(tag)
        if value:
            if not found:
                found = self.field_type(tag)
                self.fields.append(found)
        if found:
            found.set_subfield(code, value)

        return self

    def __iter__(self):
        """
        Перебор полей записи для формирования словаря "код - поля".
        """
        accumulator = {}
        for field in self.fields:
            key = field.tag

            if field.subfields:
                value = dict(field)
            else:
                value = field.value

            value_count = len(self.all(key))
            if value_count == 1:
                accumulator[key] = value
            elif value_count > 1:
                if key not in accumulator:
                    accumulator[key] = [value]
                else:
                    accumulator[key].append(value)

        for key, value in accumulator.items():
            yield key, value

    def __iadd__(self, other: 'Union[Field, FieldList]'):
        if isinstance(other, Field):
            self.fields.append(other)
        else:
            self.fields.extend(other)
        return self

    def __isub__(self, other: 'Union[Field, FieldList]'):
        if isinstance(other, Field):
            if other in self.fields:
                self.fields.remove(other)
        else:
            for one in other:
                if one in self.fields:
                    self.fields.remove(one)
        return self

    def __getitem__(self, tag: int) -> 'Union[dict, List[dict], str]':
        """
        Получение значения поля по индексу

        :param tag: числовая метка полей
        :return: значение полей (словарь, список словарей или строка)
        """
        def get_str_or_dict(field):
            if field.subfields:
                return dict(field)
            return field.value

        fields = self.all(tag)
        count = len(fields)

        if count == 1:
            return get_str_or_dict(fields[0])

        if count > 1:
            return [get_str_or_dict(field) for field in fields]

        return ''

    def __setitem__(self, key: int, value: 'RecordValue') -> None:
        """
        Присвоение поля или полей по указанной метке

        :param key: числовая метка полей
        :param value: поле или список полей (dict, Field и др.)
        :return: None
        """
        self.remove_field(key)
        if value:
            if isinstance(value, list):
                if all((isinstance(element, Field) for element in value)):
                    value = cast('FieldList', value)
                    self.fields += value
                else:
                    self.fields += [
                        self.field_type(key, cast('FieldValue', v))
                        for v in value]
            elif isinstance(value, Field):
                self.fields.append(value)
            else:
                self.fields.append(self.field_type(key, value))

    def __delitem__(self, key):
        """
        Метод удаления всех полей с указанной меткой. Может вызываться
        следующим образом -- del field[key].

        :param key: числовая метка
        :return:
        """
        assert key > 0
        self.fields = [f for f in self.fields if f.tag != key]

    def __hash__(self):
        sorted_fields = sorted(self.fields, key=hash)
        subfields_hashes = tuple(hash(f) for f in sorted_fields)
        return hash(subfields_hashes)


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

# coding: utf-8

"""
Работа с записями, полями, подполями.
"""

from typing import cast, TYPE_CHECKING
from irbis.abstract import DictLike, Hashable
from irbis.records.abstract import AbstractRecord
from irbis.records.field import Field
from irbis.records.subfield import SubField
if TYPE_CHECKING:
    from typing import Dict, List, Optional, Union, Type
    from irbis.records.field import FieldList, FieldValue

    RecordValue = Union[Field, FieldList, FieldValue, List[str]]


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
        result = self[tag]
        if isinstance(result, Field):
            return [result]
        return result

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

    @property
    def data(self) -> 'Dict[int, List[Dict]]':
        """
        Динамическое свойство извлечения данных в представлении стандартных
        типов данных Python.
        """
        result = {}
        for key in self.keys():
            fields = self[key]
            result[key] = [f.data for f in fields]
        return result

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

    def keys(self) -> 'List[int]':
        """
        Получение множества меток полей

        :return: множество меток
        """
        return list(set(field.tag for field in self.fields))

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

            value_count = len(self[key])
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

    def __getitem__(self, tag: int) -> 'FieldList':
        """
        Получение значения поля по индексу

        :param tag: числовая метка полей
        :return: поле, список полей или ничего
        """
        return [f for f in self.fields if f.tag == tag]

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

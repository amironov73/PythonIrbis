# coding: utf-8

"""
Работа с записями, полями, подполями.
"""

from collections import OrderedDict
from typing import cast, TYPE_CHECKING
from irbis.abstract import DictLike, Hashable
from irbis.records.abstract import AbstractRecord
from irbis.records.field import Field
from irbis.records.subfield import SubField
if TYPE_CHECKING:
    from typing import Dict, List, Optional, Set, Union, Type
    from irbis.records.field import FieldList, FieldSetValue, SubFieldDicts

    RecordArg = Union[Field, Dict[int, SubFieldDicts]]
    RecordValue = Union[Field, FieldList, FieldSetValue, List[str],
                        SubFieldDicts]


class Record(AbstractRecord, DictLike, Hashable):
    """
    MARC record with MFN, status, version and fields.
    """
    __slots__ = 'database', 'mfn', 'version', 'status', 'fields'
    fields: 'List[Field]'

    def __init__(self, *args: 'RecordArg') -> None:
        self.field_type: 'Type[Field]' = Field
        super().__init__(*args)

    def __bulk_set__(self, *args: 'RecordArg'):
        """
        Приватный метод установки полей записи.

        Внимание. Пользователь не должен явно обращаться к данному методу.

        :param args: список полей или словарь
        :return: ничего
        """
        if args:
            arg = args[0]
            if isinstance(arg, dict):
                for key in arg:
                    self[key] = arg[key]
            elif all((isinstance(arg, self.field_type) for arg in args)):
                self.fields += [cast('Field', arg) for arg in args]
            else:
                raise TypeError('One or more args have unsupported type')

    def add(self, tag: int,
            value: 'Optional[Union[str, SubField]]' = None) -> 'Field':
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
        result = self.get(tag)
        if isinstance(result, Field):
            return [result]
        return result

    def all_as_dict(self, tag: int) -> 'List[dict]':
        """
        Список полей с указанной меткой, каждое поле в виде словаря
        "код - значение".

        :param tag: Искомая метка поля.
        :return: Список словарей "код-значение".
        """
        assert tag > 0

        return [f.to_dict() for f in self.fields if f.tag == tag]

    def clone_fields(self) -> 'FieldList':
        return [field.clone() for field in self.fields]

    @property
    def data(self) -> 'Dict[int, List[OrderedDict]]':
        """
        Динамическое свойство извлечения данных в представлении стандартных
        типов данных Python.
        """
        result = {}
        for key in self.keys():
            fields = self[key]
            result[key] = [f.data for f in fields]
        return result

    def fm(self, tag: int, code: str = '*', default: 'Optional[str]' = None)\
            -> 'Optional[str]':
        """
        Текст первого поля с указанной меткой.

        :param tag: Искомая метка поля.
        :param code: Код подполя (опционально). Если код не задан,
        возвращается значение поля до первого разделителя.
        :param default: Значение по умолчанию.
        :return: Текст или значение по умолчанию.
        """
        assert tag > 0

        for field in self.fields:
            if field.tag == tag:
                if code:
                    return field.first_value(code, default)
                return field.value or default
        return default

    def fma(self, tag: int, code: str = '*') -> 'List[str]':
        """
        Спосок значений полей с указанной меткой.
        Пустые значения в список не включаются.

        :param tag: Искомая метка поля.
        :param code: Код (опционально). Если код не задан,
        возвращается значение поле до первого разделителя.
        :return: Список с текстами (м. б. пустой).
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

    def first(self, tag: int, default: 'Optional[Field]' = None)\
            -> 'Optional[Field]':
        """
        Первое из полей с указанной меткой.

        :param tag: Искомая метка поля.
        :param default: Значение по умолчанию.
        :return: Поле или значение по умолчанию.
        """
        assert tag > 0

        for field in self.fields:
            if field.tag == tag:
                return field
        return default

    def first_as_dict(self, tag: int) -> OrderedDict:
        """
        Первое из полей с указанной меткой в виде словаря
        "код - значение".
        """
        assert tag > 0

        for field in self.fields:
            if field.tag == tag:
                return field.to_dict()
        return OrderedDict()

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
        Получение списка меток полей без повторений и с сохранением порядка

        :return: список меток
        """
        unique: 'Set' = set()
        add = unique.add
        return [f.tag for f in self.fields
                if not (f.tag in unique or add(f.tag))]

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
        del self[tag]
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
        yield from self.fields

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

        :param tag: числовая метка полей.
        :return: список полей или ничего.
        """
        return [f for f in self.fields if f.tag == tag]

    def get(self, key: int, default: 'Optional[FieldList]' = None)\
            -> 'FieldList':
        """
        Получение значения подполя по индексу

        :param key: числовая метка полей.
        :param default: значение по-умолчанию.
        :return: список полей или default.
        """
        return super().get(key, default)

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
                        self.field_type(key, cast('FieldSetValue', v))
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
        fields_hashes = tuple(hash(f) for f in self.fields)
        return hash(fields_hashes)

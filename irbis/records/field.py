# coding: utf-8

"""
Работа с полями.
"""

from collections import OrderedDict
from typing import cast, TYPE_CHECKING
from irbis.abstract import DictLike, Hashable
from irbis.records.abstract import ValueMixin
from irbis.records.subfield import SubField
if TYPE_CHECKING:
    from irbis.records.subfield import SubFieldList, Value
    from typing import Dict, Iterable, List, Optional, Set, Union, Tuple
    from typing import Sequence

    Code = str
    SubFieldValues = Sequence[Value]
    FieldSetItemValue = Union[None, SubField, SubFieldValues]
    FieldSetItemValues = Sequence[FieldSetItemValue]
    SubFieldDict = Dict[Code, SubFieldValues]
    SubFieldDicts = List[SubFieldDict]
    SubFieldTuple = Tuple[Code, SubFieldValues]
    SubFieldTuples = List[SubFieldTuple]
    NotDictFieldSetValue = Union[FieldSetItemValue, FieldSetItemValues,
                                 SubFieldTuple, SubFieldTuples]
    FieldSetValue = Union[NotDictFieldSetValue, SubFieldDict]
    FieldList = List['Field']
    FieldGetReturn = Union[str, SubField, SubFieldList, None]


class Field(DictLike, Hashable, ValueMixin):
    """
    MARC record field with tag, value (up to the first delimiter)
    and subfields.
    """

    DEFAULT_TAG = 0

    __slots__ = 'tag', 'value', 'subfields'

    def __init__(self, tag: 'Optional[int]' = DEFAULT_TAG,
                 value: 'FieldSetValue' = None) -> None:
        self.tag: int = tag or self.DEFAULT_TAG
        self.value: 'Optional[str]' = None
        self.subfields: 'SubFieldList' = []
        self.__bulk_set__(value)

    def __bulk_set__(self, values: 'FieldSetValue' = None):
        """
        Приватный метод установки 1) подполей и 2) значения до первого
        разделителя из поддерживаемых структур данных.

        Внимание. Пользователь не должен явно обращаться к данному методу.

        :param values: Переменная или структура для создания подполей.
        """
        if values:
            if isinstance(values, str):
                self.headless_parse(values)
            else:
                if isinstance(values, dict):
                    values = list(values.items())

                if not isinstance(values, (list, tuple)):
                    values = cast('NotDictFieldSetValue', [values])
                if isinstance(values, (list, tuple)):
                    if (
                        len(values) == 2
                        and isinstance(values[0], str)
                        and isinstance(values[1], (str, list, tuple))
                    ):
                        values = cast('SubFieldTuples', [values])
                    for value in values:
                        if isinstance(value, SubField):
                            self.subfields.append(value)
                            continue
                        if (
                            isinstance(value, (list, tuple))
                            and len(value) == 2
                        ):
                            self.add(value[0], value[1])
                            continue
                        raise TypeError('Unsupported value type')

    def add(self, code: str, value: 'SubFieldValues' = '')\
            -> 'Field':
        """
        Добавление подполя с указанным кодом (и, возможно, значением)
        к записи.

        :param code: Код подполя (однобуквенный).
        :param value: Значение подполя (опционально).
        :return: Self
        """
        code = SubField.validate_code(code)
        if code == '*':
            if value and isinstance(value, (list, tuple)):
                value = value[0]

            if not self.value:
                self.value = self.validate_value(value)
            else:
                raise ValueError('Значение до первого разделителя уже задано')

        else:
            if value:
                if isinstance(value, str):
                    value = [value]
                for val in value:
                    subfield = SubField(code, val)
                    self.subfields.append(subfield)
        return self

    def add_non_empty(self, code: str, value: 'Optional[str]') -> 'Field':
        """
        Добавление подполя с указанным кодом при условии,
        что значение поля не пустое.

        :param code: Код подполя (однобуквенный).
        :param value: Значение подполя (опциональное).
        :return: Self
        """
        code = SubField.validate_code(code)
        if value:
            self.add(code, value)
        return self

    def all(self, code: str) -> 'FieldGetReturn':
        """
        Список всех подполей с указанным кодом.

        :param code: Код подполя (однобуквенный).
        :return: Список подполей (возможно, пустой).
        """
        code = SubField.validate_code(code)
        return self.get(code)

    def all_values(self, code: str) -> 'List[str]':
        """
        Список значений всех подполей с указанным кодом.
        Пустые значения подполей в список не включаются.

        :param code: Код подполя (однобуквенный).
        :return: Список значений (возможно, пустой).
        """
        code = SubField.validate_code(code)
        if code == '*':
            return [self.get_value_or_first_subfield() or '']
        return [sf.value for sf in self.subfields
                if sf.code == code if sf.value]

    def assign_from(self, other: 'Field') -> None:
        """
        Присваивание от другого поля.
        1. Значение данного поля становится равным значению другого поля.
        2. В данное поле помещаются клоны подполей из другого поля.
        3. Метка поля не меняется.

        :param other: Поле-источник
        :return: None
        """
        assert other

        self.value = other.value
        self.subfields = [sf.clone() for sf in other.subfields]

    def clear(self) -> 'Field':
        """
        Очистка поля. Удаляются все подполя и значение до первого разделителя.

        :return: Self
        """

        self.value = None
        self.subfields = []
        return self

    def clone(self) -> 'Field':
        """
        Создание полного клона поля.

        :return: Клон поля.
        """
        result = Field(self.tag, self.value)
        for subfield in self.subfields:
            result.subfields.append(subfield.clone())
        return result

    @property
    def data(self) -> 'OrderedDict[str, Union[str, SubFieldList]]':
        """
        Динамическое свойство извлечения данных в представлении стандартных
        типов данных Python.

        :return: Упорядоченный словарь, "код подполя" => "список подполей".
        Значение до первого разделителя попадает в словарь
        с ключом "пустая строка".
        """
        result: 'OrderedDict[str, Union[str, SubFieldList]]' = OrderedDict()
        for key in self.keys():
            values = self[key]
            if isinstance(values, str):
                result[key] = values
            elif isinstance(values, list):
                result[key] = [subfield.data for subfield in values]
        return result

    def first(self, code: str, default: 'Optional[SubField]' = None)\
            -> 'Optional[Union[SubField, Value]]':
        """
        Находит первое подполе с указанным кодом.

        :param code: Искомый код.
        :param default: Значение по умолчанию.
        :return: Подполе, значение до разделителя или default.
        """
        code = SubField.validate_code(code)
        result = self.get(code)
        if result:
            if isinstance(result, list):
                return result[0]
            return result
        return default

    def first_value(self, code: str, default: 'Optional[str]' = None)\
            -> 'Optional[str]':
        """
        Находит первое подполе с указанным кодом и выдает его значение.

        :param code: Искомый код.
        :param default: Значение по умолчанию.
        :return: Значение подполя или значение по умолчанию.
        """
        code = SubField.validate_code(code)
        if code == '*':
            return self.get_value_or_first_subfield()
        for subfield in self.subfields:
            if subfield.code == code:
                return subfield.value
        return default

    def get_embedded_fields(self) -> 'List[Field]':
        """
        Получение списка встроенных полей.

        :return: Список встроенных полей.
        """
        result: 'List[Field]' = []
        found: 'Optional[Field]' = None

        for subfield in self.subfields:
            if subfield.code == '1':
                if found:
                    result.append(found)
                value = subfield.value
                if not value:
                    continue
                tag = int(value[0:3])
                found = Field(tag)
                if tag < 10 and len(value) > 3:
                    found.value = value[3:]
            else:
                if found is not None:
                    found.subfields.append(subfield)

        if found:
            result.append(found)

        return result

    def get_value_or_first_subfield(self) -> 'Optional[str]':
        """
        Выдаёт значение для ^*.
        :return: Найденное значение
        """

        result = self.value
        if (not result) and self.subfields:
            result = self.subfields[0].value

        return result

    def have_subfield(self, code: str) -> bool:
        """
        Выясняет, есть ли подполе с указанным кодом.

        :param code: Искомый код подполя (должен быть однобуквенным).
        :return: True, если есть хотя бы одно подполе с указанным кодом.
        """
        code = SubField.validate_code(code)
        return code in self.keys()

    def headless_parse(self, line: str) -> None:
        """
        Разбор текстового представления поля (без метки поля).

        :param line: Строка с текстовым представлением.
        :return: None.
        """
        parts = line.split('^')
        self.value = parts[0] or None
        for raw_item in parts[1:]:
            if raw_item:
                self.add(raw_item[:1], raw_item[1:])

    def insert_at(self, index: int, code: str, value: str) -> 'Field':
        """
        Вставляет подполе в указанную позицию.

        :param index: Позиция для вставки.
        :param code: Код подполя (обязательно).
        :param value: Значение подполя (опционально).
        :return: Self
        """
        assert index >= 0
        code = SubField.validate_code(code)

        subfield = SubField(code, value)
        self.subfields.insert(index, subfield)
        return self

    def keys(self) -> 'List[str]':
        """
        Получение списка кодов подполей без повторений и с сохранением порядка

        :return: список кодов
        """
        result = []
        if self.value:
            result.append('*')
        unique: 'Set' = set()
        add = unique.add
        result.extend([sf.code for sf in self.subfields
                       if not (sf.code in unique or add(sf.code))])
        return result

    def parse(self, line: str) -> None:
        """
        Разбор текстового представления поля (в серверном формате).

        :param line: Строка с текстовым представлением.
        :return: None.
        """
        parts = line.split('#', 1)
        self.tag = int(parts[0])
        self.headless_parse(parts[1])

    def remove_at(self, index: int) -> 'Field':
        """
        Удаляет подполе в указанной позиции.

        :param index: Позиция для удаления
        :return: Self
        """
        assert index >= 0

        self.subfields.remove(self.subfields[index])
        return self

    def remove_subfield(self, code: str) -> 'Field':
        """
        Удаляет все подполя с указанным кодом.

        :param code: Код для удаления.
        :return: Self
        """
        del self[code]
        return self

    def replace_subfield(self, code: str, old_value: 'Optional[str]',
                         new_value: 'Optional[str]') -> 'Field':
        """
        Заменяет значение подполя с указанным кодом.

        :param code: Код подполя (обязательно).
        :param old_value: Старое значение.
        :param new_value: Новое значение.
        :return: Self.
        """
        code = SubField.validate_code(code)
        for subfield in self.subfields:
            if subfield.code == code and subfield.value == old_value:
                subfield.value = new_value

        return self

    def set_subfield(self, code: str, value: 'Optional[str]') -> 'Field':
        """
        Устанавливает значение первого повторения подполя с указанным кодом.
        Если value==None, подполе удаляется.

        :param code: Код искомого подполя.
        :param value: Устанавливаемое значение подполя (опционально).
        :return: Self
        """
        code = SubField.validate_code(code)
        if value:
            found = self.first(code)
            if found:
                if isinstance(found, str):
                    self.value = value
                elif isinstance(found, SubField):
                    found.value = value
            else:
                self.add(code, value)
        else:
            return self.remove_subfield(code)
        return self

    def text(self) -> str:
        """
        Текстовое представление поля без кода.
        :return:
        """
        result = ''
        if self.value:
            result = self.value
        result += ''.join(str(s) for s in self.subfields)
        return result

    def to_dict(self) -> OrderedDict:
        """
        Выдает словарь "код - значение подполя".
        :return:
        """
        result = OrderedDict()
        for subfield in self.subfields:
            result[subfield.code] = subfield.value
        return result

    def __str__(self):
        if not self.tag:
            return ''
        buffer = [str(self.tag), '#', self.value or '']
        buffer += [str(sf) for sf in self.subfields]
        return ''.join(buffer)

    def __iter__(self):
        """
        Перебор подполей в виде "код - значение".
        """
        if self.subfields:
            for subfield in self.subfields:
                yield subfield.code, subfield.value
        else:
            yield '', self.value

    def __iadd__(self, other: 'Union[SubField, Iterable[SubField]]'):
        if isinstance(other, SubField):
            self.subfields.append(other)
        else:
            self.subfields.extend(other)
        return self

    def __isub__(self, other: 'Union[SubField, Iterable[SubField]]'):
        if isinstance(other, SubField):
            if other in self.subfields:
                self.subfields.remove(other)
        else:
            for one in other:
                if one in self.subfields:
                    self.subfields.remove(one)
        return self

    def __getitem__(self, key: 'Union[str, int]')\
            -> 'FieldGetReturn':
        """
        Получение значения подполя по индексу

        :param key: строковый код или позиция подполя
        :return: список подполей, подполе или строка
        """
        if key == '*':
            if self.value:
                return self.value
        elif isinstance(key, str):
            code = SubField.validate_code(key)
            return [sf for sf in self.subfields if sf.code == code]
        elif isinstance(key, int):
            return self.subfields[key]
        raise KeyError

    def get(self, key: 'Union[str, int]', default: 'FieldGetReturn' = None)\
            -> 'FieldGetReturn':
        """
        Получение значения подполя по индексу

        :param key: строковый код или позиция подполя
        :param default: значение по-умолчанию
        :return: список подполей, подполе, строка или default
        """
        return super().get(key, default)

    def __setitem__(self, key: 'Union[str, int]', value: 'FieldSetItemValue'):
        if key == '*':
            self.value = self.validate_value(value)

        elif isinstance(key, int):
            if value:
                if isinstance(value, str):
                    self.subfields[key].value = self.validate_value(value)
                elif isinstance(value, Field):
                    self.subfields[key] = value
                elif isinstance(value, (list, tuple)) and len(value) == 2:
                    code, val = value
                    if isinstance(code, str) and isinstance(val, str):
                        self.subfields[key] = SubField(code, val)
                else:
                    raise TypeError
            else:
                self.subfields.pop(key)

        elif isinstance(key, str):
            key = SubField.validate_code(key)
            del self[key]
            if value is not None:
                values = key, value
                self.__bulk_set__(values)

    def __delitem__(self, key: 'Union[str, int]'):
        """
        Метод удаления всех подполей с указанным кодом. Может вызываться
        следующим образом -- del field[key].

        :param key: строковый код
        :return:
        """
        if isinstance(key, int):
            self.subfields.pop(key)
        elif isinstance(key, str):
            key = SubField.validate_code(key)
            self.subfields = [sf for sf in self.subfields if sf.code != key]

    def __len__(self):
        return len(self.subfields)

    def __bool__(self):
        return bool(self.tag) and (bool(self.value) or bool(self.subfields))

    def __hash__(self):
        return hash((self.tag, self.value, *self.subfields))

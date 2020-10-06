# coding: utf-8

"""
Работа с полями.
"""

from collections import OrderedDict
from typing import cast, TYPE_CHECKING
from irbis.abstract import DictLike, Hashable
from irbis.records.subfield import SubField
if TYPE_CHECKING:
    from irbis.records.subfield import SubFieldList, SubFieldDict
    from typing import Iterable, List, Optional, Set, Union

    FieldList = List['Field']
    FieldValue = Union[SubField, SubFieldList, List[SubFieldDict],
                       SubFieldDict, str, None]
    FieldGetReturn = Union[str, SubField, SubFieldList]


class Field(DictLike, Hashable):
    """
    MARC record field with tag, value (up to the first delimiter)
    and subfields.
    """

    DEFAULT_TAG = 0

    __slots__ = 'tag', 'value', 'subfields'

    def __init__(self, tag: 'Optional[int]' = DEFAULT_TAG,
                 value: 'FieldValue' = None) -> None:
        self.tag: int = tag or self.DEFAULT_TAG
        self.value: 'Optional[str]' = None
        self.subfields: 'SubFieldList' = []
        self.set_values(value)

    def set_values(self, values: 'FieldValue' = None):
        """
        Установка значений поля

        :value: Переменная или структура для создания подполей
        """
        if values is None:
            pass

        elif isinstance(values, SubField):
            self.subfields.append(values)

        elif isinstance(values, str):
            self.headless_parse(values)

        elif isinstance(values, list):
            if all((isinstance(element, SubField) for element in values)):
                self.subfields = cast('SubFieldList', values)
            else:
                raise TypeError('All elements must be of the SubField type')

        elif isinstance(values, dict):
            for code, value in values.items():
                if isinstance(value, str):
                    if code == '*':
                        self.value = value
                        continue
                    self.add(code, value)
                elif isinstance(value, list):
                    if all((isinstance(element, str) for element in value)):
                        if code == '*':
                            self.value = value[0]
                        else:
                            for val in value:
                                self.add(code, val)
                    else:
                        raise TypeError('Unsupported value type')
                else:
                    raise TypeError('Unsupported value type')
        else:
            raise TypeError('Unsupported value type')

    def add(self, code: str, value: str = '*') -> 'Field':
        """
        Добавление подполя с указанным кодом (и, возможно, значением)
        к записи.

        :param code: Код подполя (однобуквенный)
        :param value: Значение подполя (опционально)
        :return: Self
        """
        code = SubField.validate_code(code)
        if code == '*':
            if self.value is None:
                self.value = value
            else:
                raise ValueError('Значение до первого разделителя уже задано')
        subfield = SubField(code, value)
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

    def all(self, code: str) -> 'SubFieldList':
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
    def data(self) -> OrderedDict:
        """
        Динамическое свойство извлечения данных в представлении стандартных
        типов данных Python.

        :return: Упорядоченный словарь, "код подполя" => "список подполей".
        Значение до первого разделителя попадает в словарь
        с ключом "пустая строка".
        """
        result = OrderedDict()
        if self.value:
            result['*'] = [self.value]
        for key in self.keys():
            subfields = self[key]
            result[key] = []
            for subfield in subfields:
                if isinstance(subfield, SubField):
                    result[key].append(subfield.data)
                elif isinstance(subfield, str):
                    result[key].append(subfield)
        return result

    def first(self, code: str, default: 'Optional[SubField]' = None)\
            -> 'Optional[SubField]':
        """
        Находит первое подполе с указанным кодом.

        :param code: Искомый код.
        :param default: Значение по умолчанию.
        :return: Подполе или значение по умолчанию.
        """
        code = SubField.validate_code(code)
        # if code == '*':
        #    return self.get_value_or_first_subfield()
        for subfield in self.subfields:
            if subfield.code == code:
                return subfield
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
        unique: 'Set' = set()
        add = unique.add
        return [sf.code for sf in self.subfields
                if not (sf.code in unique or add(sf.code))]

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
        self.__delitem__(code)
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
        if not value:
            return self.remove_subfield(code)

        found = self.first(code)
        if not found:
            found = SubField(code)
            self.subfields.append(found)
        found.value = value

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

    def get(self, key: 'Union[str, int]', default: 'FieldGetReturn' = list)\
            -> 'FieldGetReturn':
        """
        Получение значения подполя по индексу

        :param key: строковый код или позиция подполя
        :default: значение по-умолчанию
        :return: список подполей, подполе, строка или default
        """
        if default == list and key == '*':  # [] != list
            default = ''
        elif default == list and isinstance(key, int):
            default = None
        return super().get(key, default)

    def __setitem__(self, key: 'Union[str, int]', value: 'FieldValue'):
        if key == '*':
            if value is None or isinstance(value, str):
                self.value = value
            else:
                message = 'Field.value должно быть непустой строкой или None'
                raise TypeError(message)

        elif isinstance(key, int):
            if value:
                self.subfields[key].value = value
            else:
                self.subfields.pop(key)

        elif isinstance(key, str):
            key = SubField.validate_code(key)
            del self[key]
            values = value
            if not isinstance(value, list):
                values = [values]
            if isinstance(value, list):
                for value in values:
                    if value:
                        self.add(key, value)


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

# coding: utf-8

"""
Работа с полями.
"""

from typing import TYPE_CHECKING
from irbis.subfield import SubField
if TYPE_CHECKING:
    from irbis.subfield import SubFieldList, SubFieldsDict
    from typing import Iterable, List, Optional, Set, Union

    FieldList = List['Field']
    FieldValue = Union[SubField, SubFieldList, List[SubFieldsDict],
                       SubFieldsDict, str, None]


class Field:
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

        if value is None:
            pass

        elif isinstance(value, SubField):
            self.subfields.append(value)

        elif isinstance(value, str):
            self.headless_parse(value)

        elif isinstance(value, list):
            if all((isinstance(element, SubField) for element in value)):
                self.subfields = value
            else:
                raise TypeError('All elements must be of the SubField type')

        elif isinstance(value, dict):
            for code, val in value.items():
                if isinstance(val, str):
                    if code == '':
                        self.value = val
                        continue
                    self.subfields.append(
                        SubField(code, val)
                    )
                else:
                    raise TypeError('Value of SubField must be str type')

        else:
            raise TypeError('Unsupported value type')

    def add(self, code: str, value: str = '') -> 'Field':
        """
        Добавление подполя с указанным кодом (и, возможно, значением)
        к записи.

        :param code: Код подполя (однобуквенный)
        :param value: Значение подполя (опционально)
        :return: Self
        """
        assert len(code) == 1

        self.subfields.append(SubField(code, value))
        return self

    def add_non_empty(self, code: str, value: 'Optional[str]') -> 'Field':
        """
        Добавление подполя с указанным кодом при условии,
        что значение поля не пустое.

        :param code: Код подполя (однобуквенный).
        :param value: Значение подполя (опциональное).
        :return: Self
        """
        assert len(code) == 1

        if value:
            self.subfields.append(SubField(code, value))

        return self

    def all(self, code: str) -> 'SubFieldList':
        """
        Список всех подполей с указанным кодом.

        :param code: Код подполя (однобуквенный).
        :return: Список подполей (возможно, пустой).
        """
        assert len(code) == 1

        code = code.lower()
        # if code == '*':
        #    return [self.get_value_or_first_subfield()]
        return [sf for sf in self.subfields if sf.code == code]

    def all_values(self, code: str) -> 'List[str]':
        """
        Список значений всех подполей с указанным кодом.
        Пустые значения подполей в список не включаются.

        :param code: Код подполя (однобуквенный).
        :return: Список значений (возможно, пустой).
        """
        assert len(code) == 1

        code = code.lower()
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

        :return: Клон поля
        """
        result = Field(self.tag, self.value)
        for subfield in self.subfields:
            result.subfields.append(subfield.clone())
        return result

    def first(self, code: str) -> 'Optional[SubField]':
        """
        Находит первое подполе с указанным кодом.
        :param code: Код
        :return: Подполе или None
        """
        assert len(code) == 1

        code = code.lower()
        # if code == '*':
        #    return self.get_value_or_first_subfield()
        for subfield in self.subfields:
            if subfield.code == code:
                return subfield
        return None

    def first_value(self, code: str) -> 'Optional[str]':
        """
        Находит первое подполе с указанным кодом.
        :param code: Код
        :return: Значение подполя или None
        """
        assert len(code) <= 1

        code = code.lower()
        if code == '*':
            return self.get_value_or_first_subfield()
        for subfield in self.subfields:
            if subfield.code == code:
                return subfield.value
        return None

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
        assert len(code) == 1

        code = code.lower()
        for subfield in self.subfields:
            if subfield.code == code:
                return True

        return False

    def headless_parse(self, line: str) -> None:
        """
        Разбор текстового представления поля (без метки поля).

        :param line: Строка с текстовым представлением.
        :return: None.
        """
        if '^' not in line:
            self.value = line
        else:
            if line[0] != '^':
                parts = line.split('^', 1)
                self.value = parts[0]
                parts = parts[1].split('^')
            else:
                parts = line.split('^')
            for raw_item in parts:
                if raw_item:
                    subfield = SubField(raw_item[:1], raw_item[1:])
                    self.subfields.append(subfield)

    def insert_at(self, index: int, code: str, value: str) -> 'Field':
        """
        Вставляет подполе в указанную позицию.

        :param index: Позиция для вставки.
        :param code: Код подполя (обязательно).
        :param value: Значение подполя (опционально).
        :return: Self
        """
        assert index >= 0
        assert len(code) == 1

        subfield = SubField(code, value)
        self.subfields.insert(index, subfield)
        return self

    def keys(self) -> 'Set[str]':
        """
        Получение множества кодов подполей

        :return: множество кодов
        """
        if self.subfields:
            return set(subfield.code for subfield in self.subfields)
        return set('')

    def parse(self, line: str) -> None:
        """
        Разбор текстового представления поля (в серверном формате).

        :param line: Строка с текстовым представлением.
        :return: None.
        """
        parts = line.split('#', 1)
        self.tag = int(parts[0])
        if '^' not in parts[1]:
            self.value = parts[1]
        else:
            if parts[1][0] != '^':
                parts = parts[1].split('^', 1)
                self.value = parts[0]
                parts = parts[1].split('^')
            else:
                parts = parts[1].split('^')
            for raw_item in parts:
                if raw_item:
                    subfield = SubField(raw_item[:1], raw_item[1:])
                    self.subfields.append(subfield)

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
        assert code

        code = code.lower()
        index = 0
        while index < len(self.subfields):
            subfield = self.subfields[index]
            if subfield.code == code:
                self.subfields.remove(subfield)
            else:
                index += 1

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
        assert code

        code = code.lower()
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
        assert code

        code = code.lower()
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

    def to_dict(self) -> dict:
        """
        Выдает словарь "код - значение подполя".
        :return:
        """
        result = {}
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

    def __getitem__(self, code: 'Union[str, int]') -> str:
        """
        Получение значения подполя по индексу

        :param code: строковый код подполя
        :return: строковое значение подполя
        """
        if isinstance(code, int):
            return self.subfields[code].value or ''

        if code == '':
            return self.value or ''

        return self.first_value(code) or ''

    def __setitem__(self, key: 'Union[str, int]', value: 'Optional[str]'):
        if isinstance(key, int):
            if value:
                self.subfields[key].value = value
            else:
                self.subfields.pop(key)
        else:
            found = self.first(key)
            if value:
                if found:
                    found.value = value
                else:
                    found = SubField(key, value)
                    self.subfields.append(found)
            else:
                if found:
                    self.subfields.remove(found)

    def __len__(self):
        return len(self.subfields)

    def __bool__(self):
        return bool(self.tag) and (bool(self.value) or bool(self.subfields))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.tag, self.value or tuple(self.subfields)))

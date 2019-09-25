# coding: utf-8

"""
Работа с записями, полями, подполями.
"""

from typing import Iterable, List, Optional, Union
from ._common import LOGICALLY_DELETED, PHYSICALLY_DELETED


class SubField:
    """
    MARC record subfield with code and text value.
    """

    DEFAULT_CODE = '\0'

    __slots__ = 'code', 'value'

    def __init__(self, code: str = DEFAULT_CODE,
                 value: Optional[str] = None) -> None:
        code = code or SubField.DEFAULT_CODE
        self.code: str = code.lower()
        self.value: Optional[str] = value

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

    def __str__(self):
        if self.code == self.DEFAULT_CODE:
            return ''
        return '^' + self.code + (self.value or '')

    def __bool__(self):
        return self.code != self.DEFAULT_CODE and bool(self.value)


##############################################################################

class Field:
    """
    MARC record field with tag, value (up to the first delimiter)
    and subfields.
    """

    DEFAULT_TAG = 0

    __slots__ = 'tag', 'value', 'subfields'

    def __init__(self, tag: Optional[int] = DEFAULT_TAG,
                 value: Union[SubField, str] = None) -> None:
        self.tag: int = tag or self.DEFAULT_TAG
        self.value: Optional[str] = None
        if isinstance(value, str):
            self.value = value
        self.subfields: List[SubField] = []
        if isinstance(value, SubField):
            self.subfields.append(value)

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

    def add_non_empty(self, code: str, value: Optional[str]) -> 'Field':
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

    def all(self, code: str) -> List[SubField]:
        """
        Список всех подполей с указанным кодом.

        :param code: Код подполя (однобуквенный).
        :return: Список подполей (возможно, пустой).
        """
        assert len(code) == 1

        code = code.lower()
        return [sf for sf in self.subfields if sf.code == code]

    def all_values(self, code: str) -> List[str]:
        """
        Список значений всех подполей с указанным кодом.
        Пустые значения подполей в список не включаются.

        :param code: Код подполя (однобуквенный).
        :return: Список значений (возможно, пустой).
        """
        assert len(code) == 1

        code = code.lower()
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

    def first(self, code: str) -> Optional[SubField]:
        """
        Находит первое подполе с указанным кодом.
        :param code: Код
        :return: Подполе или None
        """
        assert len(code) == 1

        code = code.lower()
        for subfield in self.subfields:
            if subfield.code == code:
                return subfield
        return None

    def first_value(self, code: str) -> Optional[str]:
        """
        Находит первое подполе с указанным кодом.
        :param code: Код
        :return: Значение подполя или None
        """
        assert len(code) == 1

        code = code.lower()
        for subfield in self.subfields:
            if subfield.code == code:
                return subfield.value
        return None

    def get_embedded_fields(self) -> List['Field']:
        """
        Получение списка встроенных полей.

        :return: Список встроенных полей.
        """
        result: List['Field'] = []
        found: Optional['Field'] = None

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

    def get_value_or_firs_subfield(self) -> Optional[str]:
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

    def replace_subfield(self, code: str, old_value: Optional[str],
                         new_value: Optional[str]) -> 'Field':
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

    def set_subfield(self, code: str, value: Optional[str]) -> 'Field':
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

    def __str__(self):
        if not self.tag:
            return ''
        buffer = [str(self.tag), '#', self.value or ''] \
            + [str(sf) for sf in self.subfields]
        return ''.join(buffer)

    def __iter__(self):
        yield from self.subfields

    def __iadd__(self, other: Union[SubField, Iterable[SubField]]):
        if isinstance(other, SubField):
            self.subfields.append(other)
        else:
            self.subfields.extend(other)
        return self

    def __isub__(self, other: Union[SubField, Iterable[SubField]]):
        if isinstance(other, SubField):
            if other in self.subfields:
                self.subfields.remove(other)
        else:
            for one in other:
                if one in self.subfields:
                    self.subfields.remove(one)
        return self

    def __getitem__(self, item: Union[str, int]):
        if isinstance(item, int):
            return self.subfields[item]
        return self.first(item)

    def __setitem__(self, key: Union[str, int], value: Optional[str]):
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


#############################################################################


class Record:
    """
    MARC record with MFN, status, version and fields.
    """

    __slots__ = 'database', 'mfn', 'version', 'status', 'fields'

    def __init__(self, *fields: Field) -> None:
        self.database: Optional[str] = None
        self.mfn: int = 0
        self.version: int = 0
        self.status: int = 0
        self.fields: List[Field] = []
        self.fields.extend(fields)

    def add(self, tag: int, value: Union[str, SubField] = None) \
            -> 'Field':
        """
        Добавление поля (возможно, с значением и подполями) к записи.

        :param tag: Метка поля.
        :param value: Значение поля (опционально)
        :return: Свежедобавленное поле
        """
        assert tag > 0

        if isinstance(value, str):
            result = Field(tag, value)
        else:
            result = Field(tag)
            if isinstance(value, SubField):
                result.subfields.append(value)

        self.fields.append(result)
        return result

    def add_non_empty(self, tag: int,
                      value: Union[str, SubField]) -> 'Record':
        """
        Добавление поля, если его значение не пустое.

        :param tag: Метка поля.
        :param value: Значение поля (опционально).
        :return: Self
        """
        assert tag > 0

        if value:
            if isinstance(value, str):
                field = Field(tag, value)
            else:
                field = Field(tag)
                if isinstance(value, SubField):
                    field.subfields.append(value)

            self.fields.append(field)

        return self

    def all(self, tag: int) -> List[Field]:
        """
        Список полей с указанной меткой.

        :param tag: Тег
        :return: Список полей (возможно, пустой)
        """
        assert tag > 0

        return [f for f in self.fields if f.tag == tag]

    def clear(self) -> 'Record':
        """
        Очистка записи (удаление всех полей).

        :return: Self
        """
        self.fields.clear()
        return self

    def clone(self) -> 'Record':
        """
        Клонирование записи.

        :return: Полный клон записи
        """
        result = Record()
        result.database = self.database
        result.mfn = self.mfn
        result.status = self.status
        result.version = self.version
        result.fields = [field.clone() for field in self.fields]
        return result

    def encode(self) -> List[str]:
        """
        Кодирование записи в серверное представление.

        :return: Список строк
        """
        result = [str(self.mfn) + '#' + str(self.status),
                  '0#' + str(self.version)]
        for field in self.fields:
            result.append(str(field))
        return result

    def fm(self, tag: int, code: str = '') -> Optional[str]:
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

    def fma(self, tag: int, code: str = '') -> List[str]:
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

    def first(self, tag: int) -> Optional[Field]:
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

    def have_field(self, tag: int) -> bool:
        """
        Есть ли в записи поле с указанной меткой?

        :param tag: Искомая метка поля.
        :return: True или False.
        """
        assert tag > 0

        for field in self.fields:
            if field.tag == tag:
                return True

        return False

    def insert_at(self, index: int, tag: int, value: Optional[str] = None) \
            -> Field:
        """
        Вставка поля в указанной позиции.

        :param index: Позиция для вставки.
        :param tag: Метка поля.
        :param value: Значение поля до первого разделитея (опционально).
        :return: Self
        """
        assert 0 <= index < len(self.fields)
        assert tag > 0

        result = Field(tag, value)
        self.fields.insert(index, result)
        return result

    def is_deleted(self) -> bool:
        """
        Удалена ли запись?
        :return: True для удаленной записи
        """
        return (self.status & (LOGICALLY_DELETED | PHYSICALLY_DELETED)) != 0

    # noinspection DuplicatedCode
    def parse(self, text: List[str]) -> None:
        """
        Разбор текстового представления записи (в серверном формате).

        :param text: Список строк
        :return: None
        """
        if not text:
            return

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
            field = Field()
            field.parse(line)
            self.fields.append(field)

    def remove_at(self, index: int) -> 'Record':
        """
        Удаление поля в указанной позиции.

        :param index: Позиция для удаления.
        :return: Self
        """
        assert 0 <= index < len(self.fields)

        self.fields.remove(self.fields[index])
        return self

    def remove_field(self, tag: int) -> 'Record':
        """
        Удаление полей с указанной меткой.

        :param tag: Метка поля.
        :return: Self.
        """
        assert tag > 0

        index = 0
        while index < len(self.fields):
            field = self.fields[index]
            if field.tag == tag:
                self.fields.remove(field)
            else:
                index += 1

        return self

    def reset(self) -> 'Record':
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

    def set_field(self, tag: int, value: Optional[str]) -> 'Record':
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
                found = Field(tag)
                self.fields.append(found)
            found.value = value
        else:
            if found:
                self.fields.remove(found)

        return self

    def set_subfield(self, tag: int, code: str,
                     value: Optional[str]) -> 'Record':
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
                found = Field(tag)
                self.fields.append(found)
        if found:
            found.set_subfield(code, value)

        return self

    def __str__(self):
        result = [str(field) for field in self.fields]
        return '\n'.join(result)

    def __iter__(self):
        yield from self.fields

    def __iadd__(self, other: Union[Field, Iterable[Field]]):
        if isinstance(other, Field):
            self.fields.append(other)
        else:
            self.fields.extend(other)
        return self

    def __isub__(self, other: Union[Field, Iterable[Field]]):
        if isinstance(other, Field):
            if other in self.fields:
                self.fields.remove(other)
        else:
            for one in other:
                if one in self.fields:
                    self.fields.remove(one)
        return self

    def __getitem__(self, item: int):
        return self.fm(item)

    def __setitem__(self, key: int,
                    value: Union[Field, SubField, str, None]):
        if value is None:
            found: List[Field] = self.all(key)
            for fld in found:
                self.fields.remove(fld)
            return

        field: Optional[Field] = self.first(key)
        if isinstance(value, str):
            if field is None:
                field = Field(key, value)
                self.fields.append(field)
            else:
                field.clear()
                field.headless_parse(value)

        if isinstance(value, Field):
            if field is None:
                field = Field(key)
                self.fields.append(field)
            value.tag = key
            field.assign_from(value)

        if isinstance(value, SubField):
            if field is None:
                field = Field(key)
                self.fields.append(field)
            field.clear()
            field.subfields.append(value)

    def __len__(self):
        return len(self.fields)

    def __bool__(self):
        return bool(self.fields)


class RawRecord:
    """
    Запись с нераскодированными полями/подполями.
    """

    __slots__ = 'database', 'mfn', 'status', 'version', 'fields'

    def __init__(self, *fields: str) -> None:
        self.database: Optional[str] = None
        self.mfn: int = 0
        self.version: int = 0
        self.status: int = 0
        self.fields: List[str] = []
        self.fields.extend(fields)

    def clear(self) -> 'RawRecord':
        """
        Очистка записи (удаление всех полей).

        :return: Self
        """
        self.fields.clear()
        return self

    def clone(self) -> 'RawRecord':
        """
        Клонирование записи.

        :return: Полный клон записи
        """
        result = RawRecord()
        result.database = self.database
        result.mfn = self.mfn
        result.status = self.status
        result.version = self.version
        result.fields = list(field for field in self.fields)
        return result

    def encode(self) -> List[str]:
        """
        Кодирование записи в серверное представление.

        :return: Список строк
        """
        result = [str(self.mfn) + '#' + str(self.status),
                  '0#' + str(self.version)]
        for field in self.fields:
            result.append(field)
        return result

    def is_deleted(self) -> bool:
        """
        Удалена ли запись?
        :return: True для удаленной записи
        """
        return (self.status & (LOGICALLY_DELETED | PHYSICALLY_DELETED)) != 0

    # noinspection DuplicatedCode
    def parse(self, text: List[str]) -> None:
        """
        Разбор текстового представления записи (в серверном формате).

        :param text: Список строк
        :return: None
        """

        if not text:
            return

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
            self.fields.append(line)

    def remove_at(self, index: int) -> 'RawRecord':
        """
        Удаление поля в указанной позиции.

        :param index: Позиция для удаления.
        :return: Self
        """
        assert 0 <= index < len(self.fields)

        self.fields.remove(self.fields[index])
        return self

    def reset(self) -> 'RawRecord':
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

    def __str__(self):
        result = [str(field) for field in self.fields]
        return '\n'.join(result)

    def __iter__(self):
        yield from self.fields

    def __len__(self):
        return len(self.fields)

    def __bool__(self):
        return bool(len(self.fields))


__all__ = ['Field', 'RawRecord', 'Record', 'SubField']

# coding: utf-8

"""
Всё, связанное с INI-файлами.
"""

from typing import Iterable, List, Optional, Union


class IniLine:
    """
    Строка INI-файла.
    """

    __slots__ = 'key', 'value'

    def __init__(self, key: Optional[str] = None,
                 value: Optional[str] = None) -> None:
        self.key = key
        self.value = value

    def __str__(self):
        return str(self.key) + '=' + str(self.value)

    def __repr__(self):
        return self.__str__()


def same_key(first: Optional[str], second: Optional[str]) -> bool:
    """
    Сравнение двух ключей (с точностью до регистра).

    :param first: Первый ключ (может отсутствовать)
    :param second: Второй ключ (может отсутствовать)
    :return: True при совпадении
    """

    if not first or not second:
        return False
    return first.upper() == second.upper()


class IniSection:
    """
    Секция INI-файла.
    """

    __slots__ = 'name', 'lines'

    def __init__(self, name: Optional[str] = None) -> None:
        self.name: Optional[str] = name
        self.lines: List[IniLine] = []

    def find(self, key: str) -> Optional[IniLine]:
        """
        Нахождение строки с указанным ключом.

        :param key: Искомый ключ
        :return: Найденная строка или None
        """
        for line in self.lines:
            if same_key(line.key, key):
                return line
        return None

    def get_value(self, key: str,
                  default: Optional[str] = None) -> Optional[str]:
        """
        Получение значения строки с указанным ключом.

        :param key: Искомый ключ
        :param default: Значение по умолчанию
        :return: Найденное значение или значение по умолчанию
        """
        found = self.find(key)
        return found.value if found else default

    def set_value(self, key: str, value: str) -> None:
        """
        Установка значения строки с указанным ключом.

        :param key: Искомый ключ
        :param value: Устанавливаемое значение
        :return: None
        """
        found = self.find(key)
        if found:
            found.value = value
        else:
            found = IniLine(key, value)
            self.lines.append(found)

    def remove(self, key: str) -> None:
        """
        Удаление строки с указанным ключом.

        :param key: Искомый ключ
        :return: None
        """
        found = self.find(key)
        if found:
            self.lines.remove(found)

    def __str__(self):
        result = []
        if self.name:
            result.append('[' + self.name + ']')
        for line in self.lines:
            result.append(str(line))
        return '\n'.join(result)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        yield from self.lines

    def __getitem__(self, item: Union[str, int]):
        if isinstance(item, int):
            return self.lines[item]
        return self.get_value(item)

    def __len__(self):
        return len(self.lines)

    def __bool__(self):
        return bool(len(self.lines))


class IniFile:
    """
    INI-файл.
    """

    __slots__ = ('sections',)

    def __init__(self):
        self.sections = []

    def find(self, name: str) -> Optional[IniSection]:
        """
        Нахождение секции с указанным именем.

        :param name: Имя секции
        :return: Найденная секция или None
        """
        for section in self.sections:
            if not name and not section.name:
                return section
            if same_key(section.name, name):
                return section
        return None

    def get_or_create(self, name: str) -> IniSection:
        """
        Получение или создание при отсутствии секции с указанным именем.

        :param name: Имя секции
        :return: Найденная или созданная секция
        """
        result = self.find(name)
        if not result:
            result = IniSection(name)
            self.sections.append(result)
        return result

    def get_value(self, name: str, key: str,
                  default: Optional[str] = None) -> Optional[str]:
        """
        Получение значения строки с указанными именем секции и ключом.

        :param name: Имя секции
        :param key: Ключ строки в секции
        :param default: Значение по умолчанию
        :return: Найденное значение или значение по умолчанию
        """
        section = self.find(name)
        if section:
            return section.get_value(key, default)
        return default

    def set_value(self, name: str, key: str, value: str) -> None:
        """
        Установка значения строки с указанными именем секции и ключом.

        :param name: Имя секции
        :param key: Ключ строки в секции
        :param value: Устанавливаемое значение
        :return: None
        """
        section = self.get_or_create(name)
        if not section:
            section = IniSection(name)
            self.sections.append(section)
        section.set_value(key, value)

    def parse(self, text: Iterable[str]) -> None:
        """
        Разбор текстового представления INI-файла.

        :param text: Последовательность текстовых строк
        :return: None
        """
        section = None
        for line in text:
            line = line.strip()
            if not line:
                continue
            if line.startswith('['):
                name = line[1:-1]
                section = self.get_or_create(name)
            else:
                parts = line.split('=', 1)
                key = parts[0]
                value = None
                if len(parts) > 1:
                    value = parts[1]
                item = IniLine(key, value)
                if section is None:
                    section = IniSection()
                    self.sections.append(section)
                section.lines.append(item)

    def __str__(self):
        result = []
        for section in self.sections:
            result.append(str(section))
        return '\n'.join(result)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        yield from self.sections

    def __getitem__(self, item: Union[str, int]):
        if isinstance(item, int):
            return self.sections[item]
        return self.find(item)

    def __len__(self):
        return len(self.sections)

    def __bool__(self):
        return bool(len(self.sections))


__all__ = ['IniFile', 'IniLine', 'IniSection']

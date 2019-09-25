# coding: utf-8

"""
Ресурсы сервера.
"""

from typing import Dict, List, Optional


class Resource:
    """
    Текстовый файл на сервере.
    """

    __slots__ = 'name', 'content'

    def __init__(self, name: str, content: str) -> None:
        self.name: str = name
        self.content: str = content

    def __str__(self) -> str:
        return f"{self.name}: {self.content}"


class ResourceDictionary:
    """
    Словарь текстовых ресурсов.
    """

    __slots__ = ('dictionary',)

    def __init__(self) -> None:
        self.dictionary: Dict[str, Resource] = {}

    def add(self, name: str, content: str) -> 'ResourceDictionary':
        """
        Регистрация ресурса в словаре.
        :param name: Имя
        :param content: Содержимое
        :return: Словарь
        """
        self.dictionary[name] = Resource(name, content)
        return self

    def all(self) -> List[Resource]:
        """
        Все зарегистрированные ресурсы в виде массива.
        :return: Массив
        """
        result: List[Resource] = []
        for item in self.dictionary.values():
            result.append(item)
        return result

    def clear(self) -> 'ResourceDictionary':
        """
        Очистка словаря.
        :return: Словарь
        """
        self.dictionary.clear()
        return self

    def count(self) -> int:
        """
        Вычисление длины словаря.
        :return: Число хранимых ресурсов
        """
        return len(self.dictionary)

    def get(self, name: str) -> Optional[str]:
        """
        Получение ресурса из словаря по имени.
        :param name: Имя
        :return: Содержимое ресурса либо None
        """
        if name in self.dictionary:
            return self.dictionary[name].content
        return None

    def have(self, name: str) -> bool:
        """
        Есть ли элемент с указанным именем в словаре?
        :param name: Имя
        :return: Наличие в словаре
        """
        return name in self.dictionary

    def put(self, name: str, content: str) -> 'ResourceDictionary':
        """
        Добавление ресурса в словарь.
        :param name: Имя
        :param content: Содержимое
        :return: Словарь
        """
        self.dictionary[name] = Resource(name, content)
        return self

    def remove(self, name: str) -> 'ResourceDictionary':
        """
        Удаление ресурса из словаря.
        :param name: Имя
        :return: Словарь
        """
        del self.dictionary[name]
        return self


__all__ = ['Resource', 'ResourceDictionary']

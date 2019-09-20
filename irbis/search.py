# coding: utf-8

"""
Всё, связанное с поиском.
"""

from typing import List, Optional
from ._common import safe_int, safe_str
from .ini import IniFile


class FoundLine:
    """
    Found item in search answer.
    """

    __slots__ = ('mfn', 'description')

    def __init__(self) -> None:
        self.mfn: int = 0
        self.description: Optional[str] = None

    def parse_line(self, line: str) -> None:
        """
        Разбор серверного представления найденной записи.

        :param line: Строка с найденной записью.
        :return: None.
        """
        parts = line.split('#', 2)
        self.mfn = safe_int(parts[0])
        if len(parts) > 1:
            self.description = parts[1]

    def __str__(self):
        return f"{self.mfn}#{self.description}"


class SearchParameters:
    """
    Parameters for search request.
    """

    __slots__ = ('database', 'first', 'format', 'max_mfn', 'min_mfn',
                 'number', 'expression', 'sequential', 'filter', 'utf')

    def __init__(self, expression: Optional[str] = None,
                 number: int = 0) -> None:
        self.database: Optional[str] = None
        self.first: int = 1
        self.format: Optional[str] = None
        self.max_mfn: int = 0
        self.min_mfn: int = 0
        self.number: int = number
        self.expression = expression
        self.sequential: Optional[str] = None
        self.filter: Optional[str] = None
        self.utf = False

    def __str__(self):
        return self.expression


class SearchScenario:
    """
    Сценарий поиска.
    """

    __slots__ = ('name', 'prefix', 'type', 'menu', 'old',
                 'correction', 'truncation', 'hint',
                 'mod_by_dic_auto', 'logic', 'advance',
                 'format')

    def __init__(self, name: Optional[str] = None) -> None:
        self.name: Optional[str] = name
        self.prefix: Optional[str] = None
        self.type: int = 0
        self.menu: Optional[str] = None
        self.old: Optional[str] = None
        self.correction: Optional[str] = None
        self.truncation: bool = False
        self.hint: Optional[str] = None
        self.mod_by_dic_auto: Optional[str] = None
        self.logic: int = 0
        self.advance: Optional[str] = None
        self.format: Optional[str] = None

    @staticmethod
    def parse(ini: IniFile) -> List['SearchScenario']:
        """
        Parse the INI file for the search scenarios.

        :param ini: INI file
        :return: List of search scenarios
        """

        section = ini.find('SEARCH')
        if not section:
            return []
        count = safe_int(safe_str(section.get_value('ItemNumb', '0')))
        if not count:
            return []
        result: List['SearchScenario'] = []
        for i in range(count):
            name = section.get_value(f'ItemName{i}')
            scenario = SearchScenario(name)
            result.append(scenario)
            scenario.prefix = section.get_value(f'ItemPref{i}') or ''
            scenario.type = safe_int(safe_str(section.get_value(
                f'ItemDictionType{i}', '0')))
            scenario.menu = section.get_value(f'ItemMenu{i}')
            scenario.old = None
            scenario.correction = section.get_value(f'ItemModByDic{i}')
            scenario.truncation = bool(section.get_value(
                f'ItemTranc{i}', '0'))
            scenario.hint = section.get_value(f'ItemHint{i}')
            scenario.mod_by_dic_auto = section.get_value(
                f'ItemModByDicAuto{i}')
            scenario.logic = safe_int(safe_str(section.get_value(
                f'ItemLogic{i}', '0')))
            scenario.advance = section.get_value(f'ItemAdv{i}')
            scenario.format = section.get_value(f'ItemPft{i}')
        return result

    def __str__(self):
        if not self.prefix:
            return safe_str(self.name)

        return safe_str(self.name) + ' ' + safe_str(self.prefix)


__all__ = ['FoundLine', 'SearchParameters', 'SearchScenario']

# coding: utf-8

"""
Всё, связанное с поиском.
"""

from typing import TYPE_CHECKING
from irbis._common import safe_int, safe_str
from irbis.ini import IniFile
if TYPE_CHECKING:
    from typing import Any, List, Optional


class FoundLine:
    """
    Found item in search answer.
    """

    __slots__ = ('mfn', 'description')

    def __init__(self) -> None:
        self.mfn: int = 0
        self.description: 'Optional[str]' = None

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

    def __init__(self, expression: 'Optional[str]' = None,
                 number: int = 0) -> None:
        self.database: 'Optional[str]' = None
        self.first: int = 1
        self.format: 'Optional[str]' = None
        self.max_mfn: int = 0
        self.min_mfn: int = 0
        self.number: int = number
        self.expression = expression
        self.sequential: 'Optional[str]' = None
        self.filter: 'Optional[str]' = None
        self.utf = False

    def encode(self, query: 'Any', connection: 'Any') -> None:
        """
        Кодирование параметров поиска в клиентский запрос.

        :param query: Клиентский запрос.
        :param connection: Подключение.
        :return: None.
        """
        database = self.database or connection.database
        query.ansi(database)
        query.utf(self.expression)
        query.add(self.number)
        query.add(self.first)
        query.ansi(self.format)
        query.add(self.min_mfn)
        query.add(self.max_mfn)
        query.ansi(self.sequential)

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

    def __init__(self, name: 'Optional[str]' = None) -> None:
        self.name: 'Optional[str]' = name
        self.prefix: 'Optional[str]' = None
        self.type: int = 0
        self.menu: 'Optional[str]' = None
        self.old: 'Optional[str]' = None
        self.correction: 'Optional[str]' = None
        self.truncation: bool = False
        self.hint: 'Optional[str]' = None
        self.mod_by_dic_auto: 'Optional[str]' = None
        self.logic: int = 0
        self.advance: 'Optional[str]' = None
        self.format: 'Optional[str]' = None

    @staticmethod
    def parse(ini: IniFile) -> 'List[SearchScenario]':
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
        result: 'List[SearchScenario]' = []
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


class TextParameters:
    """
    Параметры полнотекстового поиска для ИРБИС64+.
    """
    __slots__ = ('request', 'words', 'morphology', 'prefix',
                 'max_distance', 'context', 'max_count',
                 'cell_type', 'cell_count')

    def __init__(self) -> None:
        self.request: 'Optional[str]' = None
        self.words: 'List[str]' = []
        self.morphology: bool = False
        self.prefix: 'Optional[str]' = "KT="
        self.max_distance: int = -1
        self.context: 'Optional[str]' = None
        self.max_count: int = 100
        self.cell_type: 'Optional[str]' = None
        self.cell_count: int = 5

    def encode(self, query: 'Any') -> None:
        """
        Кодирование параметров полнотекстового поиска в клиентский запрос.

        :param query: Клиентский запрос.
        :return: None
        """
        delimiter: str = '\x1F'
        morpho = '0'
        if self.morphology:
            morpho = '1'
        line = (self.request or '') + delimiter + \
            ','.join(self.words) + delimiter + \
            morpho + delimiter + \
            (self.prefix or '') + delimiter + \
            str(self.max_distance) + delimiter + \
            (self.context or '') + delimiter + \
            str(self.max_count) + delimiter + \
            (self.cell_type or '') + delimiter + \
            str(self.cell_count)
        query.utf(line)


class TextResult:
    """
    Результат полнотекстового поиска
    """
    __slots__ = ('mfn', 'pages', 'formatted')

    def __init__(self) -> None:
        self.mfn: int = 0
        self.pages: 'List[int]' = []
        self.formatted: 'Optional[str]' = None

    def decode(self, line: str) -> None:
        """
        Декодирование строки с одним результатом полнотекстового поиска.
        """
        parts = line.split('#', 2)
        self.mfn = int(parts[0])
        if len(parts) == 3:
            self.formatted = parts[2]
        if len(parts) > 1:
            parts = parts[1].split('\x1F')
            for part in parts:
                if part.isdecimal():
                    page = int(part)
                    self.pages.append(page)


__all__ = ['FoundLine', 'SearchParameters', 'SearchScenario', 'TextParameters',
           'TextResult']

# coding: utf-8

"""
Модуль содержит основную функциональность по работе с сервером ИРБИС64,
в т. ч. для манипуляций с записями.
"""

# ManagedIrbis ported from C# to Python.
# Python supported: 3.6 and higher
# IRBIS64 supported: 2014 and higher

from ._common import ADMINISTRATOR, BRIEF, close_async, init_async, \
    irbis_event_loop

from .alphabet import AlphabetTable, load_alphabet_table, UpperCaseTable, \
    load_uppercase_table
from .database import DatabaseInfo
from .error import IrbisError, IrbisFileNotFoundError
from .ini import IniFile, IniLine, IniSection
from .menus import load_menu, MenuEntry, MenuFile
from .opt import load_opt_file, OptFile
from .par import load_par_file, ParFile
from .process import Process
from .query import ClientQuery
from .record import Field, RawRecord, Record, SubField
from .response import ServerResponse
from .search import FoundLine, SearchParameters, SearchScenario
from .specification import FileSpecification
from .terms import PostingParameters, TermInfo, TermParameters, TermPosting
from .tree import load_tree_file, TreeFile, TreeNode
from .version import ServerVersion

from .connection import Connection

__version__ = '0.1.100'
__author__ = 'Alexey Mironov'
__email__ = 'amironov73@gmail.com'

__title__ = 'irbis'
__summary__ = 'ManagedIrbis ported from C# to Python'
__uri__ = 'http://arsmagna.ru'

__license__ = 'MIT License'
__copyright__ = 'Copyright 2018-2019 Alexey Mironov'

__all__ = ['ADMINISTRATOR', 'AlphabetTable', 'BRIEF', 'ClientQuery',
           'Connection', 'close_async', 'DatabaseInfo', 'irbis_event_loop',
           'IrbisError', 'IrbisFileNotFoundError', 'Field',
           'FileSpecification', 'FoundLine', 'IniFile', 'IniLine',
           'IniSection', 'init_async', 'load_alphabet_table', 'load_menu',
           'load_opt_file', 'load_par_file', 'load_tree_file',
           'load_uppercase_table', 'MenuEntry', 'MenuFile', 'OptFile',
           'ParFile', 'PostingParameters', 'Process', 'RawRecord',
           'Record', 'SearchParameters', 'SearchScenario',
           'ServerResponse', 'ServerVersion', 'SubField', 'TermInfo',
           'TermParameters', 'TermPosting', 'TreeFile', 'TreeNode',
           'UpperCaseTable']

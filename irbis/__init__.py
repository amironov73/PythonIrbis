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
from .record import Field, Record, SubField
from .error import IrbisError
from .ini import IniFile, IniLine, IniSection
from .query import ClientQuery
from .specification import FileSpecification
from .response import ServerResponse
from .search import FoundLine, SearchParameters
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

__all__ = ['ADMINISTRATOR', 'BRIEF', 'ClientQuery', 'Connection',
           'close_async', 'irbis_event_loop', 'IrbisError', 'Field',
           'FileSpecification', 'FoundLine', 'IniFile', 'IniLine',
           'IniSection', 'init_async', 'Record', 'SearchParameters',
           'ServerResponse', 'ServerVersion', 'SubField']

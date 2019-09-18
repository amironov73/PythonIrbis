# coding: utf-8

"""
Модуль содержит основную функциональность по работе с сервером ИРБИС64,
в т. ч. для манипуляций с записями.
"""

# ManagedIrbis ported from C# to Python.
# Python supported: 3.6 and higher
# IRBIS64 supported: 2014 and higher

from .record import MarcRecord, RecordField, SubField
from .error import IrbisError
from .query import ClientQuery
from .connection import Connection
from .response import ServerResponse
from .specification import FileSpecification

__version__ = '0.1.100'
__author__ = 'Alexey Mironov'
__email__ = 'amironov73@gmail.com'

__title__ = 'irbis'
__summary__ = 'ManagedIrbis ported from C# to Python'
__uri__ = 'http://arsmagna.ru'


__license__ = 'MIT License'
__copyright__ = 'Copyright 2018-2019 Alexey Mironov'

__all__ = ['ClientQuery', 'Connection', 'IrbisError', 'FileSpecification',
           'MarcRecord', 'RecordField', 'ServerResponse', 'SubField']

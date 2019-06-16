# coding: utf-8

"""
Search expression builder.
"""

from typing import Any

###############################################################################

class Search:
    """
    Search expression builder class.
    """

    __slots__ = ('_buffer',)

    def __init__(self) -> None:
        self._buffer = ''

    @staticmethod
    def all() -> 'Search':
        """
        All documents in the database.
        """
        result = Search()
        result._buffer = 'I=$'
        return result

    def and_(self, *items: Any) -> 'Search':
        """
        Logical AND.
        """
        self._buffer = '(' + self._buffer
        for item in items:
            self._buffer = self._buffer + ' * ' + Search.wrap(item)
        self._buffer = self._buffer + ')'
        return self

    @staticmethod
    def equals(prefix: str, *values: Any) -> 'Search':
        """
        Prefix search for matching records.
        """
        result = Search()
        text = Search.wrap(prefix + str(values[0]))
        if len(values) > 1:
            text = '(' + text
            for item in values[1:len(values)]:
                text = text + ' + ' + Search.wrap(prefix + str(item))
            text = text + ')'
        result._buffer = text
        return result

    @staticmethod
    def need_wrap(text: str) -> bool:
        """
        Need wrap the text?
        """
        if not text:
            return True
        if text[0] in '"(':
            return False
        for c in text:
            if c in ' +*^()"#':
                return True
        return False

    def not_(self, text: Any) -> 'Search':
        """
        Logical NOT.
        """
        self._buffer = '(' + self._buffer + ' ^ ' + Search.wrap(text) + ')'
        return self

    def or_(self, *items: Any) -> 'Search':
        """
        Logical OR.
        """
        self._buffer = '(' + self._buffer
        for item in items:
            self._buffer = self._buffer + ' + ' + Search.wrap(item)
        self._buffer = self._buffer + ')'
        return self

    def same_field(self, *items: Any) -> 'Search':
        """
        Logical "Same field"
        """
        self._buffer = '(' + self._buffer
        for item in items:
            self._buffer = self._buffer + ' (G) ' + Search.wrap(item)
        self._buffer = self._buffer + ')'
        return self

    def same_repeat(self, *items: Any) -> 'Search':
        """
        Logical "Same field repeat"
        """
        self._buffer = '(' + self._buffer
        for item in items:
            self._buffer = self._buffer + ' (F) ' + Search.wrap(item)
        self._buffer = self._buffer + ')'
        return self

    @staticmethod
    def wrap(text: Any) -> str:
        """
        Wrap the text if needed.
        """
        text = str(text)
        if Search.need_wrap(text):
            return '"' + text + '"'
        return text

    def __str__(self):
        return self._buffer

###############################################################################

def keyword(*values: Any) -> Search:
    return Search.equals('K=', *values)

def author(*values: Any) -> Search:
    return Search.equals('A=', *values)

def title(*values: Any) -> Search:
    return Search.equals('T=', *values)

def number(*values: Any) -> Search:
    return Search.equals('IN=', *values)

def publisher(*values: Any) -> Search:
    return Search.equals('O=', *values)

def place(*values: Any) -> Search:
    return Search.equals('MI=', *values)

def subject(*values: Any) -> Search:
    return Search.equals('S=', *values)

def language(*values: Any) -> Search:
    return Search.equals('J=', *values)

def year(*values: Any) -> Search:
    return Search.equals('G=', *values)

def magazine(*values: Any) -> Search:
    return Search.equals('TJ=', *values)

def documentKind(*values: Any) -> Search:
    return Search.equals('V=', *values)

def udc(*values: Any) -> Search:
    return Search.equals('U=', *values)

def bbk(*values: Any) -> Search:
    return Search.equals('BBK=', *values)

def rzn(*values: Any) -> Search:
    return Search.equals('RZN=', *values)

def mhr(*values: Any) -> Search:
    return Search.equals('MHR=', *values)

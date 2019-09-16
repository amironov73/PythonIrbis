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

    __slots__ = ('buffer',)

    def __init__(self) -> None:
        self.buffer = ''

    @staticmethod
    def all() -> 'Search':
        """
        All documents in the database.
        """
        result = Search()
        result.buffer = 'I=$'
        return result

    def and_(self, *items: Any) -> 'Search':
        """
        Logical AND.
        """
        self.buffer = '(' + self.buffer
        for item in items:
            self.buffer = self.buffer + ' * ' + Search.wrap(item)
        self.buffer = self.buffer + ')'
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
        result.buffer = text
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
        for one in text:
            if one in ' +*^()"#':
                return True
        return False

    def not_(self, text: Any) -> 'Search':
        """
        Logical NOT.
        """
        self.buffer = '(' + self.buffer + ' ^ ' + Search.wrap(text) + ')'
        return self

    def or_(self, *items: Any) -> 'Search':
        """
        Logical OR.
        """
        self.buffer = '(' + self.buffer
        for item in items:
            self.buffer = self.buffer + ' + ' + Search.wrap(item)
        self.buffer = self.buffer + ')'
        return self

    def same_field(self, *items: Any) -> 'Search':
        """
        Logical "Same field"
        """
        self.buffer = '(' + self.buffer
        for item in items:
            self.buffer = self.buffer + ' (G) ' + Search.wrap(item)
        self.buffer = self.buffer + ')'
        return self

    def same_repeat(self, *items: Any) -> 'Search':
        """
        Logical "Same field repeat"
        """
        self.buffer = '(' + self.buffer
        for item in items:
            self.buffer = self.buffer + ' (F) ' + Search.wrap(item)
        self.buffer = self.buffer + ')'
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
        return self.buffer

###############################################################################


def keyword(*values: Any) -> Search:
    """
    Поиск по ключевым словам.

    :param values: Искомые ключевые слова.
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('K=', *values)


def author(*values: Any) -> Search:
    """
    Поиск по индивидуальным авторам.

    :param values: Искомые авторы.
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('A=', *values)


def title(*values: Any) -> Search:
    """
    Поиск по заглавиям.

    :param values: Искомые заглавия.
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('T=', *values)


def number(*values: Any) -> Search:
    """
    Поиск по инвентарным номерам.

    :param values: Искомые номера.
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('IN=', *values)


def publisher(*values: Any) -> Search:
    """
    Поиск по издательству.

    :param values: Искомые издательства.
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('O=', *values)


def place(*values: Any) -> Search:
    """
    Поиск по месту издания (городу).

    :param values: Искомые места (города).
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('MI=', *values)


def subject(*values: Any) -> Search:
    """
    Поиск по предметным рубрикам.

    :param values: Искомые рубрики.
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('S=', *values)


def language(*values: Any) -> Search:
    """
    Поиск по языку документа.

    :param values: Искомые языки.
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('J=', *values)


def year(*values: Any) -> Search:
    """
    Поиск по году издания.

    :param values: Искомые годы.
    :return: Построитель запросов.
    """
    assert values
    return Search.equals('G=', *values)


def magazine(*values: Any) -> Search:
    """
    Поиск по заглавиям журналов.

    :param values: Искомые заглавия журналов.
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('TJ=', *values)


def document_kind(*values: Any) -> Search:
    """
    Поиск по виду документа.

    :param values: Искомые виды документов.
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('V=', *values)


def udc(*values: Any) -> Search:
    """
    Поиск по индексам УДК.

    :param values: Искомые индексы ББК.
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('U=', *values)


def bbk(*values: Any) -> Search:
    """
    Поиск по индексам ББК.

    :param values: Искомые индексы ББК.
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('BBK=', *values)


def rzn(*values: Any) -> Search:
    """
    Поиск по разделу знаний.

    :param values: Искомые разделы знаний.
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('RZN=', *values)


def mhr(*values: Any) -> Search:
    """
    Поиск по месту хранения.

    :param values: Искомые места хранения.
    :return: Построитель запросов.
    """
    assert values

    return Search.equals('MHR=', *values)

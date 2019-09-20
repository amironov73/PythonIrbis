# coding: utf-8

"""
Работа с терминами словаря.
"""

from typing import Iterable, List, Optional
from ._common import safe_str


class PostingParameters:
    """
    Параметры для команды ReadPostings.
    """

    __slots__ = 'database', 'first', 'fmt', 'number', 'terms'

    def __init__(self, term: str = None, fmt: str = None) -> None:
        self.database: Optional[str] = None
        self.first: int = 1
        self.fmt: Optional[str] = fmt
        self.number: int = 0
        self.terms: List[str] = []
        if term:
            self.terms.append(term)

    def __str__(self):
        return str(self.terms)


class TermInfo:
    """
    Информация о поисковом терме.
    """

    __slots__ = 'count', 'text'

    def __init__(self, count: int = 0, text: str = '') -> None:
        self.count: int = count
        self.text: str = text

    @staticmethod
    def parse(lines: Iterable[str]):
        """
        Parse the text for term info.

        :param lines: Text to parse
        :return: Term info
        """
        result = []
        for line in lines:
            parts = line.split('#', 1)
            item = TermInfo(int(parts[0]), parts[1])
            result.append(item)
        return result

    def __str__(self):
        return str(self.count) + '#' + self.text


class TermParameters:
    """
    Параметры для команды ReadTerms
    """

    __slots__ = 'database', 'number', 'reverse', 'start', 'format'

    def __init__(self, start: str = None, number: int = 10) -> None:
        self.database: str = ''
        self.number: int = number
        self.reverse: bool = False
        self.start: Optional[str] = start
        self.format: Optional[str] = None

    def __str__(self):
        return str(self.number) + ' ' + safe_str(self.format)


class TermPosting:
    """
    Постинг терма.
    """

    __slots__ = 'mfn', 'tag', 'occurrence', 'count', 'text'

    def __init__(self) -> None:
        self.mfn: int = 0
        self.tag: int = 0
        self.occurrence: int = 0
        self.count: int = 0
        self.text: Optional[str] = None

    def parse(self, text: str) -> None:
        """
        Parse the text for term postings.

        :param text: Text to parse
        :return: None
        """

        parts = text.split('#', 4)
        if len(parts) < 4:
            return
        self.mfn = int(parts[0])
        self.tag = int(parts[1])
        self.occurrence = int(parts[2])
        self.count = int(parts[3])
        if len(parts) > 4:
            self.text = parts[4]

    def __str__(self):
        subst = ''
        if self.text:
            subst = self.text
        return ' '.join([str(self.mfn), str(self.tag),
                         str(self.occurrence), str(self.count),
                         subst])


__all__ = ['PostingParameters', 'TermInfo', 'TermParameters', 'TermPosting']

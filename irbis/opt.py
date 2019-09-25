# coding: utf-8

"""
Работа с OPT-файлами.
"""

import re
from typing import List, Optional
from ._common import ANSI, STOP_MARKER


class OptLine:
    """
    Строка в OPT-файле.
    """

    __slots__ = 'pattern', 'worksheet'

    def __init__(self, pattern: str = '', worksheet: str = '') -> None:
        self.pattern: str = pattern
        self.worksheet: str = worksheet

    def parse(self, text: str) -> None:
        """
        Parse the line.

        :param text: Text to parse
        :return: None
        """
        parts = re.split(r'\s+', text.strip())
        self.pattern = parts[0]
        self.worksheet = parts[1]


class OptFile:
    """
    OPT-файл.
    """

    WILDCARD = '+'

    __slots__ = 'lines', 'length', 'tag'

    def __init__(self):
        self.lines: List[OptLine] = []
        self.length: int = 5
        self.tag: int = 920

    def parse(self, text: List[str]) -> None:
        """
        Parse the text for OPT table.

        :param text: Text to parse
        :return: None
        """
        self.tag = int(text[0])
        self.length = int(text[1])
        for line in text[2:]:
            if not line:
                continue
            line = line.strip()
            if not line:
                continue
            if line.startswith('*'):
                continue
            one = OptLine()
            one.parse(line)
            self.lines.append(one)

    @staticmethod
    def same_char(pattern: str, testable: str) -> bool:
        """
        Compare the character against the pattern.

        :param pattern: Pattern character
        :param testable: Character to examine
        :return: True or False
        """
        if pattern == OptFile.WILDCARD:
            return True
        return pattern.lower() == testable.lower()

    def same_text(self, pattern: str, testable: str) -> bool:
        """
        Compare tag value against the OPT pattern.

        :param pattern: Pattern to use
        :param testable: Tag value to examine
        :return: True or False
        """

        if not pattern:
            return False

        if not testable:
            return pattern[0] == OptFile.WILDCARD

        pattern_index = 0
        testable_index = 0

        while True:
            pattern_char = pattern[pattern_index]
            testable_char = testable[testable_index]
            pattern_index += 1
            testable_index += 1
            pattern_next = pattern_index < len(pattern)
            testable_next = testable_index < len(testable)

            if pattern_next and not testable_next:
                if pattern_char == OptFile.WILDCARD:
                    while pattern_index < len(pattern):
                        pattern_char = pattern[pattern_index]
                        pattern_index += 1

                        if pattern_char != OptFile.WILDCARD:
                            return False

                    return True

            if pattern_next != testable_next:
                return False

            if not pattern_next:
                return True

            if not self.same_char(pattern_char, testable_char):
                return False

    def resolve_worksheet(self, tag: str) -> Optional[str]:
        """
        Resolve worksheet for the specified tag value.

        :param tag: Tag value, e. g. "SPEC"
        :return: Worksheet name or None
        """

        for line in self.lines:
            if self.same_text(line.pattern, tag):
                return line.worksheet

        return None

    def save(self, filename: str) -> None:
        """
        Save the OPT table to the specified file.

        :param filename: Name of the file
        :return: None
        """
        with open(filename, 'wt', encoding=ANSI) as stream:
            text = str(self)
            stream.write(text)

    def __str__(self):
        result = [str(self.tag), str(self.length)]
        for line in self.lines:
            result.append(line.pattern.ljust(6) + line.worksheet)
        result.append(STOP_MARKER)
        return '\n'.join(result)


def load_opt_file(filename: str) -> OptFile:
    """
    Load the OPT from the specified file.

    :param filename: Name of the file
    :return: OPT file
    """

    result = OptFile()
    with open(filename, 'rt', encoding=ANSI) as stream:
        lines = stream.readlines()
        result.parse(lines)
    return result


__all__ = ['load_opt_file', 'OptFile', 'OptLine']

# coding: utf-8

"""
Работа с алфавитной таблицей.
"""

import re
from typing import Dict, Generator, List
from ._common import ANSI


class AlphabetTable:
    """
    Alphabet character table
    """

    FILENAME = 'isisacw.tab'

    __slots__ = ('characters',)

    def __init__(self) -> None:
        self.characters: List[str] = []

    @staticmethod
    def get_default():
        """
        Get the default alphabet table.

        :return: Alphabet table
        """
        result = AlphabetTable()
        result.characters = [
            '\u0026', '\u0040', '\u0041', '\u0042', '\u0043', '\u0044',
            '\u0045', '\u0046', '\u0047', '\u0048', '\u0049', '\u004A',
            '\u004B', '\u004C', '\u004D', '\u004E', '\u004F', '\u0050',
            '\u0051', '\u0052', '\u0053', '\u0054', '\u0055', '\u0056',
            '\u0057', '\u0058', '\u0059', '\u005A', '\u0061', '\u0062',
            '\u0063', '\u0064', '\u0065', '\u0066', '\u0067', '\u0068',
            '\u0069', '\u006A', '\u006B', '\u006C', '\u006D', '\u006E',
            '\u006F', '\u0070', '\u0071', '\u0072', '\u0073', '\u0074',
            '\u0075', '\u0076', '\u0077', '\u0078', '\u0079', '\u007A',
            '\u0098', '\u00A0', '\u00A4', '\u00A6', '\u00A7', '\u00A9',
            '\u00AB', '\u00AC', '\u00AD', '\u00AE', '\u00B0', '\u00B1',
            '\u00B5', '\u00B6', '\u00B7', '\u00BB', '\u0401', '\u0402',
            '\u0403', '\u0404', '\u0405', '\u0406', '\u0407', '\u0408',
            '\u0409', '\u040A', '\u040B', '\u040C', '\u040E', '\u040F',
            '\u0410', '\u0411', '\u0412', '\u0413', '\u0414', '\u0415',
            '\u0416', '\u0417', '\u0418', '\u0419', '\u041A', '\u041B',
            '\u041C', '\u041D', '\u041E', '\u041F', '\u0420', '\u0421',
            '\u0422', '\u0423', '\u0424', '\u0425', '\u0426', '\u0427',
            '\u0428', '\u0429', '\u042A', '\u042B', '\u042C', '\u042D',
            '\u042E', '\u042F', '\u0430', '\u0431', '\u0432', '\u0433',
            '\u0434', '\u0435', '\u0436', '\u0437', '\u0438', '\u0439',
            '\u043A', '\u043B', '\u043C', '\u043D', '\u043E', '\u043F',
            '\u0440', '\u0441', '\u0442', '\u0443', '\u0444', '\u0445',
            '\u0446', '\u0447', '\u0448', '\u0449', '\u044A', '\u044B',
            '\u044C', '\u044D', '\u044E', '\u044F', '\u0451', '\u0452',
            '\u0453', '\u0454', '\u0455', '\u0456', '\u0457', '\u0458',
            '\u0459', '\u045A', '\u045B', '\u045C', '\u045E', '\u045F',
            '\u0490', '\u0491', '\u2013', '\u2014', '\u2018', '\u2019',
            '\u201A', '\u201C', '\u201D', '\u201E', '\u2020', '\u2021',
            '\u2022', '\u2026', '\u2030', '\u2039', '\u203A', '\u20AC',
            '\u2116', '\u2122'
        ]
        return result

    def is_alpha(self, char: str) -> bool:
        """
        Determine whether the character is in the alphabet.

        :param char: Character to examine
        :return: True or False
        """

        return char in self.characters

    def parse(self, text: str) -> None:
        """
        Parse the text for alphabet table.

        :param text: Text to parse
        :return: None
        """

        parts = re.findall(r'\d+', text)
        array = bytearray(int(x) for x in parts if x and x.isdigit())
        array.remove(0x98)  # Этот символ не мапится
        self.characters = list(array.decode(ANSI))

    def split_words(self, text: str) -> Generator:
        """
        Split the text to words according the alphabet table.

        :param text: Text to split
        :return: List of words
        """

        accumulator = []
        for char in text:
            if char in self.characters:
                accumulator.append(char)
            else:
                if accumulator:
                    yield ''.join(accumulator)
                    accumulator.clear()
        if accumulator:
            yield ''.join(accumulator)

    def trim(self, text: str) -> str:
        """
        Trim the text according to the alphabet table.

        :param text: Text to trim
        :return: Trimmed text
        """
        result = text
        while result and result[0] not in self.characters:
            result = result[1:]
        while result and result[-1] not in self.characters:
            result = result[:-1]
        return result


def load_alphabet_table(filename: str) -> AlphabetTable:
    """
    Load the alphabet table from the specified file.

    :param filename: Name of the file
    :return: Alphabet table
    """
    with open(filename, 'rt', encoding=ANSI) as stream:
        text = stream.read()
    result = AlphabetTable()
    result.parse(text)
    return result


class UpperCaseTable:
    """
    Upper-case character table.
    """

    FILENAME = 'isisucw.tab'

    __slots__ = ('mapping',)

    def __init__(self) -> None:
        self.mapping: Dict = dict()

    @staticmethod
    def get_default():
        """
        Get the default uppercase table.

        :return: Uppercase table
        """
        result = UpperCaseTable()
        result.mapping = {
            chr(0x0000): chr(0x0000),
            chr(0x0001): chr(0x0001),
            chr(0x0002): chr(0x0002),
            chr(0x0003): chr(0x0003),
            chr(0x0004): chr(0x0004),
            chr(0x0005): chr(0x0005),
            chr(0x0006): chr(0x0006),
            chr(0x0007): chr(0x0007),
            chr(0x0008): chr(0x0008),
            chr(0x0009): chr(0x0009),
            chr(0x000A): chr(0x000A),
            chr(0x000B): chr(0x000B),
            chr(0x000C): chr(0x000C),
            chr(0x000D): chr(0x000D),
            chr(0x000E): chr(0x000E),
            chr(0x000F): chr(0x000F),
            chr(0x0010): chr(0x0010),
            chr(0x0011): chr(0x0011),
            chr(0x0012): chr(0x0012),
            chr(0x0013): chr(0x0013),
            chr(0x0014): chr(0x0014),
            chr(0x0015): chr(0x0015),
            chr(0x0016): chr(0x0016),
            chr(0x0017): chr(0x0017),
            chr(0x0018): chr(0x0018),
            chr(0x0019): chr(0x0019),
            chr(0x001A): chr(0x001A),
            chr(0x001B): chr(0x001B),
            chr(0x001C): chr(0x001C),
            chr(0x001D): chr(0x001C),
            chr(0x001E): chr(0x001E),
            chr(0x001F): chr(0x001F),
            chr(0x0020): chr(0x0020),
            chr(0x0021): chr(0x0021),
            chr(0x0022): chr(0x0022),
            chr(0x0023): chr(0x0023),
            chr(0x0024): chr(0x0024),
            chr(0x0025): chr(0x0025),
            chr(0x0026): chr(0x0026),
            chr(0x0027): chr(0x0027),
            chr(0x0028): chr(0x0028),
            chr(0x0029): chr(0x0029),
            chr(0x002A): chr(0x002A),
            chr(0x002B): chr(0x002B),
            chr(0x002C): chr(0x002C),
            chr(0x002D): chr(0x002D),
            chr(0x002E): chr(0x002E),
            chr(0x002F): chr(0x002F),
            chr(0x0030): chr(0x0030),
            chr(0x0031): chr(0x0031),
            chr(0x0032): chr(0x0032),
            chr(0x0033): chr(0x0033),
            chr(0x0034): chr(0x0034),
            chr(0x0035): chr(0x0035),
            chr(0x0036): chr(0x0036),
            chr(0x0037): chr(0x0037),
            chr(0x0038): chr(0x0038),
            chr(0x0039): chr(0x0039),
            chr(0x003A): chr(0x003A),
            chr(0x003B): chr(0x003B),
            chr(0x003C): chr(0x003C),
            chr(0x003D): chr(0x003D),
            chr(0x003E): chr(0x003E),
            chr(0x003F): chr(0x003F),
            chr(0x0040): chr(0x0040),
            chr(0x0041): chr(0x0041),
            chr(0x0042): chr(0x0042),
            chr(0x0043): chr(0x0043),
            chr(0x0044): chr(0x0044),
            chr(0x0045): chr(0x0045),
            chr(0x0046): chr(0x0046),
            chr(0x0047): chr(0x0047),
            chr(0x0048): chr(0x0048),
            chr(0x0049): chr(0x0049),
            chr(0x004A): chr(0x004A),
            chr(0x004B): chr(0x004B),
            chr(0x004C): chr(0x004C),
            chr(0x004D): chr(0x004D),
            chr(0x004E): chr(0x004E),
            chr(0x004F): chr(0x004F),
            chr(0x0050): chr(0x0050),
            chr(0x0051): chr(0x0051),
            chr(0x0052): chr(0x0052),
            chr(0x0053): chr(0x0053),
            chr(0x0054): chr(0x0054),
            chr(0x0055): chr(0x0055),
            chr(0x0056): chr(0x0056),
            chr(0x0057): chr(0x0057),
            chr(0x0058): chr(0x0058),
            chr(0x0059): chr(0x0059),
            chr(0x005A): chr(0x005A),
            chr(0x005B): chr(0x005B),
            chr(0x005C): chr(0x005C),
            chr(0x005D): chr(0x005D),
            chr(0x005E): chr(0x005E),
            chr(0x005F): chr(0x005F),
            chr(0x0060): chr(0x0060),
            chr(0x0061): chr(0x0041),
            chr(0x0062): chr(0x0042),
            chr(0x0063): chr(0x0043),
            chr(0x0064): chr(0x0044),
            chr(0x0065): chr(0x0045),
            chr(0x0066): chr(0x0046),
            chr(0x0067): chr(0x0047),
            chr(0x0068): chr(0x0048),
            chr(0x0069): chr(0x0049),
            chr(0x006A): chr(0x004A),
            chr(0x006B): chr(0x004B),
            chr(0x006C): chr(0x004C),
            chr(0x006D): chr(0x004D),
            chr(0x006E): chr(0x004E),
            chr(0x006F): chr(0x004F),
            chr(0x0070): chr(0x0050),
            chr(0x0071): chr(0x0051),
            chr(0x0072): chr(0x0052),
            chr(0x0073): chr(0x0053),
            chr(0x0074): chr(0x0054),
            chr(0x0075): chr(0x0055),
            chr(0x0076): chr(0x0056),
            chr(0x0077): chr(0x0057),
            chr(0x0078): chr(0x0058),
            chr(0x0079): chr(0x0059),
            chr(0x007A): chr(0x005A),
            chr(0x007B): chr(0x007B),
            chr(0x007C): chr(0x007C),
            chr(0x007D): chr(0x007D),
            chr(0x007E): chr(0x007E),
            chr(0x007F): chr(0x007F),
            chr(0x0402): chr(0x0402),
            chr(0x0403): chr(0x0403),
            chr(0x201A): chr(0x201A),
            chr(0x0453): chr(0x0453),
            chr(0x201E): chr(0x201E),
            chr(0x2026): chr(0x2026),
            chr(0x2020): chr(0x2020),
            chr(0x2021): chr(0x2021),
            chr(0x20AC): chr(0x20AC),
            chr(0x2030): chr(0x2030),
            chr(0x0409): chr(0x0409),
            chr(0x2039): chr(0x2039),
            chr(0x040A): chr(0x040A),
            chr(0x040C): chr(0x040C),
            chr(0x040B): chr(0x040B),
            chr(0x040F): chr(0x040F),
            chr(0x0452): chr(0x0452),
            chr(0x2018): chr(0x2018),
            chr(0x2019): chr(0x2019),
            chr(0x201C): chr(0x201C),
            chr(0x201D): chr(0x201D),
            chr(0x2022): chr(0x2022),
            chr(0x2013): chr(0x2013),
            chr(0x2014): chr(0x2014),
            chr(0x0098): chr(0x0098),
            chr(0x2122): chr(0x2122),
            chr(0x0459): chr(0x0459),
            chr(0x203A): chr(0x203A),
            chr(0x045A): chr(0x045A),
            chr(0x045C): chr(0x045C),
            chr(0x045B): chr(0x045B),
            chr(0x045F): chr(0x045F),
            chr(0x00A0): chr(0x00A0),
            chr(0x040E): chr(0x040E),
            chr(0x045E): chr(0x040E),
            chr(0x0408): chr(0x0408),
            chr(0x00A4): chr(0x00A4),
            chr(0x0490): chr(0x0490),
            chr(0x00A6): chr(0x00A6),
            chr(0x00A7): chr(0x00A7),
            chr(0x0401): chr(0x0401),
            chr(0x00A9): chr(0x00A9),
            chr(0x0404): chr(0x0404),
            chr(0x00AB): chr(0x00AB),
            chr(0x00AC): chr(0x00AC),
            chr(0x00AD): chr(0x00AD),
            chr(0x00AE): chr(0x00AE),
            chr(0x0407): chr(0x0407),
            chr(0x00B0): chr(0x00B0),
            chr(0x00B1): chr(0x00B1),
            chr(0x0406): chr(0x0406),
            chr(0x0456): chr(0x0406),
            chr(0x0491): chr(0x0490),
            chr(0x00B5): chr(0x00B5),
            chr(0x00B6): chr(0x00B6),
            chr(0x00B7): chr(0x00B7),
            chr(0x0451): chr(0x0401),
            chr(0x2116): chr(0x2116),
            chr(0x0454): chr(0x0404),
            chr(0x00BB): chr(0x00BB),
            chr(0x0458): chr(0x0408),
            chr(0x0405): chr(0x0405),
            chr(0x0455): chr(0x0405),
            chr(0x0457): chr(0x0407),
            chr(0x0410): chr(0x0410),
            chr(0x0411): chr(0x0411),
            chr(0x0412): chr(0x0412),
            chr(0x0413): chr(0x0413),
            chr(0x0414): chr(0x0414),
            chr(0x0415): chr(0x0415),
            chr(0x0416): chr(0x0416),
            chr(0x0417): chr(0x0417),
            chr(0x0418): chr(0x0418),
            chr(0x0419): chr(0x0419),
            chr(0x041A): chr(0x041A),
            chr(0x041B): chr(0x041B),
            chr(0x041C): chr(0x041C),
            chr(0x041D): chr(0x041D),
            chr(0x041E): chr(0x041E),
            chr(0x041F): chr(0x041F),
            chr(0x0420): chr(0x0420),
            chr(0x0421): chr(0x0421),
            chr(0x0422): chr(0x0422),
            chr(0x0423): chr(0x0423),
            chr(0x0424): chr(0x0424),
            chr(0x0425): chr(0x0425),
            chr(0x0426): chr(0x0426),
            chr(0x0427): chr(0x0427),
            chr(0x0428): chr(0x0428),
            chr(0x0429): chr(0x0429),
            chr(0x042A): chr(0x042A),
            chr(0x042B): chr(0x042B),
            chr(0x042C): chr(0x042C),
            chr(0x042D): chr(0x042D),
            chr(0x042E): chr(0x042E),
            chr(0x042F): chr(0x042F),
            chr(0x0430): chr(0x0410),
            chr(0x0431): chr(0x0411),
            chr(0x0432): chr(0x0412),
            chr(0x0433): chr(0x0413),
            chr(0x0434): chr(0x0414),
            chr(0x0435): chr(0x0415),
            chr(0x0436): chr(0x0416),
            chr(0x0437): chr(0x0417),
            chr(0x0438): chr(0x0418),
            chr(0x0439): chr(0x0419),
            chr(0x043A): chr(0x041A),
            chr(0x043B): chr(0x041B),
            chr(0x043C): chr(0x041C),
            chr(0x043D): chr(0x041D),
            chr(0x043E): chr(0x041E),
            chr(0x043F): chr(0x041F),
            chr(0x0440): chr(0x0420),
            chr(0x0441): chr(0x0421),
            chr(0x0442): chr(0x0422),
            chr(0x0443): chr(0x0423),
            chr(0x0444): chr(0x0424),
            chr(0x0445): chr(0x0425),
            chr(0x0446): chr(0x0426),
            chr(0x0447): chr(0x0427),
            chr(0x0448): chr(0x0428),
            chr(0x0449): chr(0x0429),
            chr(0x044A): chr(0x042A),
            chr(0x044B): chr(0x042B),
            chr(0x044C): chr(0x042C),
            chr(0x044D): chr(0x042D),
            chr(0x044E): chr(0x042E),
            chr(0x044F): chr(0x042F)
        }
        return result

    def parse(self, text: str) -> None:
        """
        Parse the text for the uppercase table.

        :param text: Text to parse
        :return: None
        """
        parts = re.findall(r'\d+', text)
        if not parts:
            # Попалась пустая таблица
            return

        assert len(parts) == 256
        first = bytearray(int(x) for x in parts if x and x.isdigit())
        first = first.replace(b'\x98', b'\x20')  # Этот символ не мапится
        first_chars = list(first.decode(ANSI))
        second = bytearray(x for x in range(256))
        second = second.replace(b'\x98', b'\x20')  # Этот символ не мапится
        second_chars = list(second.decode(ANSI))
        for upper, lower in zip(first_chars, second_chars):
            self.mapping[lower] = upper

    def upper(self, text: str) -> str:
        """
        Convert the text to uppercase according the table.

        :param text: Text to convert
        :return: Converted text
        """
        result = []
        for char in text:
            if char in self.mapping:
                result.append(self.mapping[char])
            else:
                result.append(char)
        return ''.join(result)


def load_uppercase_table(filename: str) -> UpperCaseTable:
    """
    Load the uppercase table from the specified file.

    :param filename: Name of the file
    :return: Uppercase table
    """
    with open(filename, 'rt', encoding=ANSI) as stream:
        text = stream.read()
    result = UpperCaseTable()
    result.parse(text)
    return result


__all__ = ['AlphabetTable', 'load_alphabet_table', 'UpperCaseTable',
           'load_uppercase_table']

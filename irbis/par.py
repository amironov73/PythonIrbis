# coding: utf-8

"""
Работа с PAR-файлами.
"""

from typing import DefaultDict, Iterable
from collections import defaultdict
from ._common import ANSI


class ParFile:
    """
    PAR-файл.
    """

    __slots__ = ('xrf', 'mst', 'cnt', 'n01', 'n02', 'l01', 'l02', 'ifp',
                 'any', 'pft', 'ext')

    def __init__(self, mst: str = '') -> None:
        self.xrf: str = mst
        self.mst: str = mst
        self.cnt: str = mst
        self.n01: str = mst
        self.n02: str = mst
        self.l01: str = mst
        self.l02: str = mst
        self.ifp: str = mst
        self.any: str = mst
        self.pft: str = mst
        self.ext: str = mst

    @staticmethod
    def make_dict(text: Iterable[str]) -> DefaultDict:
        """
        Make the dictionary from the text.

        :param text: Text to parse.
        :return: Dictionary
        """
        result: DefaultDict = defaultdict(lambda: '')
        for line in text:
            if not line:
                continue
            parts = line.split('=', 1)
            if len(parts) < 2:
                continue
            key = parts[0].strip()
            value = parts[1].strip()
            result[key] = value
        return result

    def parse(self, text: Iterable[str]) -> None:
        """
        Parse the text for PAR entries.

        :param text: Text to parse
        :return: None
        """

        paths = ParFile.make_dict(text)
        self.xrf = paths['1']
        self.mst = paths['2']
        self.cnt = paths['3']
        self.n01 = paths['4']
        self.n02 = paths['5']
        self.l01 = paths['6']
        self.l02 = paths['7']
        self.ifp = paths['8']
        self.any = paths['9']
        self.pft = paths['10']
        self.ext = paths['11']

    def save(self, filename: str) -> None:
        """
        Save paths to the specified file.

        :param filename: File to use
        :return: None
        """
        with open(filename, 'wt', encoding=ANSI) as stream:
            stream.write(f'1={self.xrf}\n')
            stream.write(f'2={self.mst}\n')
            stream.write(f'3={self.cnt}\n')
            stream.write(f'4={self.n01}\n')
            stream.write(f'5={self.n02}\n')
            stream.write(f'6={self.l01}\n')
            stream.write(f'7={self.l02}\n')
            stream.write(f'8={self.ifp}\n')
            stream.write(f'9={self.any}\n')
            stream.write(f'10={self.pft}\n')
            stream.write(f'11={self.ext}\n')

    def __str__(self):
        result = ['1=' + self.xrf,
                  '2=' + self.mst,
                  '3=' + self.cnt,
                  '4=' + self.n01,
                  '5=' + self.n02,
                  '6=' + self.l01,
                  '7=' + self.l02,
                  '8=' + self.ifp,
                  '9=' + self.any,
                  '10=' + self.pft,
                  '11=' + self.ext]
        return '\n'.join(result)


def load_par_file(filename: str) -> ParFile:
    """
    Load PAR from the specified file.

    :param filename: File to use
    :return: PAR file
    """

    result = ParFile()
    with open(filename, 'rt', encoding=ANSI) as stream:
        lines = stream.readlines()
        result.parse(lines)
    return result


__all__ = ['load_par_file', 'ParFile']

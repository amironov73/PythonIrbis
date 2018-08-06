# Infrastructure for IRBIS client

from pyirbis import *

###############################################################################

# Меню


class MenuEntry:
    """
    Пара строк в меню.
    """

    __slots__ = 'code', 'comment'

    def __init__(self, code: str = '', comment: str = ''):
        self.code = code
        self.comment = comment

    def __str__(self):
        if self.comment:
            return self.code + ' - ' + self.comment
        return self.code

    def __repr__(self):
        return self.__str__()


class MenuFile:
    """
    Файл меню.
    """

    __slots__ = 'entries'

    def __init__(self):
        self.entries: [MenuEntry] = []

    def add(self, code: str, comment: str = ''):
        entry = MenuEntry(code, comment)
        self.entries.append(entry)
        return self

    def get_entry(self, code: str) -> Optional[MenuEntry]:
        code = code.lower()
        for entry in self.entries:
            if entry.code.lower() == code:
                return entry

        code = code.strip()
        for entry in self.entries:
            if entry.code.lower() == code:
                return entry

        code = MenuFile.trim_code(code)
        for entry in self.entries:
            if entry.code.lower() == code:
                return entry

        return None

    def get_value(self, code: str, default_value: Optional[str]=None) -> Optional[str]:
        entry = self.get_entry(code)
        result = entry and entry.comment or default_value
        return result

    def parse(self, lines: [str]) -> None:
        i = 0
        while i + 1 < len(lines):
            code = lines[i]
            comment = lines[i + 1]
            if code.startswith(STOP_MARKER):
                break
            self.add(code, comment)
            i += 2

    @staticmethod
    def trim_code(code: str) -> str:
        result = code.strip(' -=:')
        return result

    def __str__(self):
        result = []
        for entry in self.entries:
            result.append(entry.code)
            result.append(entry.comment)
        result.append(STOP_MARKER)
        return '\n'.join(result)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        yield from self.entries

    def __getitem__(self, item: str):
        return self.get_value(item)


###############################################################################

# PAR-файл

class ParFile:
    """
    PAR-файл.
    """

    __slots__ = ('xrf', 'mst', 'cnt', 'n01', 'n02', 'l01', 'l02', 'ifp',
                 'any', 'pft', 'ext')

    def __init__(self, mst: str = ''):
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
    def make_dict(text: [str]) -> dict:
        result = dict()
        for line in text:
            if not line:
                continue
            parts = line.split('=', 2)
            if len(parts) < 2:
                continue
            key = parts[0].strip()
            value = parts[1].strip()
            result[key] = value
        return result

    def parse(self, text: [str]) -> None:
        d = ParFile.make_dict(text)
        self.xrf = d['1']
        self.mst = d['2']
        self.cnt = d['3']
        self.n01 = d['4']
        self.n02 = d['5']
        self.l01 = d['6']
        self.l02 = d['7']
        self.ifp = d['8']
        self.any = d['9']
        self.pft = d['10']
        self.ext = d['11']

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


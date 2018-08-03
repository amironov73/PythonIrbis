class PostingParameters:
    """
    Параметры для команды ReadPostings.
    """

    __slots__ = 'database', 'first', 'fmt', 'number', 'terms'

    def __init__(self, term: str = None, fmt: str = None):
        self.database: str = None
        self.first: int = 1
        self.fmt: str = fmt
        self.number: int = 0
        self.terms: [str] = []
        if term:
            self.terms.append(term)

    def __str__(self):
        return str(self.terms)

    def __repr__(self):
        return str(self.terms)


class SearchParameters:
    """
    Параметры поискового запроса.
    """

    __slots__ = ('database', 'first', 'format', 'max_mfn', 'min_mfn',
                 'number', 'expression', 'sequential', 'filter', 'utf')

    def __init__(self, expression: str = ''):
        self.database = ''
        self.first = 1
        self.format = ''
        self.max_mfn = 0
        self.min_mfn = 0
        self.number = 0
        self.expression = expression
        self.sequential = ''
        self.filter = ''
        self.utf = False

    def __str__(self):
        return self.expression


class SearchScenario:
    """
    Сценарий поиска.
    """

    __slots__ = ('name', 'prefix', 'type', 'menu', 'old',
                 'correction', 'truncation', 'hint',
                 'mod_by_dic_auto', 'logic', 'advance',
                 'format')

    def __str__(self):
        return self.name + ' ' + self.prefix


class TermInfo:
    """
    Информация о поисковом терме.
    """

    __slots__ = 'count', 'text'

    def __init__(self, count: int = 0, text: str = ''):
        self.count: int = count
        self.text: str = text

    @staticmethod
    def parse(lines: [str]):
        result = []
        for line in lines:
            parts = line.split('#', 2)
            item = TermInfo(int(parts[0]), parts[1])
            result.append(item)
        return result

    def __str__(self):
        return str(self.count) + '#' + self.text

    def __repr__(self):
        return str(self.count) + '#' + self.text


class TermParameters:
    """
    Параметры для команды ReadTerms
    """

    __slots__ = 'database', 'number', 'reverse', 'start', 'format'

    def __init__(self, start: str = None, number: int = 10):
        self.database: str = ''
        self.number: int = number
        self.reverse: bool = False
        self.start: str = start
        self.format: str = ''

    def __str__(self):
        return str(self.number) + ' ' + self.format


class TermPosting:
    """
    Постинг терма.
    """

    __slots__ = 'mfn', 'tag', 'occurrence', 'count', 'text'

    def __init__(self):
        self.mfn: int = 0
        self.tag: int = 0
        self.occurrence: int = 0
        self.count: int = 0
        self.text: str = None

    def parse(self, text: str) -> None:
        parts = text.split('#', 5)
        if len(parts) < 4:
            return
        self.mfn = int(parts[0])
        self.tag = int(parts[1])
        self.occurrence = int(parts[2])
        self.count = int(parts[3])
        if len(parts) > 4:
            self.text = parts[4]

    def __str__(self):
        return ' '.join([str(self.mfn), str(self.tag),
                         str(self.occurrence), str(self.count),
                         self.text])

    def __repr__(self):
        return self.__str__()

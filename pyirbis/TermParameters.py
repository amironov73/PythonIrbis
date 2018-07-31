class TermParameters:
    """
    Параметры для команды ReadTerms
    """

    __slots__ = "database", "number", "reverse", "start", "format"

    def __init__(self, start: str, number: int = 10):
        self.database: str = ''
        self.number: int = number
        self.reverse: bool = False
        self.start: str = start
        self.format: str = ''

    def __str__(self):
        return str(self.number) + ' ' + self.format


__all__ = [TermParameters]

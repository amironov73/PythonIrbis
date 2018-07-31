from pyirbis.ServerResponse import ServerResponse


class TermInfo:
    """
    Информация о поисковом терме.
    """

    __slots__ = "count", "text"

    def __init__(self, count: int = 0, text: str = ''):
        self.count: int = count
        self.text: str = text

    @staticmethod
    def parse(response: ServerResponse):
        result = []
        while True:
            line = response.utf()
            if not line:
                break
            parts = line.split('#', 2)
            item = TermInfo(int(parts[0]), parts[1])
            result.append(item)
        return result

    def __str__(self):
        return str(self.count) + '#' + self.text

    def __repr__(self):
        return str(self.count) + '#' + self.text


__all__ = [TermInfo]

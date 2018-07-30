class IrbisFormat:
    """
    Манипуляции с форматами.
    """

    ALL = "&uf('+0')"
    BRIEF = '@brief'
    IBIS = '@ibiskw_h'
    INFORMATIONAL = '@info_w'
    OPTIMIZED = '@'

    @staticmethod
    def remove_comments(text: str):
        if '/*' not in text:
            return text

        result = []
        state = ''
        index = 0
        length = len(text)
        while index < length:
            c = text[index]
            if state == "'" or state == '"' or state == '|':
                if c == state:
                    state = ''
                result.append(c)
            else:
                if c == '/':
                    if index + 1 < length and text[index + 1] == '*':
                        while index < length:
                            c = text[index]
                            if c == '\r' or c == '\n':
                                result.append(c)
                                break
                            index = index + 1
                    else:
                        result.append(c)
                else:
                    if c == "'" or c == '"' or c == '|':
                        state = c
                        result.append(c)
                    else:
                        result.append(c)
            index = index + 1

        return ''.join(result)

    @staticmethod
    def prepare(text: str):
        text = IrbisFormat.remove_comments(text)
        length = len(text)
        if length == 0:
            return text

        flag = False
        for c in text:
            if c < ' ':
                flag = True
                break

        if not flag:
            return text

        result = []
        for c in text:
            if c >= ' ':
                result.append(c)

        return ''.join(result)

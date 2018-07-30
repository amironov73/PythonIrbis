from pyirbis.SubField import SubField


class RecordField:
    """
    Поле с тегом, значением (до первого разделителя) и подполями.
    """

    def __init__(self, tag=0, value=''):
        self.tag = tag
        self.value = value
        self.subfields = []

    def add(self, code: str, value: str):
        self.subfields.append(SubField(code, value))
        return self

    def clear(self):
        self.subfields = []
        return self

    def clone(self):
        result = RecordField(self.tag, self.value)
        for sf in self.subfields:
            result.subfields.append(sf.clone())
        return result

    def __str__(self):
        return ''

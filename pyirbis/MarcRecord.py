from pyirbis.RecordField import RecordField


class MarcRecord:
    """
    Запись с MFN, статусом, версией и полями.
    """

    def __init__(self):
        self.database = ''
        self.mfn = 0
        self.version = 0
        self.status = 0
        self.fields = []

    def add(self, tag: int, value=''):
        self.fields.append(RecordField(tag, value))
        return self

    def clear(self):
        self.fields.clear()
        return self

    def clone(self):
        result = MarcRecord()
        result.database = self.database
        result.mfn = self.mfn
        result.status = self.status
        result.version = self.version
        for f in self.fields:
            result.fields.append(f.clone())
        return result

    def __str__(self):
        return ''

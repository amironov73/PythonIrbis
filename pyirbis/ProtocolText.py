from pyirbis import SubField, RecordField, MarcRecord


class ProtocolText:
    """
    Кодирование записи в протокольное представление.
    """

    DELIMITER = '\x1F\x1E'

    def __init__(self):
        self._buffer = []

    def subfield(self, subfield: SubField):
        self._buffer.append('^' + subfield.code + subfield.value)

    def field(self, field: RecordField):
        self._buffer.append(str(field.tag) + '#' + field.value)
        for sf in field.subfields:
            self.subfield(sf)

    def record(self, record: MarcRecord):
        self._buffer.append(str(record.mfn) + '#' + str(record.status) + self.DELIMITER)
        self._buffer.append('0#' + str(record.version) + self.DELIMITER)
        for field in record.fields:
            self.field(field)
            self.DELIMITER

    def __str__(self):
        return ''.join(self._buffer)

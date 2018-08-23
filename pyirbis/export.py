# coding: utf-8

"""
Reading and writing plain text files in IRBIS format.
"""


from typing import Optional
from typing.io import TextIO

from pyirbis.core import STOP_MARKER, RecordField, MarcRecord, safe_str


def read_text_record(stream: TextIO) -> Optional[MarcRecord]:
    """
    Чтение записи из файла в текстовом обменном формате ИРБИС.

    :param stream: Файл
    :return: Запись или None
    """

    result = MarcRecord()
    while True:
        line: str = stream.readline()
        if not line:
            break
        line = line.strip()
        if line.startswith(STOP_MARKER):
            break
        if not line.startswith('#'):
            break
        parts = line[1:].split(':', 1)
        if len(parts) != 2:
            break
        tag = int(parts[0])
        text = parts[1][1:]
        field = RecordField(tag)
        field.parse(text)
        result.fields.append(field)

    if not result.fields:  # Если в записи нет полей, возвращаем None
        return None

    return result


def write_text_record(stream: TextIO, record: MarcRecord) -> None:
    """
    Сохранение записи в файл в текстовом обменном формате ИРБИС.

    :param stream: Файл
    :param record: Запись
    :return: None
    """

    assert stream
    assert record

    for field in record.fields:
        parts = ['#' + str(field.tag) + ': ' + safe_str(field.value)]
        for subfield in field.subfields:
            parts.extend(str(subfield))
        line = ''.join(parts) + '\n'
        stream.write(line)
    stream.write(STOP_MARKER + '\n')


__all__ = ['read_text_record', 'write_text_record']

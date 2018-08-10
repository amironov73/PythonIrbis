# coding: utf-8

from pyirbis.core import *
from typing.io import BinaryIO

# Length of the record marker
MARKER_LENGTH = 24

# Record delimiter
RECORD_DELIMITER = 0x1D

# Field delimiter
FIELD_DELIMITER = 0x1E

# Subfield delimiter
SUBFIELD_DELIMITER = 0x1F


def parse_int(buffer):
    result = 0
    for b in buffer:
        result = result * 10 + b - 48
    return result


def read_record(stream: BinaryIO, charset=ANSI) -> Optional[MarcRecord]:
    """
    Чтение записи из файла в формате ISO 2709.

    :param stream: Файл или файлоподобный объект
    :param charset: Кодировка
    :return: Декодированная запись либо None
    """

    # Считываем длину записи
    marker = stream.read(5)
    if len(marker) != 5:
        return None

    # а затем и ее остаток
    record_length = parse_int(marker)
    need = record_length - 5
    tail = stream.read(need)
    if len(tail) != need:
        return None

    # Простая проверка, что мы имеем дело с нормальной ISO-записью
    record = marker + tail
    if record[record_length - 1] != RECORD_DELIMITER:
        return None

    # Превращаем запись в Unicode
    chars = record.decode(charset)
    indicator_length = parse_int(record[10:11])
    base_address = parse_int(record[12:17])

    # Начинаем собственно конверсию
    result = MarcRecord()

    # Пошли по полям при помощи справочника
    directory = MARKER_LENGTH
    while record[directory] != FIELD_DELIMITER:
        # если нарвались на разделитель, значит, справочник закончился

        tag = parse_int(record[directory:directory + 3])
        field_length = parse_int(record[directory + 3:directory + 7])
        field_offset = parse_int(record[directory + 7:directory + 12]) + base_address
        field = RecordField(tag)
        result.fields.append(field)

        if tag < 10:
            # фиксированное поле
            # не может содержать подполей и индикаторов
            field.value = chars[field_offset:field_offset + field_length - 1]
        else:
            # поле переменной длины
            # содержит два однобайтных индикатора
            # может содержать подполя
            start = field_offset + indicator_length
            stop = field_offset + field_length - indicator_length + 1
            position = start

            # ищем значение поля до первого разделителя
            while position < stop:
                if record[start] == SUBFIELD_DELIMITER:
                    break
                position += 1

            # если есть текст до первого раздлителя, запоминаем его
            if position != start:
                field.value = chars[start:position]

            # просматриваем подполя
            start = position
            while start < stop:
                position = start + 1
                while position < stop:
                    if record[position] == SUBFIELD_DELIMITER:
                        break
                    position += 1
                subfield = SubField(chars[start + 1], chars[start + 2:position])
                field.subfields.append(subfield)
                start = position

        # переходим к следующему полю в справочнике
        directory += 12

    return result

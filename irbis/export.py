# coding: utf-8

"""
Reading and writing plain text files in IRBIS format.
"""

# pylint: disable=too-many-locals
# pylint: disable=too-many-statements


from typing import Iterable, Optional, List

from ._common import ANSI, STOP_MARKER, safe_str
from .error import IrbisError
from .record import SubField, Field, Record


def read_text_record(stream) -> Optional[Record]:
    """
    Чтение записи из файла в текстовом обменном формате ИРБИС.

    :param stream: Файл
    :return: Запись или None
    """

    result = Record()
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
        field = Field(tag)
        field.parse(text)
        result.fields.append(field)

    if not result.fields:  # Если в записи нет полей, возвращаем None
        return None

    return result


def write_text_record(stream, record: Record) -> None:
    """
    Сохранение записи в файл в текстовом обменном формате ИРБИС.

    :param stream: Текстовый поток, в который разрешена запись.
    :param record: Библиографическая запись.
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


###############################################################################

# Length of the record marker
MARKER_LENGTH = 24

# Record delimiter
RECORD_DELIMITER = 0x1D

# Field delimiter
FIELD_DELIMITER = 0x1E

# Subfield delimiter
SUBFIELD_DELIMITER = 0x1F


def parse_int(buffer: Iterable):
    """
    Parse the bytes for integer value.

    :param buffer: Buffer to parse
    :return: Integer value
    """

    result = 0
    for byte in buffer:
        result = result * 10 + byte - 48
    return result


def encode_int(buffer: bytearray, position: int,
               length: int, value: int) -> None:
    """
    Encode the integer value.

    :param buffer: Buffer to fill
    :param position: Start position
    :param length: Chunk length
    :param value: Value to encode
    :return: None
    """

    length -= 1
    position += length
    while length >= 0:
        buffer[position] = value % 10 + ord('0')
        value //= 10
        position -= 1
        length -= 1


def encode_str(buffer: bytearray, position: int,
               value: Optional[str], encoding: str) -> int:
    """
    Encode the string value.

    :param buffer: Buffer to fill
    :param position: Start position
    :param value: Value to encode (can be None or empty string)
    :param encoding: Encoding to use
    :return: Updated position
    """

    if value:
        encoded = value.encode(encoding)
        for byte in encoded:
            buffer[position] = byte
            position += 1

    return position


def read_iso_record(stream, charset: str = ANSI) -> Optional[Record]:
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
    indicator_length = parse_int(record[10:11])
    base_address = parse_int(record[12:17])

    # Начинаем собственно конверсию
    result = Record()

    # Пошли по полям при помощи справочника
    directory = MARKER_LENGTH
    while record[directory] != FIELD_DELIMITER:
        # если нарвались на разделитель, значит, справочник закончился

        tag = parse_int(record[directory:directory + 3])
        field_length = parse_int(record[directory + 3:directory + 7])
        field_offset = parse_int(record[directory + 7:directory + 12]) + \
            base_address
        field = Field(tag)
        result.fields.append(field)

        if tag < 10:
            # фиксированное поле
            # не может содержать подполей и индикаторов
            field.value = record[field_offset:field_offset +
                                 field_length - 1].decode(charset)
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
                field.value = record[start:position].decode(charset)

            # просматриваем подполя
            start = position
            while start < stop:
                position = start + 1
                while position < stop:
                    if record[position] == SUBFIELD_DELIMITER:
                        break
                    position += 1
                subfield = SubField(chr(record[start + 1]),
                                    record[start + 2:position].decode(charset))
                field.subfields.append(subfield)
                start = position

        # переходим к следующему полю в справочнике
        directory += 12

    return result


def write_iso_record(stream, record: Record, encoding: str) -> None:
    """
    Сохранение записи в файл в формате ISO 2709.

    :param stream: Поток
    :param record: Запись
    :param encoding: Кодировка
    :return: None
    """

    record_length = MARKER_LENGTH
    dictionary_length = 1  # С учетом ограничителя справочника
    field_length: List[int] = []

    # Сначала подсчитываем общую длину записи
    for field in record.fields:

        if field.tag <= 0 or field.tag >= 1000:
            # Невозможно закодировать тег поля
            raise Exception

        dictionary_length += 12  # Одна статья справочника
        this_field_length = 0
        if field.tag < 10:
            # В фиксированном поле не бывает подполей и индикаторов
            val = field.value
            if val:
                this_field_length += len(val.encode(encoding))
        else:
            this_field_length += 2  # Индикаторы
            if field.value:
                this_field_length += len(field.value.encode(encoding))
            for subfield in field.subfields:
                code = subfield.code
                if code is None or ord(code) <= 32 or ord(code) >= 255:
                    raise IrbisError('Bad code: ' + safe_str(code))
                this_field_length += 2  # Признак подполя и его код
                val = subfield.value
                if val:
                    this_field_length += len(val.encode(encoding))
        this_field_length += 1  # Разделитель полей

        if this_field_length >= 10_000:
            # Слишком длинное поле
            raise Exception

        field_length.append(this_field_length)
        record_length += this_field_length

    record_length += dictionary_length  # Справочник
    record_length += 1  # Разделитель записей

    if record_length >= 100_000:
        # Слишком длинная запись
        raise Exception

    # Приступаем к кодированию
    dictionary_position = MARKER_LENGTH
    base_address = MARKER_LENGTH + dictionary_length
    current_address = base_address
    buffer = bytearray(record_length)
    for i in range(base_address):
        buffer[i] = 32  # Заполняем пробелами
    encode_int(buffer, 0, 5, record_length)
    encode_int(buffer, 12, 5, base_address)

    buffer[5] = ord('n')  # Record status
    buffer[6] = ord('a')  # Record type
    buffer[7] = ord('m')  # Bibliographical index
    buffer[8] = ord('2')
    buffer[10] = ord('2')
    buffer[11] = ord('2')
    buffer[17] = ord(' ')  # Bibliographical level
    buffer[18] = ord('i')  # Cataloging rules
    buffer[19] = ord(' ')  # Related record
    buffer[20] = ord('4')  # Field length
    buffer[21] = ord('5')  # Field offset
    buffer[22] = ord('0')

    # Кодируем конец справочника
    buffer[base_address - 1] = FIELD_DELIMITER

    # Проходим по полям
    for i, field in enumerate(record.fields):
        # Кодируем справочник
        encode_int(buffer, dictionary_position + 0, 3,
                   field.tag)
        encode_int(buffer, dictionary_position + 3, 4,
                   field_length[i])
        encode_int(buffer, dictionary_position + 7, 5,
                   current_address - base_address)

        # Кодируем поле
        if field.tag < 10:
            # В фиксированном поле не бывает подполей и индикаторов
            encode_str(buffer, current_address, field.value, encoding)
        else:
            # Два индикатора
            buffer[current_address + 0] = 32
            buffer[current_address + 1] = 32
            current_address += 2

            # Значение поля до первого разделителя
            current_address = encode_str(buffer, current_address,
                                         field.value, encoding)

            # Подполя
            for subfield in field.subfields:
                buffer[current_address + 0] = SUBFIELD_DELIMITER
                buffer[current_address + 1] = ord(subfield.code)
                current_address += 2
                current_address = encode_str(buffer, current_address,
                                             subfield.value, encoding)
        buffer[current_address] = FIELD_DELIMITER
        current_address += 1
        dictionary_position += 12

    # Ограничитель записи
    buffer[record_length - 2] = FIELD_DELIMITER
    buffer[record_length - 1] = RECORD_DELIMITER

    # Собственно записываем
    stream.write(buffer)


###############################################################################


__all__ = ['read_text_record', 'read_iso_record', 'STOP_MARKER',
           'write_text_record', 'write_iso_record']

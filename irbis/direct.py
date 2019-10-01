# coding: utf-8

"""
Прямой доступ к базе данных.
"""

from typing import List
from io import SEEK_SET
from ctypes import BigEndianStructure, c_int32, c_uint16, c_uint32
from ._common import change_extension, UTF
from .record import Field, RawRecord, Record


#############################################################################


class XrfRecord(BigEndianStructure):
    """
    Содержит информацию о смещении и статусе записи в мастер-файле.
    """
    _fields_ = [('offset_low', c_uint32),
                ('offset_high', c_uint32),
                ('status', c_int32)]

    def offset(self) -> int:
        """
        Вычисление полного смещения для данной записи.
        :return:
        """
        return self.offset_low + (self.offset_high << 32)

    def __str__(self):
        return f"{self.offset()}: {self.status}"


#############################################################################


class XrfFile:
    """
    Файл перекрестных ссылок.
    """

    __slots__ = ('_stream',)

    def __init__(self, filename: str) -> None:
        self._stream = open(filename, 'rb')

    @staticmethod
    def _get_offset(mfn: int) -> int:
        return (mfn - 1) * 12

    def close(self) -> None:
        """
        Закрывает файл.
        :return: None.
        """
        self._stream.close()

    def read_record(self, mfn: int) -> XrfRecord:
        """
        Чтение одной записи.
        :param mfn:
        :return:
        """
        offset = self._get_offset(mfn)
        self._stream.seek(offset, SEEK_SET)
        result = XrfRecord()
        self._stream.readinto(result)  # type: ignore
        return result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return exc_type is None


#############################################################################

class MstLeader(BigEndianStructure):
    """
    Лидер записи.
    """

    _fields_ = [('mfn', c_uint32),
                ('length', c_uint32),
                ('back_low', c_uint32),
                ('back_high', c_uint32),
                ('base', c_uint32),
                ('nvf', c_uint32),
                ('version', c_uint32),
                ('status', c_uint32)]

    def __str__(self):
        return f"MFN {self.mfn}, version {self.version}, status {self.status}"


#############################################################################


class MstEntry(BigEndianStructure):
    """
    Элемент справочника MST-файла,
    описывающий поле переменной длины.
    """

    _fields_ = [('tag', c_uint32),
                ('position', c_uint32),
                ('length', c_uint32)]

    def __str__(self):
        return f"{self.tag}: {self.position}: {self.length}"


#############################################################################


class MstControl(BigEndianStructure):
    """
    Первая запись в файле документов – управляющая
    запись, которая формируется (в момент определения
    базы данных или при ее инициализации) и поддерживается
    автоматически.
    """

    _fields_ = [('ctl_mfn', c_uint32),
                ('next_mfn', c_uint32),
                ('next_low', c_uint32),
                ('next_high', c_uint32),
                ('mft_type', c_uint32),
                ('rec_cnt', c_uint32),
                ('mfc_xx1', c_uint32),
                ('mfc_xx2', c_uint32),
                ('mfc_xx3', c_uint32)]

    def next_offset(self) -> int:
        """
        Смещение на свободное место.
        :return:
        """
        return self.next_low + (self.next_high << 32)

    def __str__(self):
        return f"{self.next_mfn}: {self.next_offset()}"

#############################################################################


class MstField:
    """
    Поле в мастер-записи.
    """

    __slots__ = 'tag', 'value'

    def __init__(self):
        self.tag: int = 0
        self.value: str = ''

    def __str__(self):
        return f"{self.tag}: {self.value}"


#############################################################################


class MstRecord:
    """
    Запись в мастер-файле.
    """

    __slots__ = 'leader', 'fields'

    def __init__(self):
        self.leader: MstLeader = MstLeader()
        self.fields: List[MstField] = []

    def decode_raw(self) -> RawRecord:
        """
        Декодирование в сырую запись.
        :return:
        """
        result = RawRecord()
        result.mfn = self.leader.mfn
        result.version = self.leader.version
        result.status = self.leader.status
        for field in self.fields:
            line = f"{field.tag}#{field.value}"
            result.fields.append(line)
        return result

    def decode_record(self) -> Record:
        """
        Декодирование в полноценную запись.
        :return:
        """
        result = Record()
        result.mfn = self.leader.mfn
        result.version = self.leader.version
        result.status = self.leader.status
        for source in self.fields:
            target = Field(source.tag)
            target.headless_parse(source.value)
            result.fields.append(target)
        return result

    def dump_fields(self) -> None:
        """
        Дамп полей на консоль.
        :return: None.
        """
        for field in self.fields:
            print(field)
        print('-' * 70)

    def __str__(self):
        return str(self.leader)


#############################################################################


class MstFile:
    """
    Мастер-файл базы данных.
    """

    __slots__ = '_stream', 'control', '_filename'

    def __init__(self, filename: str) -> None:
        """
        Открытие файла.
        :param filename: Имя файла.
        """
        self._filename = filename
        self._stream = open(filename, 'rb')
        self.control = MstControl()
        self._stream.readinto(self.control)  # type: ignore

    def close(self) -> None:
        """
        Закрывает файл.
        :return:
        """
        self._stream.close()

    def next_mfn(self) -> int:
        """
        Получение следующего MFN.
        :return:
        """
        return self.control.next_mfn

    def read_record(self, offset: int) -> MstRecord:
        """
        Чтение записи по указанному смещению.
        :param offset: Смещение.
        :return: Прочитанная запись.
        """
        self._stream.seek(offset, SEEK_SET)
        result = MstRecord()
        self._stream.readinto(result.leader)  # type: ignore
        nvf = result.leader.nvf
        entries: List[MstEntry] = []
        for i in range(nvf):
            entry = MstEntry()
            self._stream.readinto(entry)  # type: ignore
            entries.append(entry)
        base = result.leader.base
        for i in range(nvf):
            field = MstField()
            field.tag = entries[i].tag
            position = entries[i].position
            self._stream.seek(offset + base + position, SEEK_SET)
            field_length = entries[i].length
            raw_value = self._stream.read(field_length)
            field.value = str(raw_value, UTF)
            result.fields.append(field)
        return result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return exc_type is None

    def __str__(self):
        return f"{self._filename}: {self.next_mfn()}"


#############################################################################


class NodeItem(BigEndianStructure):
    """
    Элемент справочника в N01/L01.
    """

    _fields_ = [('length', c_uint16),
                ('key_offset', c_uint16),
                ('offset_low', c_int32),
                ('offset_high', c_int32)]

    def offset(self):
        """
        Полное смещение.
        :return:
        """
        return self.offset_high + (self.offset_low << 32)

    def __str__(self):
        return f"{self.length}: {self.key_offset}"


#############################################################################


class NodeLeader(BigEndianStructure):
    """
    Лидер записи в L01/N01.
    """

    _fields_ = [('number', c_uint32),
                ('previous', c_int32),
                ('next', c_uint32),
                ('term_count', c_int32),
                ('free_offset', c_int32)]

    def __str__(self):
        return f"{self.number}"


#############################################################################


class NodeRecord:
    """
    Файлы N01 и L01 содержат  в себе индексы словаря поисковых
    терминов и состоят из записей (блоков) постоянной длины.
    Записи состоят из трех частей: лидера, справочника
    и ключей переменной длины.
    """

    __slots__ = 'leader', 'items', 'keys'

    def __init__(self):
        self.leader: NodeLeader = NodeLeader()
        self.items: List[NodeItem] = []
        self.keys: List[str] = []

    def __str__(self):
        return str(self.leader)


#############################################################################


class Link(BigEndianStructure):
    """
    Ссылка на запись в мастер-файле.
    """

    _fields_ = [('mfn', c_uint32),
                ('tag', c_int32),
                ('occ', c_int32),
                ('cnt', c_int32)]

    def __str__(self):
        return f"{self.mfn}: {self.tag}: {self.occ}: {self.cnt}"


#############################################################################


class InvertedLeader(BigEndianStructure):
    """
    Заголовок инвертированной записи.
    """

    _fields_ = [('low', c_int32),
                ('high', c_int32),
                ('total', c_int32),
                ('used', c_int32),
                ('count', c_int32)]

    def __str__(self):
        return f"{self.high}: {self.low}"


#############################################################################


class InvertedRecord:
    """
    Запись состоит из заголовка и упорядоченного набора ссылок.
    """

    __slots__ = 'leader', 'links'

    def __init__(self):
        self.leader: InvertedLeader = InvertedLeader()
        self.links: List[Link] = []

    def __str__(self):
        return str(self.leader)


#############################################################################


class InvertedFile:
    """
    Работа с инверсным файлом.
    """

    NODE_LENGTH = 2048

    __slots__ = '_ifp', '_l01', '_n01'

    def __init__(self, filename: str) -> None:
        self._ifp = open(change_extension(filename, '.ifp'), 'rb')
        self._l01 = open(change_extension(filename, '.l01'), 'rb')
        self._n01 = open(change_extension(filename, '.n01'), 'rb')

    def close(self):
        """
        Закрывает файлы.
        :return:
        """
        self._ifp.close()
        self._l01.close()
        self._n01.close()

    @staticmethod
    def _node_offset(number: int) -> int:
        return (number - 1) * InvertedFile.NODE_LENGTH

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return exc_type is None

#############################################################################


class DirectAccess:
    """
    Прямой доступ к базе данных.
    """

    __slots__ = '_xrf', '_mst', '_inverted', '_filename'

    def __init__(self, master_file_name: str) -> None:
        self._filename = master_file_name
        self._mst = MstFile(master_file_name)
        xrf_file_name = change_extension(master_file_name, '.xrf')
        self._xrf = XrfFile(xrf_file_name)
        self._inverted = InvertedFile(master_file_name)

    def close(self) -> None:
        """
        Закрывает файлы.
        :return:
        """
        self._mst.close()
        self._xrf.close()
        self._inverted.close()

    def next_mfn(self) -> int:
        """
        Получает следующий MFN.
        :return:
        """
        return self._mst.next_mfn()

    def read_mst_record(self, mfn: int) -> MstRecord:
        """
        Чтение MST-записи.
        :param mfn: MFN.
        :return: Прочитанная запись.
        """
        xrf_record = self._xrf.read_record(mfn)
        result = self._mst.read_record(xrf_record.offset())
        return result

    def read_raw_record(self, mfn: int) -> RawRecord:
        """
        Чтение RAW-записи.
        :param mfn: MFN.
        :return: Прочитанная запись.
        """
        mst_record = self.read_mst_record(mfn)
        return mst_record.decode_raw()

    def read_record(self, mfn: int) -> Record:
        """
        Чтение полностью декодированной записи.
        :param mfn: MFN.
        :return:
        """
        mst_record = self.read_mst_record(mfn)
        return mst_record.decode_record()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return exc_type is None

    def __str__(self):
        return f"{self._filename}: {self.next_mfn()}"


#############################################################################


__all__ = ['DirectAccess', 'InvertedFile', 'MstControl', 'MstField', 'MstFile',
           'MstEntry', 'MstRecord', 'XrfFile', 'XrfRecord']

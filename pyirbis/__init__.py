# Record status

LOGICALLY_DELETED = 1
PHYSICALLY_DELETED = 2
ABSENT = 4
NON_ACTUALIZED = 8
LAST = 32
LOCKED = 64

# Encodings

ANSI = 'cp1251'
UTF = 'utf-8'
OEM = 'cp866'

# Paths

SYSTEM = 0
DATA = 1
MASTER_FILE = 2
INVERTED_FILE = 3
PARAMETER_FILE = 10
FULL_TEXT = 11
INTERNAL_RESOURCE = 12

# Text delimiters

IRBIS_DELIMITER = '\x1F\x1E'
SHORT_DELIMITER = '\x1E'
MSDOS_DELIMITER = '\r\n'

# Command codes

# Получение признака монопольной блокировки базы данных
EXCLUSIVE_DATABASE_LOCK = '#'

# Получение списка удаленных, неактуализированных
# и заблокированных записей
RECORD_LIST = '0'

# Получение версии сервера
SERVER_INFO = '1'

# Получение статистики по базе данных
DATABASE_STAT = '2'

# Глобальная корректировка
GLOBAL_CORRECTION = '5'

# Сохранение группы записей
SAVE_RECORD_GROUP = '6'

# Печать
PRINT = '7'

# Запись параметров в ini - файл, расположенный на сервере
UPDATE_INI_FILE = '8'

IMPORT_ISO = '9'

# Регистрация клиента на сервере
REGISTER_CLIENT = 'A'

# Разрегистрация клиента
UNREGISTER_CLIENT = 'B'

# Чтение записи, ее расформатирование
READ_RECORD = 'C'

# Сохранение записи
UPDATE_RECORD = 'D'

# Разблокировка записи
UNLOCK_RECORD = 'E'

# Актуализация записи
ACTUALIZE_RECORD = 'F'

# Форматирование записи или группы записей
FORMAT_RECORD = 'G'

# Получение терминов и ссылок словаря,
# форматирование записей
READ_TERMS = 'H'

# Получение ссылок для термина (списка терминов)
READ_POSTINGS = 'I'

# Глобальная корректировка виртуальной записи
CORRECT_VIRTUAL_RECORD = 'J'

# Поиск записей с опциональным форматированием
SEARCH = 'K'

# Получение / сохранение текстового файла,
# расположенного на сервере (группы текстовых файлов)
READ_DOCUMENT = 'L'

BACKUP = 'M'

# Пустая операция. Периодическое подтверждение
# соединения с сервером
NOP = 'N'

# Получение максимального MFN для базы данных
GET_MAX_MFN = 'O'

# Получение терминов и ссылок словаря в обратном порядке
READ_TERMS_REVERSE = 'P'

# Разблокирование записей
UNLOCK_RECORDS = 'Q'

# Полнотекстовый поиск
FULL_TEXT_SEARCH = 'R'

# Опустошение базы данных
EMPTY_DATABASE = 'S'

# Создание базы данных
CREATE_DATABASE = 'T'

# Разблокирование базы данных
UNLOCK_DATABASE = 'U'

# Чтение ссылок для заданного MFN
GET_RECORD_POSTINGS = 'V'

# Удаление базы данных
DELETE_DATABASE = 'W'

# Реорганизация мастер - файла
RELOAD_MASTER_FILE = 'X'

# Реорганизация словаря
RELOAD_DICTIONARY = 'Y'

# Создание поискового словаря заново
CREATE_DICTIONARY = 'Z'

# Получение статистики работы сервера
GET_SERVER_STAT = '+1'

# Получение списка запущенных процессов
GET_PROCESS_LIST = '+3'

# Сохранение списка пользователей
SET_USER_LIST = '+7'

# Перезапуск сервера
RESTART_SERVER = '+8'

# Получение списка пользователей
GET_USER_LIST = '+9'

# Получение списка файлов на сервере
LIST_FILES = '!'

# Запись с полями и подполями


class SubField:
    """
    Подполе с кодом и значением.
    """

    __slots__ = "code", "value"

    def __init__(self, code: str = '\0', value: str = ''):
        self.code: str = code.lower()
        self.value: str = value

    def assign_from(self, other):
        self.code = other.code
        self.value = other.value

    def clone(self):
        return SubField(self.code, self.value)

    def __str__(self):
        return '^' + self.code + self.value

    def __repr__(self):
        return '^' + self.code + self.value


class RecordField:
    """
    Поле с тегом, значением (до первого разделителя) и подполями.
    """

    __slots__ = "tag", "value", "subfields"

    def __init__(self, tag: int = 0, value: str = ''):
        self.tag: int = tag
        self.value: value = value
        self.subfields: [SubField] = []

    def add(self, code: str, value: str = ''):
        self.subfields.append(SubField(code, value))
        return self

    def all(self, code: str) -> [SubField]:
        code = code.lower()
        return [sf for sf in self.subfields if sf.code == code]

    def all_values(self, code: str) -> [str]:
        code = code.lower()
        return [sf.value for sf in self.subfields if sf.code == code]

    def assign_from(self, other):
        self.value = other.value
        self.subfields = [sf.clone() for sf in other.subfields]

    def clear(self):
        self.subfields = []
        return self

    def clone(self):
        result = RecordField(self.tag, self.value)
        for sf in self.subfields:
            result.subfields.append(sf.clone())
        return result

    def first(self, code: str) -> SubField:
        """
        Находит первое подполе с указанным кодом.
        :param code: Код
        :return: Подполе или None
        """
        code = code.lower()
        for subfield in self.subfields:
            if subfield.code == code:
                return subfield
        return None

    def first_value(self, code: str) -> str:
        """
        Находит первое подполе с указанным кодом.
        :param code: Код
        :return: Значение подполя или None
        """
        code = code.lower()
        for subfield in self.subfields:
            if subfield.code == code:
                return subfield.value
        return None

    def parse(self, line: str) -> None:
        parts = line.split('#', 2)
        self.tag = int(parts[0])
        if '^' not in parts[1]:
            self.value = parts[1]
        else:
            if parts[1][0] != '^':
                parts = parts[1].split('^', 2)
                self.value = parts[0]
                parts = parts[1].split('^')
            else:
                parts = parts[1].split('^')
            for x in parts:
                sub = SubField(x[:1], x[1:])
                self.subfields.append(sub)

    def to_text(self) -> str:
        buffer = [str(self.tag), '#', self.value] + [str(sf) for sf in self.subfields]
        return ''.join(buffer)

    def __str__(self):
        return self.to_text()

    def __repr__(self):
        return self.to_text()


class MarcRecord:
    """
    Запись с MFN, статусом, версией и полями.
    """

    __slots__ = "database", "mfn", "version", "status", "fields"

    def __init__(self):
        self.database: str = ''
        self.mfn: int = 0
        self.version: int = 0
        self.status: int = 0
        self.fields: [RecordField] = []

    def add(self, tag: int, value='', *subfields: SubField):
        field = RecordField(tag, value)
        field.subfields.extend(subfields)
        self.fields.append(field)
        return self

    def all(self, tag: int) -> [RecordField]:
        return [f for f in self.fields if f.tag == tag]

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

    def fm(self, tag: int, code: str = '') -> str:
        """
        Текст первого поля с указанным тегом.
        :param tag: Тег
        :param code: Значение (опционально)
        :return: Текст или None
        """
        for field in self.fields:
            if field.tag == tag:
                if code:
                    return field.first_value(code)
                else:
                    return field.value
        return None

    def fma(self, tag: int, code: str = '') -> [str]:
        result = []
        for field in self.fields:
            if field.tag == tag:
                if code:
                    one = field.first_value(code)
                    if one:
                        result.append(one)
                else:
                    one = field.value
                    if one:
                        result.append(one)
        return result

    def first(self, tag: int) -> RecordField:
        for field in self.fields:
            if field.tag == tag:
                return field
        return None

    def is_deleted(self) -> bool:
        return (self.status & (LOGICALLY_DELETED | PHYSICALLY_DELETED)) != 0

    def parse(self, text: [str]) -> None:
        if not text:
            return
        line = text[0]
        parts = line.split('#')
        self.mfn = int(parts[0])
        if len(parts) != 1 and parts[1]:
            self.status = int(parts[1])
        line = text[1]
        parts = line.split('#')
        self.version = int(parts[1])
        self.fields.clear()
        for line in text[2:]:
            field = RecordField()
            field.parse(line)
            self.fields.append(field)

    def to_text(self) -> str:
        result=[str(field) for field in self.fields]
        return '\n'.join(result)

    def __str__(self):
        return self.to_text()

    def __repr__(self):
        return self.to_text()

import random
from typing import Tuple, Union

from pyirbis.infrastructure import *
from pyirbis.search import *


###############################################################################

# Запись с полями и подполями


class SubField:
    """
    Подполе с кодом и значением.
    """

    __slots__ = 'code', 'value'

    def __init__(self, code: str = '\0', value: str = None):
        self.code: str = code.lower()
        self.value: str = value

    def assign_from(self, other):
        self.code = other.code
        self.value = other.value

    def clone(self):
        return SubField(self.code, self.value)

    def __str__(self):
        return '^' + self.code + (self.value or '')

    def __repr__(self):
        return self.__str__()


class RecordField:
    """
    Поле с тегом, значением (до первого разделителя) и подполями.
    """

    __slots__ = 'tag', 'value', 'subfields'

    def __init__(self, tag: int = 0, value: str = None):
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

    def first(self, code: str) -> Optional[SubField]:
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

    def first_value(self, code: str) -> Optional[str]:
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
                if x:
                    sub = SubField(x[:1], x[1:])
                    self.subfields.append(sub)

    def to_text(self) -> str:
        buffer = [str(self.tag), '#', self.value or ''] + [str(sf) for sf in self.subfields]
        return ''.join(buffer)

    def __str__(self):
        return self.to_text()

    def __repr__(self):
        return self.to_text()


class MarcRecord:
    """
    Запись с MFN, статусом, версией и полями.
    """

    __slots__ = 'database', 'mfn', 'version', 'status', 'fields'

    def __init__(self):
        self.database: str = None
        self.mfn: int = 0
        self.version: int = 0
        self.status: int = 0
        self.fields: [RecordField] = []

    def add(self, tag: int, value: Union[str, SubField] = None,
            *subfields: SubField):
        if isinstance(value, str):
            field = RecordField(tag, value)
        else:
            field = RecordField(tag)
            if isinstance(value, SubField):
                field.subfields.append(value)
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

    def encode(self) -> [str]:
        result = [str(self.mfn) + '#' + str(self.status),
                  '0#' + str(self.version)]
        for field in self.fields:
            result.append(str(field))
        return result

    def fm(self, tag: int, code: str = '') -> Optional[str]:
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

    def first(self, tag: int) -> Optional[RecordField]:
        for field in self.fields:
            if field.tag == tag:
                return field
        return None

    def is_deleted(self) -> bool:
        """
        Удалена ли запись?
        :return: True для удаленной записи
        """
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
        result = [str(field) for field in self.fields]
        return '\n'.join(result)

    def __str__(self):
        return self.to_text()

    def __repr__(self):
        return self.to_text()

    def __iter__(self):
        yield from self.fieldsi

    def __getitem__(self, item: int):
        return self.fm(item)

###############################################################################

# Подключение к серверу


class IrbisConnection:

    def __init__(self):
        self.host = 'localhost'
        self.port = 6666
        self.username = ''
        self.password = ''
        self.database = 'IBIS'
        self.workstation = 'C'
        self.clientId = 0
        self.queryId = 0
        self.connected = False
        self._stack = []

    def actualize_record(self, mfn: int, database: Optional[str] = None) -> None:
        """
        Актуализация записи с указанным MFN.

        :param mfn: MFN записи
        :param database: База данных
        :return: None
        """
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, ACTUALIZE_RECORD)
        query.ansi(database).add(mfn)
        with self.execute(query) as response:
            response.check_return_code()

    def connect(self):
        """
        Подключение к серверу ИРБИС64.

        :return: INI-файл
        """
        if self.connected:
            return

        self.queryId = 0
        self.clientId = random.randint(100000, 900000)
        query = ClientQuery(self, REGISTER_CLIENT)
        query.ansi(self.username)
        query.ansi(self.password)
        with self.execute(query) as response:
            response.check_return_code()
        self.connected = True
        return ''

    def create_database(self, database: Optional[str] = None,
                        description: Optional[str] = None,
                        reader_access: bool = True) -> None:
        """
        Создание базы данных.

        :param database: Имя создаваемой базы
        :param description: Описание в свободной форме
        :param reader_access: Читатель будет иметь доступ?
        :return: None
        """
        database = database or self.database or throw_value_error()
        description = description or ''
        query = ClientQuery(self, CREATE_DATABASE)
        query.ansi(database).ansi(description).add(int(reader_access))
        with self.execute(query) as response:
            response.check_return_code()

    def create_dictionary(self, database: Optional[str] = None) -> None:
        """
        Создание словаря в базе данных.

        :param database: База данных
        :return: None
        """
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, CREATE_DICTIONARY)
        query.ansi(database)
        with self.execute(query) as response:
            response.check_return_code()

    def delete_database(self, database: Optional[str] = None) -> None:
        """
        Удаление базы данных.

        :param database: Имя удаляемой базы
        :return: None
        """
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, DELETE_DATABASE)
        query.ansi(database)
        with self.execute(query) as response:
            response.check_return_code()

    def delete_record(self, mfn: int) -> None:
        """
        Удаление записи по ее MFN.

        :param mfn: MFN удаляемой записи
        :return: None
        """
        record = self.read_record(mfn)
        if not record.is_deleted():
            record.status |= LOGICALLY_DELETED
            self.write_record(record, dont_parse=True)

    def disconnect(self) -> None:
        """
        Отключение от сервера.

        :return: None
        """
        if not self.connected:
            return
        query = ClientQuery(self, UNREGISTER_CLIENT)
        query.ansi(self.username)
        self.execute_forget(query)
        self.connected = False

    def execute(self, query: ClientQuery) -> ServerResponse:
        """
        Выполнение произвольного запроса к серверу.

        :param query: Запрос
        :return: Ответ сервера (не забыть закрыть!)
        """
        sock = socket.socket()
        sock.connect((self.host, self.port))
        packet = query.encode()
        sock.send(packet)
        return ServerResponse(sock)

    def execute_ansi(self, commands: []) -> ServerResponse:
        """
        Простой запрос к серверу, когда все строки запроса
        в кодировке ANSI.

        :param commands: Команда и параметры запроса
        :return: Ответ сервера (не забыть закрыть!)
        """
        query = ClientQuery(self, commands[0])
        for x in commands[1:]:
            query.ansi(x)
        return self.execute(query)

    def execute_forget(self, query: ClientQuery) -> None:
        """
        Выполнение запроса к серверу, когда нам не важен результат
        (мы не собираемся его парсить).

        :param query: Клиентский запрос
        :return: None
        """
        with self.execute(query):
            pass

    def format_record(self, script: str, mfn: int) -> str:
        """
        Форматирование записи с указанным MFN.

        :param script: Текст формата
        :param mfn: MFN записи
        :return: Результат расформатирования
        """
        script = script or throw_value_error()
        mfn = mfn or throw_value_error()
        query = ClientQuery(self, FORMAT_RECORD)
        query.ansi(self.database).ansi(script).add(1).add(mfn)
        with self.execute(query) as response:
            response.check_return_code()
            result = response.utf_remaining_text()
            return result

    def get_database_info(self, database: Optional[str] = None) -> DatabaseInfo:
        """
        Получение информации о базе данных.

        :param database: Имя базы
        :return: Информация о базе
        """
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, RECORD_LIST).ansi(database)
        with self.execute(query) as response:
            response.check_return_code()
            result = DatabaseInfo()
            result.parse(response)
            result.name = database
            return result

    def get_max_mfn(self, database: Optional[str] = None) -> int:
        """
        Получение максимального MFN для указанной базы данных.

        :param database: База данных
        :return: MFN, который будет присвоен следующей записи
        """
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, GET_MAX_MFN)
        query.ansi(database)
        with self.execute(query) as response:
            response.check_return_code()
            result = response.return_code
            return result

    def get_server_stat(self) -> ServerStat:
        """
        Получение статистики с сервера.

        :return: Полученная статистика
        """
        query = ClientQuery(self, GET_SERVER_STAT)
        with self.execute(query) as response:
            response.check_return_code()
            result = ServerStat()
            result.parse(response)
            return result

    def get_server_version(self) -> IrbisVersion:
        """
        Получение версии сервера.

        :return: Версия сервера
        """
        query = ClientQuery(self, SERVER_INFO)
        with self.execute(query) as response:
            response.check_return_code()
            lines = response.ansi_remaining_lines()
            result = IrbisVersion()
            result.parse(lines)
            return result

    def get_user_list(self) -> [UserInfo]:
        """
        Получение списка пользователей с сервера.

        :return: Список пользователей
        """
        query = ClientQuery(self, GET_USER_LIST)
        with self.execute(query) as response:
            response.check_return_code()
            result = UserInfo.parse(response)
            return result

    def list_files(self, specification: Union[FileSpecification, str]) -> [str]:
        """
        Получение списка файлов с сервера.

        :param specification: Спецификация или маска имени файла (если нужны файлы, лежащие в папке текущей базы данных)
        :return: Список файлов
        """
        if isinstance(specification, str):
            specification = FileSpecification(MASTER_FILE, self.database, specification)

        query = ClientQuery(self, LIST_FILES)
        query.ansi(str(specification))
        result = []
        with self.execute(query) as response:
            lines = response.ansi_remaining_lines()
            result.extend(lines)
        return result

    def list_processes(self) -> [ServerProcess]:
        """
        Получение списка серверных процессов.

        :return: Список процессов
        """
        query = ClientQuery(self, GET_PROCESS_LIST)
        with self.execute(query) as response:
            response.check_return_code()
            result = ServerProcess.parse(response)
            return result

    def nop(self) -> None:
        """
        Пустая операция (используется для периодического
        подтверждения подключения клиента).

        :return: None
        """
        with self.execute_ansi([NOP]):
            pass

    def parse_connection_string(self, text: str) -> None:
        """
        Разбор строки подключения.

        :param text: Строка подключения
        :return: None
        """
        for item in text.split(';'):
            if not item:
                continue
            parts = item.split('=', 2)
            name = parts[0].strip().lower()
            value = parts[1].strip()

            if name in ['host', 'server', 'address']:
                self.host = value

            if name == 'port':
                self.port = int(value)

            if name in ['user', 'username', 'name', 'login']:
                self.username = value

            if name in ['pwd', 'password']:
                self.password = value

            if name in ['db', 'database', 'catalog']:
                self.database = value

            if name in ['arm', 'workstation']:
                self.workstation = value

    def pop_database(self) -> str:
        """
        Восстановление подключения к прошлой базе данных,
        запомненной с помощью push_database.

        :return: Прошлая база данных
        """
        result = self.database
        self.database = self._stack.pop()
        return result

    def print_table(self, definition: TableDefinition) -> str:
        """
        Расформатирование таблицы.

        :param definition: Определение таблицы
        :return: Результат расформатирования
        """
        database = definition.database or self.database or throw_value_error()
        query = ClientQuery(self, PRINT)
        query.ansi(database).ansi(definition.table)
        query.ansi('')  # instead of the headers
        query.ansi(definition.mode).utf(definition.search)
        query.add(definition.min_mfn).add(definition.max_mfn)
        query.utf(definition.sequential)
        query.ansi('')  # instead of the MFN list
        with self.execute(query) as response:
            result = response.utf_remaining_text()
            return result

    def push_database(self, database: str) -> str:
        """
        Установка подключения к новой базе данных,
        с запоминанием предыдущей базы.

        :param database: Новая база данных
        :return: Предыдущая база данных
        """
        result = self.database
        self._stack.append(result)
        self.database = database
        return result

    def read_alphabet_table(self, specification: Optional[FileSpecification] = None) -> AlphabetTable:
        if specification is None:
            specification = FileSpecification(SYSTEM, None, AlphabetTable.FILENAME)

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        with self.execute(query) as response:
            result = AlphabetTable()
            result.parse(response)
            if not result.characters:
                result = AlphabetTable.get_default()
            return result

    def read_binary_file(self, specification: FileSpecification):
        """
        Чтение двоичного файла с сервера.

        :param specification: спецификация файла
        :return: Полученный файл или None, если файл не найден
        """
        pass

    def read_ini(self, specification: Union[FileSpecification, str]) -> IniFile:
        if isinstance(specification, str):
            specification = FileSpecification(MASTER_FILE, self.database, specification)

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        with self.execute(query) as response:
            result = IniFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            result.parse(text)
            return result

    def read_menu(self, specification: Union[FileSpecification, str]) -> MenuFile:
        if isinstance(specification, str):
            specification = FileSpecification(MASTER_FILE, self.database, specification)

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        with self.execute(query) as response:
            result = MenuFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            result.parse(text)
            return result

    def read_opt(self, specification: Union[FileSpecification, str]) -> OptFile:
        if isinstance(specification, str):
            specification = FileSpecification(MASTER_FILE, self.database, specification)

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        with self.execute(query) as response:
            result = OptFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            result.parse(text)
            return result

    def read_par(self, specification: Union[FileSpecification, str]) -> ParFile:
        """
        Получение PAR-файла с сервера.

        :param specification: Спецификация или имя файла (если он лежит в папке DATA)
        :return: Полученный файл
        """
        if isinstance(specification, str):
            specification = FileSpecification(DATA, None, specification)

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        with self.execute(query) as response:
            result = ParFile()
            text = irbis_to_lines(response.ansi_remaining_text())
            result.parse(text)
            return result

    def read_postings(self, parameters: Union[PostingParameters, str],
                      fmt: Optional[str] = None) -> [TermPosting]:
        """
        Считывание постингов для указанных термов из поискового словаря.

        :param parameters: Параметры постингов или терм
        :param fmt: Опциональный формат
        :return: Список постингов
        """

        if isinstance(parameters, str):
            parameters = PostingParameters(parameters)
            parameters.fmt = fmt

        database = parameters.database or self.database or throw_value_error()
        query = ClientQuery(self, READ_POSTINGS)
        query.ansi(database).add(parameters.number)
        query.add(parameters.first).ansi(parameters.fmt)
        for term in parameters.terms:
                query.utf(term)
        with self.execute(query) as response:
            response.check_return_code(READ_TERMS_CODES)
            result = []
            while True:
                line = response.utf()
                if not line:
                    break
                posting = TermPosting()
                posting.parse(line)
                result.append(posting)
            return result

    def read_record(self, mfn: int, version: int = 0) -> MarcRecord:
        """
        Чтение записи с указанным MFN с сервера.

        :param mfn: MFN
        :param version: версия
        :return: Прочитанная запись
        """
        mfn = mfn or throw_value_error()
        query = ClientQuery(self, READ_RECORD)
        query.ansi(self.database).add(mfn)
        if version:
            query.add(version)
        result = MarcRecord()
        with self.execute(query) as response:
            response.check_return_code(READ_RECORD_CODES)
            text = response.utf_remaining_lines()
            result.database = self.database
            result.parse(text)
        if version:
            self.unlock_records([mfn])
        return result

    def read_terms(self, parameters: Union[TermParameters, str, Tuple[str, int]]) -> []:
        """
        Получение термов поискового словаря.

        :param parameters: Параметры термов или терм или кортеж "терм, количество"
        :return: Список термов
        """
        if isinstance(parameters, tuple):
            parameters2 = TermParameters(parameters[0])
            parameters2.number = parameters[1]
            parameters = parameters

        if isinstance(parameters, str):
            parameters = TermParameters(parameters)
            parameters.number = 10

        database = parameters.database or self.database or throw_value_error()
        command = READ_TERMS_REVERSE if parameters.reverse else READ_TERMS
        query = ClientQuery(self, command)
        query.ansi(database).utf(parameters.start)
        query.add(parameters.number).ansi(parameters.format)
        with self.execute(query) as response:
            response.check_return_code(READ_TERMS_CODES)
            lines = response.utf_remaining_lines()
            result = TermInfo.parse(lines)
            return result

    def read_text_file(self, specification: Union[FileSpecification, str]) -> str:
        """
        Получение текстового файла с сервера в виде потока.

        :param specification: Спецификация или имя файла (если он находится в папке текущей базы данных).
        :return: Текст файла или пустая строка, если файл не найден
        """
        if isinstance(specification, str):
            specification = FileSpecification(MASTER_FILE, self.database, specification)

        query = ClientQuery(self, READ_DOCUMENT)
        query.ansi(str(specification))
        with self.execute(query) as response:
            result = response.ansi_remaining_text()
            return result

    def read_tree_file(self, specification: Union[FileSpecification, str]) -> TreeFile:
        if isinstance(specification, str):
            specification = FileSpecification(MASTER_FILE, self.database, specification)

        query = ClientQuery(self, READ_DOCUMENT)
        query.ansi(str(specification))
        with self.execute(query) as response:
            text = response.ansi_remaining_text()
            text = [line for line in irbis_to_lines(text) if line]
            result = TreeFile()
            result.parse(text)
            return result

    def read_uppercase_table(self, specification: Optional[FileSpecification] = None) -> UpperCaseTable:
        if specification is None:
            specification = FileSpecification(SYSTEM, None, UpperCaseTable.FILENAME)

        query = ClientQuery(self, READ_DOCUMENT).ansi(str(specification))
        with self.execute(query) as response:
            result = UpperCaseTable()
            result.parse(response)
            if not result.mapping:
                result = UpperCaseTable.get_default()
            return result

    def reload_dictionary(self, database: str = '') -> None:
        """
        Пересоздание словаря.

        :param database: База данных
        :return: None
        """
        database = database or self.database or throw_value_error()
        with self.execute_ansi([RELOAD_DICTIONARY, database]):
            pass

    def reload_master_file(self, database: str = '') -> None:
        """
        Пересоздание мастер-файла.

        :param database: База данных
        :return: None
        """
        database = database or self.database or throw_value_error()
        with self.execute_ansi([RELOAD_MASTER_FILE, database]):
            pass

    def restart_server(self) -> None:
        """
        Перезапуск сервера (без утери подключенных клиентов).

        :return: None
        """
        with self.execute_ansi([RESTART_SERVER]):
            pass

    def search(self, parameters: Union[SearchParameters, str]) -> []:
        """
        Поиск записей.

        :param parameters: Параметры поиска (либо поисковый запрос)
        :return: Список найденных MFN
        """
        if isinstance(parameters, str):
            parameters = SearchParameters(parameters)

        database = parameters.database or self.database or throw_value_error()
        query = ClientQuery(self, SEARCH)
        query.ansi(database)
        query.utf(parameters.expression)
        query.add(parameters.number)
        query.add(parameters.first)
        query.ansi(parameters.format)
        query.add(parameters.min_mfn)
        query.add(parameters.max_mfn)
        query.ansi(parameters.sequential)
        response = self.execute(query)
        response.check_return_code()
        expected = response.number()
        result = []
        for i in range(expected):
            line = response.ansi()
            mfn = int(line)
            result.append(mfn)
        return result

    def to_connection_string(self) -> str:
        """
        Выдача строки подключения для текущего соединения.

        :return: Строка подключения
        """
        return 'host=' + self.host + ';port=' + str(self.port) \
               + ';username=' + self.username + ';password=' \
               + self.password + ';database=' + self.database \
               + ';workstation=' + self.workstation + ';'

    def truncate_database(self, database: str = '') -> None:
        """
        Опустошение базы данных.

        :param database: База данных
        :return: None
        """
        database = database or self.database or throw_value_error()
        with self.execute_ansi([EMPTY_DATABASE, database]):
            pass

    def unlock_database(self, database: Optional[str] = None) -> None:
        """
        Разблокирование базы данных.

        :param database: Имя базы
        :return: None
        """
        database = database or self.database or throw_value_error()
        with self.execute_ansi([UNLOCK_DATABASE, database]):
            pass

    def unlock_records(self, records: [int], database: Optional[str] = None) -> None:
        """
        Разблокирование записей.

        :param records: Список MFN
        :param database: База данных
        :return: None
        """
        database = database or self.database or throw_value_error()
        query = ClientQuery(self, UNLOCK_RECORDS)
        query.ansi(database)
        for mfn in records:
            query.add(mfn)
        with self.execute(query) as response:
            response.check_return_code()

    def update_ini_file(self, lines: [str]) -> None:
        """
        Обновление строк серверного INI-файла.

        :param lines: Измененные строки
        :return: None
        """
        if not lines:
            return
        query = ClientQuery(self, UPDATE_INI_FILE)
        for line in lines:
            query.ansi(line)
        self.execute_forget(query)

    def update_user_list(self, user_list) -> None:
        """
        Обновление списка пользователей на сервере.

        :param user_list: Список пользователей
        :return: None
        """
        pass

    def write_record(self, record: MarcRecord, lock: bool = False,
                     actualize: bool = True,
                     dont_parse: bool = False) -> int:
        """
        Сохранение записи на сервере.

        :param record: Запись
        :param lock: Оставить запись заблокированной?
        :param actualize: Актуализировать запись?
        :param dont_parse: Не разбирать ответ сервера?
        :return: Новый максимальный MFN
        """
        database = record.database or self.database or throw_value_error()
        query = ClientQuery(self, UPDATE_RECORD)
        query.ansi(database).add(int(lock)).add(int(actualize))
        query.utf(IRBIS_DELIMITER.join(record.encode()))
        with self.execute(query) as response:
            response.check_return_code()
            result = response.return_code  # Новый максимальный MFN
            if not dont_parse:
                first_line = response.utf()
                text = short_irbis_to_lines(response.utf())
                text.insert(0, first_line)
                record.database = database
                record.parse(text)
        return result

    def write_text_file(self, specification: FileSpecification) -> None:
        """
        Сохранение текстового файла на сервере.

        :param specification: Спецификация (включая текст для сохранения)
        :return: None
        """
        query = ClientQuery(self, READ_DOCUMENT)
        query.ansi(str(specification))
        with self.execute(query) as response:
            response.check_return_code()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return exc_type is None


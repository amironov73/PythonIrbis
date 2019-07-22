# coding: utf-8

"""
Infrastructure related extended functionality for IRBIS64 client
"""

import re
from typing import List, Tuple, Dict, Iterable, Optional, Union

from irbis.core import Connection, FileSpecification, ClientQuery, ServerResponse, IniFile, \
    safe_str, safe_int, irbis_to_lines, throw_value_error, same_string, \
    ANSI, STOP_MARKER, SYSTEM, DATA, SHORT_DELIMITER, \
    READ_TERMS, READ_TERMS_REVERSE, READ_TERMS_CODES, READ_POSTINGS, GET_USER_LIST, SET_USER_LIST, \
    GET_SERVER_STAT, RECORD_LIST, PRINT, \
    IrbisError


###############################################################################


class MenuEntry:
    """
    Пара строк в меню.
    """

    __slots__ = 'code', 'comment'

    def __init__(self, code: str = '', comment: str = '') -> None:
        self.code: str = code
        self.comment: str = comment

    def __str__(self):
        if self.comment:
            return self.code + ' - ' + self.comment
        return self.code

    def __repr__(self):
        return self.__str__()


class MenuFile:
    """
    Файл меню.
    """

    __slots__ = ('entries',)

    def __init__(self) -> None:
        self.entries: List[MenuEntry] = []

    def add(self, code: str, comment: str = ''):
        """
        Add an entry to the menu.

        :param code: Code
        :param comment: Comment
        :return: Self
        """
        entry = MenuEntry(code, comment)
        self.entries.append(entry)
        return self

    def get_entry(self, code: str) -> Optional[MenuEntry]:
        """
        Get an entry for the specified code.

        :param code: Code to search
        :return: Found entry or None
        """

        code = code.lower()
        for entry in self.entries:
            if entry.code.lower() == code:
                return entry

        code = code.strip()
        for entry in self.entries:
            if entry.code.lower() == code:
                return entry

        code = MenuFile.trim_code(code)
        for entry in self.entries:
            if entry.code.lower() == code:
                return entry

        return None

    def get_value(self, code: str,
                  default_value: Optional[str] = None) -> Optional[str]:
        """
        Get value for the specified code.

        :param code: Code to search
        :param default_value: Default value
        :return: Found or default value
        """

        entry = self.get_entry(code)
        result = entry.comment if entry else default_value
        return result

    def parse(self, lines: List[str]) -> None:
        """
        Parse the text for menu entries.

        :param lines: Text to parse
        :return: None
        """

        i = 0
        while i + 1 < len(lines):
            code = lines[i]
            comment = lines[i + 1]
            if code.startswith(STOP_MARKER):
                break
            self.add(code, comment)
            i += 2

    def save(self, filename: str) -> None:
        """
        Save the menu to the specified file.

        :param filename: Name of the file
        :return: None
        """

        with open(filename, 'wt', encoding=ANSI) as stream:
            for entry in self.entries:
                stream.write(entry.code + '\n')
                stream.write(entry.comment + '\n')
            stream.write(STOP_MARKER + '\n')

    @staticmethod
    def trim_code(code: str) -> str:
        """
        Trim the code.

        :param code: code to process
        :return: Trimmed code
        """

        result = code.strip(' -=:')
        return result

    def __str__(self):
        result = []
        for entry in self.entries:
            result.append(entry.code)
            result.append(entry.comment)
        result.append(STOP_MARKER)
        return '\n'.join(result)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        yield from self.entries

    def __getitem__(self, item: str):
        return self.get_value(item)


def load_menu(filename: str) -> MenuFile:
    """
    Чтение меню из файла.

    :param filename: Имя файла
    :return: Меню
    """
    with open(filename, 'rt', encoding=ANSI) as stream:
        result = MenuFile()
        lines = stream.readlines()
        result.parse(lines)
        return result


def read_menu(connection: Connection,
              specification: Union[FileSpecification, str]) -> MenuFile:
    """
    Чтение меню с сервера.

    :param connection: Подключение
    :param specification: Спецификация файла
    :return: Меню
    """
    assert connection and isinstance(connection, Connection)

    with connection.read_text_stream(specification) as response:
        result = MenuFile()
        text = irbis_to_lines(response.ansi_remaining_text())
        result.parse(text)
        return result


Connection.read_menu = read_menu  # type: ignore


###############################################################################


class ParFile:
    """
    PAR-файл.
    """

    __slots__ = ('xrf', 'mst', 'cnt', 'n01', 'n02', 'l01', 'l02', 'ifp',
                 'any', 'pft', 'ext')

    def __init__(self, mst: str = '') -> None:
        self.xrf: str = mst
        self.mst: str = mst
        self.cnt: str = mst
        self.n01: str = mst
        self.n02: str = mst
        self.l01: str = mst
        self.l02: str = mst
        self.ifp: str = mst
        self.any: str = mst
        self.pft: str = mst
        self.ext: str = mst

    @staticmethod
    def make_dict(text: Iterable[str]) -> Dict:
        """
        Make the dictionary from the text.

        :param text: Text to parse.
        :return: Dictionary
        """

        import collections
        result: Dict = collections.defaultdict(lambda: '')
        for line in text:
            if not line:
                continue
            parts = line.split('=', 1)
            if len(parts) < 2:
                continue
            key = parts[0].strip()
            value = parts[1].strip()
            result[key] = value
        return result

    def parse(self, text: Iterable[str]) -> None:
        """
        Parse the text for PAR entries.

        :param text: Text to parse
        :return: None
        """

        paths = ParFile.make_dict(text)
        self.xrf = paths['1']
        self.mst = paths['2']
        self.cnt = paths['3']
        self.n01 = paths['4']
        self.n02 = paths['5']
        self.l01 = paths['6']
        self.l02 = paths['7']
        self.ifp = paths['8']
        self.any = paths['9']
        self.pft = paths['10']
        self.ext = paths['11']

    def save(self, filename: str) -> None:
        """
        Save paths to the specified file.

        :param filename: File to use
        :return: None
        """
        with open(filename, 'wt', encoding=ANSI) as stream:
            stream.write(f'1={self.xrf}\n')
            stream.write(f'2={self.mst}\n')
            stream.write(f'3={self.cnt}\n')
            stream.write(f'4={self.n01}\n')
            stream.write(f'5={self.n02}\n')
            stream.write(f'6={self.l01}\n')
            stream.write(f'7={self.l02}\n')
            stream.write(f'8={self.ifp}\n')
            stream.write(f'9={self.any}\n')
            stream.write(f'10={self.pft}\n')
            stream.write(f'11={self.ext}\n')

    def __str__(self):
        result = ['1=' + self.xrf,
                  '2=' + self.mst,
                  '3=' + self.cnt,
                  '4=' + self.n01,
                  '5=' + self.n02,
                  '6=' + self.l01,
                  '7=' + self.l02,
                  '8=' + self.ifp,
                  '9=' + self.any,
                  '10=' + self.pft,
                  '11=' + self.ext]
        return '\n'.join(result)


def load_par_file(filename: str) -> ParFile:
    """
    Load PAR from the specified file.

    :param filename: File to use
    :return: PAR file
    """

    result = ParFile()
    with open(filename, 'rt', encoding=ANSI) as stream:
        lines = stream.readlines()
        result.parse(lines)
    return result


def read_par_file(connection: Connection,
                  specification: Union[FileSpecification, str]) -> ParFile:
    """
    Получение PAR-файла с сервера.

    :param connection: Подключение
    :param specification: Спецификация или имя файла (если он лежит в папке DATA)
    :return: Полученный файл
    """
    assert connection and isinstance(connection, Connection)

    if isinstance(specification, str):
        specification = FileSpecification(DATA, None, specification)

    with connection.read_text_stream(specification) as response:
        result = ParFile()
        text = irbis_to_lines(response.ansi_remaining_text())
        result.parse(text)
        return result


Connection.read_par_file = read_par_file  # type: ignore


###############################################################################


class TermPosting:
    """
    Постинг терма.
    """

    __slots__ = 'mfn', 'tag', 'occurrence', 'count', 'text'

    def __init__(self) -> None:
        self.mfn: int = 0
        self.tag: int = 0
        self.occurrence: int = 0
        self.count: int = 0
        self.text: Optional[str] = None

    def parse(self, text: str) -> None:
        """
        Parse the text for term postings.

        :param text: Text to parse
        :return: None
        """

        parts = text.split('#', 4)
        if len(parts) < 4:
            return
        self.mfn = int(parts[0])
        self.tag = int(parts[1])
        self.occurrence = int(parts[2])
        self.count = int(parts[3])
        if len(parts) > 4:
            self.text = parts[4]

    def __str__(self):
        subst = ''
        if self.text:
            subst = self.text
        return ' '.join([str(self.mfn), str(self.tag),
                         str(self.occurrence), str(self.count),
                         subst])

    def __repr__(self):
        return self.__str__()


def get_record_postings(connection: Connection, mfn: int, prefix: str) -> List[TermPosting]:
    """
    Получение постингов для указанных записи и префикса.

    :param connection: Подключение.
    :param mfn: MFN записи.
    :param prefix: Префикс в виде "A=$".
    :return: Список постингов.
    """
    assert connection and isinstance(connection, Connection)

    query = ClientQuery(connection, 'V')
    query.ansi(connection.database)
    query.add(mfn)
    query.utf(prefix)
    result: List[TermPosting] = []
    with connection.execute(query) as response:
        response.check_return_code()
        lines = response.utf_remaining_lines()
        for line in lines:
            one: TermPosting = TermPosting()
            one.parse(line)
            result.append(one)
    return result


Connection.get_record_postings = get_record_postings  # type: ignore


###############################################################################


class TermInfo:
    """
    Информация о поисковом терме.
    """

    __slots__ = 'count', 'text'

    def __init__(self, count: int = 0, text: str = '') -> None:
        self.count: int = count
        self.text: str = text

    @staticmethod
    def parse(lines: Iterable[str]):
        """
        Parse the text for term info.

        :param lines: Text to parse
        :return: Term info
        """
        result = []
        for line in lines:
            parts = line.split('#', 1)
            item = TermInfo(int(parts[0]), parts[1])
            result.append(item)
        return result

    def __str__(self):
        return str(self.count) + '#' + self.text

    def __repr__(self):
        return str(self.count) + '#' + self.text


###############################################################################


class TermParameters:
    """
    Параметры для команды ReadTerms
    """

    __slots__ = 'database', 'number', 'reverse', 'start', 'format'

    def __init__(self, start: str = None, number: int = 10) -> None:
        self.database: str = ''
        self.number: int = number
        self.reverse: bool = False
        self.start: Optional[str] = start
        self.format: Optional[str] = None

    def __str__(self):
        return str(self.number) + ' ' + safe_str(self.format)


def read_terms(connection: Connection,
               parameters: Union[TermParameters, str, Tuple[str, int]]) -> List[TermInfo]:
    """
    Получение термов поискового словаря.

    :param connection: Подключение
    :param parameters: Параметры термов или терм или кортеж "терм, количество"
    :return: Список термов
    """
    assert connection and isinstance(connection, Connection)

    if isinstance(parameters, tuple):
        parameters2 = TermParameters(parameters[0])
        parameters2.number = parameters[1]
        parameters = parameters2

    if isinstance(parameters, str):
        parameters = TermParameters(parameters)
        parameters.number = 10

    assert isinstance(parameters, TermParameters)

    database = parameters.database or connection.database or throw_value_error()
    command = READ_TERMS_REVERSE if parameters.reverse else READ_TERMS
    query = ClientQuery(connection, command)
    query.ansi(database).utf(parameters.start)
    query.add(parameters.number).ansi(parameters.format)
    with connection.execute(query) as response:
        response.check_return_code(READ_TERMS_CODES)
        lines = response.utf_remaining_lines()
        result = TermInfo.parse(lines)
        return result


Connection.read_terms = read_terms  # type: ignore


###############################################################################


class PostingParameters:
    """
    Параметры для команды ReadPostings.
    """

    __slots__ = 'database', 'first', 'fmt', 'number', 'terms'

    def __init__(self, term: str = None, fmt: str = None) -> None:
        self.database: Optional[str] = None
        self.first: int = 1
        self.fmt: Optional[str] = fmt
        self.number: int = 0
        self.terms: List[str] = []
        if term:
            self.terms.append(term)

    def __str__(self):
        return str(self.terms)

    def __repr__(self):
        return str(self.terms)


def read_postings(connection: Connection,
                  parameters: Union[PostingParameters, str],
                  fmt: Optional[str] = None) -> List[TermPosting]:
    """
    Считывание постингов для указанных термов из поискового словаря.

    :param connection: Подключение
    :param parameters: Параметры постингов или терм
    :param fmt: Опциональный формат
    :return: Список постингов
    """
    assert connection and isinstance(connection, Connection)

    if isinstance(parameters, str):
        parameters = PostingParameters(parameters)
        parameters.fmt = fmt

    database = parameters.database or connection.database or throw_value_error()
    query = ClientQuery(connection, READ_POSTINGS)
    query.ansi(database).add(parameters.number)
    query.add(parameters.first).ansi(parameters.fmt)
    for term in parameters.terms:
        query.utf(term)
    with connection.execute(query) as response:
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


Connection.read_postings = read_postings  # type: ignore


###############################################################################


class TreeNode:
    """
    TRE-file line.
    """

    __slots__ = 'children', 'value', 'level'

    def __init__(self, value: Optional[str] = None, level: int = 0) -> None:
        self.children: List = []
        self.value: Optional[str] = value
        self.level: int = level

    def add(self, name: str):
        """
        Add a child node.

        :param name: Name of the child.
        :return: Added subnode
        """

        result = TreeNode(name)
        self.children.append(result)
        return result

    def write(self) -> List[str]:
        """
        Represent the node and its child as lines.

        :return: List of lines
        """
        result = [TreeFile.INDENT * self.level + safe_str(self.value)]
        for child in self.children:
            inner = child.write()
            result.extend(inner)
        return result

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class TreeFile:
    """
    TRE-file.
    """

    INDENT = '\u0009'

    __slots__ = ('roots',)

    def __init__(self):
        self.roots: List[TreeNode] = []

    @staticmethod
    def _count_indent(text: str) -> int:
        result = 0
        for char in text:
            if char == TreeFile.INDENT:
                result += 1
            else:
                break
        return result

    @staticmethod
    def _arrange_level(nodes: List[TreeNode], level: int) -> None:
        count = len(nodes)
        index = 0
        while index < count:
            index = TreeFile._arrange_nodes(nodes, level, index, count)

    @staticmethod
    def _arrange_nodes(nodes: List[TreeNode], level: int, index: int, count: int) -> int:
        nxt = index + 1
        level2 = level + 1
        parent = nodes[index]
        while nxt < count:
            child = nodes[nxt]
            if child.level <= level:
                break
            if child.level == level2:
                parent.children.append(child)
            nxt += 1
        return nxt

    def add(self, name: str) -> TreeNode:
        """
        Add zero level node with specified name.

        :param name: Name of the node
        :return: Created node
        """

        result = TreeNode(name)
        self.roots.append(result)
        return result

    @staticmethod
    def determine_level(nodes: Iterable[TreeNode], current: int) -> None:
        """
        Determine level of the nodes.

        :param nodes: Nodes to process
        :param current: Current level
        :return: None
        """

        for node in nodes:
            node.level = current
            TreeFile.determine_level(node.children, current + 1)

    def parse(self, text: Iterable[str]) -> None:
        """
        Parse the text for the tree structure.

        :param text: Text to parse
        :return: None
        """

        nodes = []
        for line in text:
            level = TreeFile._count_indent(line)
            line = line[level:]
            node = TreeNode(line, level)
            nodes.append(node)

        max_level = max(node.level for node in nodes)
        for level in range(max_level):
            TreeFile._arrange_level(nodes, level)

        for node in nodes:
            if node.level == 0:
                self.roots.append(node)

    def save(self, filename: str) -> None:
        """
        Save the tree to the specified file.

        :param filename: Name of the file
        :return: None
        """

        with open(filename, 'wt', encoding=ANSI) as stream:
            text = str(self)
            stream.write(text)

    def __str__(self):
        TreeFile.determine_level(self.roots, 0)
        result = []
        for node in self.roots:
            result.extend(node.write())
        return '\n'.join(result)


def load_tree_file(filename: str) -> TreeFile:
    """
    Load the tree from the specified file.

    :param filename: Name of the file.
    :return: Tree structure
    """

    result = TreeFile()
    with open(filename, 'rt', encoding=ANSI) as stream:
        lines = stream.readlines()
        result.parse(lines)
    return result


def read_tree_file(connection: Connection,
                   specification: Union[FileSpecification, str]) -> TreeFile:
    """
    Чтение TRE-файла с сервера.

    :param connection: Подключение
    :param specification:  Спецификация
    :return: Дерево
    """

    assert connection and isinstance(connection, Connection)

    with connection.read_text_stream(specification) as response:
        text = response.ansi_remaining_text()
        text = [line for line in irbis_to_lines(text) if line]
        result = TreeFile()
        result.parse(text)
        return result


Connection.read_tree_file = read_tree_file  # type: ignore


###############################################################################


class SearchScenario:
    """
    Сценарий поиска.
    """

    __slots__ = ('name', 'prefix', 'type', 'menu', 'old',
                 'correction', 'truncation', 'hint',
                 'mod_by_dic_auto', 'logic', 'advance',
                 'format')

    def __init__(self, name: Optional[str] = None) -> None:
        self.name: Optional[str] = name
        self.prefix: Optional[str] = None
        self.type: int = 0
        self.menu: Optional[str] = None
        self.old: Optional[str] = None
        self.correction: Optional[str] = None
        self.truncation: bool = False
        self.hint: Optional[str] = None
        self.mod_by_dic_auto: Optional[str] = None
        self.logic: int = 0
        self.advance: Optional[str] = None
        self.format: Optional[str] = None

    @staticmethod
    def parse(ini: IniFile) -> List:
        """
        Parse the INI file for the search scenarios.

        :param ini: INI file
        :return: List of search scenarios
        """

        section = ini.find('SEARCH')
        if not section:
            return []
        count = safe_int(safe_str(section.get_value('ItemNumb', '0')))
        if not count:
            return []
        result = []
        for i in range(count):
            name = section.get_value(f'ItemName{i}')
            scenario = SearchScenario(name)
            result.append(scenario)
            scenario.prefix = section.get_value(f'ItemPref{i}') or ''
            scenario.type = safe_int(safe_str(section.get_value(f'ItemDictionType{i}', '0')))
            scenario.menu = section.get_value(f'ItemMenu{i}')
            scenario.old = None
            scenario.correction = section.get_value(f'ItemModByDic{i}')
            scenario.truncation = bool(section.get_value(f'ItemTranc{i}', '0'))
            scenario.hint = section.get_value(f'ItemHint{i}')
            scenario.mod_by_dic_auto = section.get_value(f'ItemModByDicAuto{i}')
            scenario.logic = safe_int(safe_str(section.get_value(f'ItemLogic{i}', '0')))
            scenario.advance = section.get_value(f'ItemAdv{i}')
            scenario.format = section.get_value(f'ItemPft{i}')
        return result

    def __str__(self):
        if not self.prefix:
            return safe_str(self.name)

        return safe_str(self.name) + ' ' + safe_str(self.prefix)


def read_search_scenario(connection: Connection,
                         specification: Union[FileSpecification, str]) -> List[SearchScenario]:
    """
    Read search scenario from the server.

    :param connection: Connection to use
    :param specification: File which contains the scenario
    :return: List of the scenarios (possibly empty)
    """

    assert connection and isinstance(connection, Connection)

    if isinstance(specification, str):
        specification = connection.near_master(specification)

    with connection.read_text_stream(specification) as response:
        ini = IniFile()
        text = irbis_to_lines(response.ansi_remaining_text())
        ini.parse(text)
        result = SearchScenario.parse(ini)
        return result


Connection.read_search_scenario = read_search_scenario  # type: ignore


###############################################################################


class UserInfo:
    """
    Информация о зарегистрированном пользователе системы.
    """

    __slots__ = ('number', 'name', 'password', 'cataloger',
                 'reader', 'circulation', 'acquisitions',
                 'provision', 'administrator')

    def __init__(self, name: Optional[str] = None, password: Optional[str] = None) -> None:
        self.number: Optional[str] = None
        self.name: Optional[str] = name
        self.password: Optional[str] = password
        self.cataloger: Optional[str] = None
        self.reader: Optional[str] = None
        self.circulation: Optional[str] = None
        self.acquisitions: Optional[str] = None
        self.provision: Optional[str] = None
        self.administrator: Optional[str] = None

    @staticmethod
    def parse(response: ServerResponse) -> List:
        """
        Parse the server response for the user info.

        :param response: Response to parse.
        :return: List of user infos.
        """

        result: List = []
        user_count = response.number()
        lines_per_user = response.number()
        if not user_count or not lines_per_user:
            return result
        for _ in range(user_count):
            user = UserInfo()
            user.number = response.ansi()
            user.name = response.ansi()
            user.password = response.ansi()
            user.cataloger = response.ansi()
            user.reader = response.ansi()
            user.circulation = response.ansi()
            user.acquisitions = response.ansi()
            user.provision = response.ansi()
            user.administrator = response.ansi()
            result.append(user)
        return result

    @staticmethod
    def format_pair(prefix: str, value: str, default: str) -> str:
        """
        Format the pair prefix=value.

        :param prefix: Prefix to use
        :param value: Value to use
        :param default: Default value
        :return: Formatted text
        """

        if same_string(value, default):
            return ''

        return prefix + '=' + safe_str(value) + ';'

    def encode(self):
        """
        Encode the user info.

        :return: Text representation of the user info.
        """

        return self.name + '\n' + self.password + '\n' \
            + UserInfo.format_pair('C', self.cataloger, "irbisc.ini") \
            + UserInfo.format_pair('R', self.reader, "irbisr.ini") \
            + UserInfo.format_pair('B', self.circulation, "irbisb.ini") \
            + UserInfo.format_pair('M', self.acquisitions, "irbism.ini") \
            + UserInfo.format_pair('K', self.provision, "irbisk.ini") \
            + UserInfo.format_pair('A', self.administrator, "irbisa.ini")

    def __str__(self):
        buffer = [self.number, self.name, self.password, self.cataloger,
                  self.reader, self.circulation, self.acquisitions,
                  self.provision, self.administrator]
        return ' '.join(x for x in buffer if x)


def get_user_list(connection: Connection) -> List[UserInfo]:
    """
    Получение списка пользователей с сервера.

    :param connection: Подключение
    :return: Список пользователей
    """

    assert connection and isinstance(connection, Connection)

    query = ClientQuery(connection, GET_USER_LIST)
    with connection.execute(query) as response:
        response.check_return_code()
        result = UserInfo.parse(response)
        return result


def update_user_list(connection: Connection, users: List[UserInfo]) -> None:
    """
    Обновление списка пользователей на сервере.

    :param connection: Подключение
    :param users:  Список пользователей
    :return: None
    """
    assert connection and isinstance(connection, Connection)
    assert isinstance(users, list) and users

    query = ClientQuery(connection, SET_USER_LIST)
    for user in users:
        query.ansi(user.encode())
    connection.execute_forget(query)


Connection.get_user_list = get_user_list  # type: ignore
Connection.update_user_list = update_user_list  # type: ignore


###############################################################################


class OptLine:
    """
    Строка в OPT-файле.
    """

    __slots__ = 'pattern', 'worksheet'

    def __init__(self, pattern: str = '', worksheet: str = '') -> None:
        self.pattern: str = pattern
        self.worksheet: str = worksheet

    def parse(self, text: str) -> None:
        """
        Parse the line.

        :param text: Text to parse
        :return: None
        """

        parts = re.split(r'\s+', text.strip())
        self.pattern = parts[0]
        self.worksheet = parts[1]


class OptFile:
    """
    OPT-файл.
    """

    WILDCARD = '+'

    __slots__ = 'lines', 'length', 'tag'

    def __init__(self):
        self.lines: List[OptLine] = []
        self.length: int = 5
        self.tag: int = 920

    def parse(self, text: List[str]) -> None:
        """
        Parse the text for OPT table.

        :param text: Text to parse
        :return: None
        """
        self.tag = int(text[0])
        self.length = int(text[1])
        for line in text[2:]:
            if not line:
                continue
            line = line.strip()
            if not line:
                continue
            if line.startswith('*'):
                continue
            one = OptLine()
            one.parse(line)
            self.lines.append(one)

    @staticmethod
    def same_char(pattern: str, testable: str) -> bool:
        """
        Compare the character against the pattern.

        :param pattern: Pattern character
        :param testable: Character to examine
        :return: True or False
        """
        if pattern == OptFile.WILDCARD:
            return True
        return pattern.lower() == testable.lower()

    def same_text(self, pattern: str, testable: str) -> bool:
        """
        Compare tag value against the OPT pattern.

        :param pattern: Pattern to use
        :param testable: Tag value to examine
        :return: True or False
        """

        if not pattern:
            return False

        if not testable:
            return pattern[0] == OptFile.WILDCARD

        pattern_index = 0
        testable_index = 0

        while True:
            pattern_char = pattern[pattern_index]
            testable_char = testable[testable_index]
            pattern_index += 1
            testable_index += 1
            pattern_next = pattern_index < len(pattern)
            testable_next = testable_index < len(testable)

            if pattern_next and not testable_next:
                if pattern_char == OptFile.WILDCARD:
                    while pattern_index < len(pattern):
                        pattern_char = pattern[pattern_index]
                        pattern_index += 1
                        if pattern_char != OptFile.WILDCARD:
                            return False
                    return True

            if pattern_next != testable_next:
                return False
            if not pattern_next:
                return True
            if not self.same_char(pattern_char, testable_char):
                return False

    def resolve_worksheet(self, tag: str) -> Optional[str]:
        """
        Resolve worksheet for the specified tag value.

        :param tag: Tag value, e. g. "SPEC"
        :return: Worksheet name or None
        """

        for line in self.lines:
            if self.same_text(line.pattern, tag):
                return line.worksheet
        return None

    def save(self, filename: str) -> None:
        """
        Save the OPT table to the specified file.

        :param filename: Name of the file
        :return: None
        """
        with open(filename, 'wt', encoding=ANSI) as stream:
            text = str(self)
            stream.write(text)

    def __str__(self):
        result = [str(self.tag), str(self.length)]
        for line in self.lines:
            result.append(line.pattern.ljust(6) + line.worksheet)
        result.append(STOP_MARKER)
        return '\n'.join(result)


def load_opt_file(filename: str) -> OptFile:
    """
    Load the OPT from the specified file.

    :param filename: Name of the file
    :return: OPT file
    """

    result = OptFile()
    with open(filename, 'rt', encoding=ANSI) as stream:
        lines = stream.readlines()
        result.parse(lines)
    return result


def read_opt_file(connection: Connection,
                  specification: Union[FileSpecification, str]) -> OptFile:
    """
    Получение файла оптимизации рабочих листов с сервера.

    :param connection: Подключение
    :param specification: Спецификация
    :return: Файл оптимизации
    """
    assert connection and isinstance(connection, Connection)

    with connection.read_text_stream(specification) as response:
        result = OptFile()
        text = irbis_to_lines(response.ansi_remaining_text())
        result.parse(text)
        return result


Connection.read_opt_file = read_opt_file  # type: ignore


###############################################################################


class ClientInfo:
    """
    Информация о клиенте, подключенном к серверу ИРБИС
    (не обязательно о текущем)
    """

    __slots__ = ('number', 'ip_address', 'port', 'name', 'client_id',
                 'workstation', 'registered', 'acknowledged',
                 'last_command', 'command_number')

    def __init__(self):
        self.number: Optional[str] = None
        self.ip_address: Optional[str] = None
        self.port: Optional[str] = None
        self.name: Optional[str] = None
        self.client_id: Optional[str] = None
        self.workstation: Optional[str] = None
        self.registered: Optional[str] = None
        self.acknowledged: Optional[str] = None
        self.last_command: Optional[str] = None
        self.command_number: Optional[str] = None

    def __str__(self):
        return ' '.join([self.number, self.ip_address, self.port, self.name,
                         self.client_id, self.workstation,
                         self.registered, self.acknowledged,
                         self.last_command, self.command_number])

    def __repr__(self):
        return self.__str__()


###############################################################################


class ServerStat:
    """
    Статистика работы ИРБИС-сервера
    """

    __slots__ = 'running_clients', 'client_count', 'total_command_count'

    def __init__(self):
        self.running_clients: [ClientInfo] = []
        self.client_count: int = 0
        self.total_command_count: int = 0

    def parse(self, response: ServerResponse) -> None:
        """
        Parse the server response for the stat.

        :param response: Server response
        :return: None
        """

        self.total_command_count = response.number()
        self.client_count = response.number()
        lines_per_client = response.number()
        if not lines_per_client:
            return

        for _ in range(self.client_count):
            client = ClientInfo()
            client.number = response.ansi()
            client.ip_address = response.ansi()
            client.port = response.ansi()
            client.name = response.ansi()
            client.client_id = response.ansi()
            client.workstation = response.ansi()
            client.registered = response.ansi()
            client.acknowledged = response.ansi()
            client.last_command = response.ansi()
            client.command_number = response.ansi()
            self.running_clients.append(client)

    def __str__(self):
        return str(self.client_count) + ', ' + str(self.total_command_count)


def get_server_stat(connection: Connection) -> ServerStat:
    """
    Получение статистики с сервера.

    :return: Полученная статистика
    """

    assert connection and isinstance(connection, Connection)

    query = ClientQuery(connection, GET_SERVER_STAT)
    with connection.execute(query) as response:
        response.check_return_code()
        result = ServerStat()
        result.parse(response)
        return result


Connection.get_server_stat = get_server_stat  # type: ignore


###############################################################################


class DatabaseInfo:
    """
    Информация о базе данных ИРБИС.
    """

    __slots__ = ('name', 'description', 'max_mfn', 'logically_deleted',
                 'physically_deleted', 'nonactualized', 'locked_records',
                 'database_locked', 'read_only')

    def __init__(self, name: Optional[str] = None, description: Optional[str] = None) -> None:
        self.name: Optional[str] = name
        self.description: Optional[str] = description
        self.max_mfn: int = 0
        self.logically_deleted: List[int] = []
        self.physically_deleted: List[int] = []
        self.nonactualized: List[int] = []
        self.locked_records: List[int] = []
        self.database_locked: bool = False
        self.read_only: bool = False

    @staticmethod
    def _parse(line: str) -> List[int]:
        if not line:
            return []
        return [int(x) for x in line.split(SHORT_DELIMITER) if x]

    def parse(self, response: ServerResponse) -> None:
        """
        Parse the server response for database info.

        :param response: Response to parse
        :return: None
        """
        self.logically_deleted = self._parse(response.ansi())
        self.physically_deleted = self._parse(response.ansi())
        self.nonactualized = self._parse(response.ansi())
        self.locked_records = self._parse(response.ansi())
        self.max_mfn = int(response.ansi())
        self.database_locked = bool(int(response.ansi()))

    def __str__(self):
        if not self.description:
            return self.name or '(none)'
        return self.name + ' - ' + self.description


def get_database_info(connection: Connection,
                      database: Optional[str] = None) -> DatabaseInfo:
    """
    Получение информации о базе данных.

    :param connection: Подключение
    :param database: Имя базы
    :return: Информация о базе
    """

    assert connection and isinstance(connection, Connection)

    database = database or connection.database or throw_value_error()
    query = ClientQuery(connection, RECORD_LIST).ansi(database)
    with connection.execute(query) as response:
        response.check_return_code()
        result = DatabaseInfo()
        result.parse(response)
        result.name = database
        return result


Connection.get_database_info = get_database_info  # type: ignore


###############################################################################


class TableDefinition:
    """
    Определение таблицы, данные для команды TableCommand
    """

    __slots__ = ('database', 'table', 'headers', 'mode', 'search',
                 'min_mfn', 'max_mfn', 'sequential', 'mfn_list')

    def __init__(self):
        self.database: Optional[str] = None
        self.table: Optional[str] = None
        self.headers: [str] = []
        self.mode: Optional[str] = None
        self.search: Optional[str] = None
        self.min_mfn: int = 0
        self.max_mfn: int = 0
        self.sequential: Optional[str] = None
        self.mfn_list: [int] = []


def print_table(connection: Connection,
                definition: TableDefinition) -> str:
    """
    Расформатирование таблицы.

    :param connection: Подключение
    :param definition: Определение таблицы
    :return: Результат расформатирования
    """

    assert connection and isinstance(connection, Connection)

    database = definition.database or connection.database or throw_value_error()
    query = ClientQuery(connection, PRINT)
    query.ansi(database).ansi(definition.table)
    query.ansi('')  # instead of the headers
    query.ansi(definition.mode).utf(definition.search)
    query.add(definition.min_mfn).add(definition.max_mfn)
    query.utf(definition.sequential)
    query.ansi('')  # instead of the MFN list
    with connection.execute(query) as response:
        result = response.utf_remaining_text()
        return result


Connection.print_table = print_table  # type: ignore


###############################################################################


class AlphabetTable:
    """
    Alphabet character table
    """

    FILENAME = 'isisacw.tab'

    __slots__ = ('characters',)

    def __init__(self) -> None:
        self.characters: List[str] = []

    @staticmethod
    def get_default():
        """
        Get the default alphabet table.

        :return: Alphabet table
        """
        result = AlphabetTable()
        result.characters = [
            '\u0026', '\u0040', '\u0041', '\u0042', '\u0043', '\u0044', '\u0045',
            '\u0046', '\u0047', '\u0048', '\u0049', '\u004A', '\u004B', '\u004C',
            '\u004D', '\u004E', '\u004F', '\u0050', '\u0051', '\u0052', '\u0053',
            '\u0054', '\u0055', '\u0056', '\u0057', '\u0058', '\u0059', '\u005A',
            '\u0061', '\u0062', '\u0063', '\u0064', '\u0065', '\u0066', '\u0067',
            '\u0068', '\u0069', '\u006A', '\u006B', '\u006C', '\u006D', '\u006E',
            '\u006F', '\u0070', '\u0071', '\u0072', '\u0073', '\u0074', '\u0075',
            '\u0076', '\u0077', '\u0078', '\u0079', '\u007A', '\u0098', '\u00A0',
            '\u00A4', '\u00A6', '\u00A7', '\u00A9', '\u00AB', '\u00AC', '\u00AD',
            '\u00AE', '\u00B0', '\u00B1', '\u00B5', '\u00B6', '\u00B7', '\u00BB',
            '\u0401', '\u0402', '\u0403', '\u0404', '\u0405', '\u0406', '\u0407',
            '\u0408', '\u0409', '\u040A', '\u040B', '\u040C', '\u040E', '\u040F',
            '\u0410', '\u0411', '\u0412', '\u0413', '\u0414', '\u0415', '\u0416',
            '\u0417', '\u0418', '\u0419', '\u041A', '\u041B', '\u041C', '\u041D',
            '\u041E', '\u041F', '\u0420', '\u0421', '\u0422', '\u0423', '\u0424',
            '\u0425', '\u0426', '\u0427', '\u0428', '\u0429', '\u042A', '\u042B',
            '\u042C', '\u042D', '\u042E', '\u042F', '\u0430', '\u0431', '\u0432',
            '\u0433', '\u0434', '\u0435', '\u0436', '\u0437', '\u0438', '\u0439',
            '\u043A', '\u043B', '\u043C', '\u043D', '\u043E', '\u043F', '\u0440',
            '\u0441', '\u0442', '\u0443', '\u0444', '\u0445', '\u0446', '\u0447',
            '\u0448', '\u0449', '\u044A', '\u044B', '\u044C', '\u044D', '\u044E',
            '\u044F', '\u0451', '\u0452', '\u0453', '\u0454', '\u0455', '\u0456',
            '\u0457', '\u0458', '\u0459', '\u045A', '\u045B', '\u045C', '\u045E',
            '\u045F', '\u0490', '\u0491', '\u2013', '\u2014', '\u2018', '\u2019',
            '\u201A', '\u201C', '\u201D', '\u201E', '\u2020', '\u2021', '\u2022',
            '\u2026', '\u2030', '\u2039', '\u203A', '\u20AC', '\u2116', '\u2122'
        ]
        return result

    def is_alpha(self, char: str) -> bool:
        """
        Determine whether the character is in the alphabet.

        :param char: Character to examine
        :return: True or False
        """

        return char in self.characters

    def parse(self, text: str) -> None:
        """
        Parse the text for alphabet table.

        :param text: Text to parse
        :return: None
        """
        parts = re.findall(r'\d+', text)
        array = bytearray(int(x) for x in parts if x and x.isdigit())
        array.remove(0x98)  # Этот символ не мапится
        self.characters = list(array.decode(ANSI))

    def split_words(self, text: str) -> List[str]:
        """
        Split the text to words according the alphabet table.

        :param text: Text to split
        :return: List of words
        """

        # TODO convert to generator?

        result = []
        accumulator = []
        for char in text:
            if char in self.characters:
                accumulator.append(char)
            else:
                if accumulator:
                    result.append(''.join(accumulator))
                    accumulator.clear()
        if accumulator:
            result.append(''.join(accumulator))
        return result

    def trim(self, text: str) -> str:
        """
        Trim the text according to the alphabet table.

        :param text: Text to trim
        :return: Trimmed text
        """
        result = text
        while result and result[0] not in self.characters:
            result = result[1:]
        while result and result[-1] not in self.characters:
            result = result[:-1]
        return result


def load_alphabet_table(filename: str) -> AlphabetTable:
    """
    Load the alphabet table from the specified file.

    :param filename: Name of the file
    :return: Alphabet table
    """
    with open(filename, 'rt', encoding=ANSI) as stream:
        text = stream.read()
    result = AlphabetTable()
    result.parse(text)
    return result


def read_alphabet_table(connection: Connection,
                        specification: Optional[FileSpecification] = None) -> AlphabetTable:
    """
    Чтение алфавитной таблицы с сервера.

    :param connection: Подключение
    :param specification: Спецификация
    :return: Таблица
    """

    assert connection and isinstance(connection, Connection)

    if specification is None:
        specification = FileSpecification(SYSTEM, None, AlphabetTable.FILENAME)

    with connection.read_text_stream(specification) as response:
        text = response.ansi_remaining_text()
        if text:
            result = AlphabetTable()
            result.parse(text)
        else:
            result = AlphabetTable.get_default()
        return result


Connection.read_alphabet_table = read_alphabet_table  # type: ignore


###############################################################################


class UpperCaseTable:
    """
    Upper-case character table.
    """

    FILENAME = 'isisucw.tab'

    __slots__ = ('mapping',)

    def __init__(self) -> None:
        self.mapping: Dict = dict()

    @staticmethod
    def get_default():
        """
        Get the default uppercase table.

        :return: Uppercase table
        """
        result = UpperCaseTable()
        result.mapping = {
            chr(0x0000): chr(0x0000),
            chr(0x0001): chr(0x0001),
            chr(0x0002): chr(0x0002),
            chr(0x0003): chr(0x0003),
            chr(0x0004): chr(0x0004),
            chr(0x0005): chr(0x0005),
            chr(0x0006): chr(0x0006),
            chr(0x0007): chr(0x0007),
            chr(0x0008): chr(0x0008),
            chr(0x0009): chr(0x0009),
            chr(0x000A): chr(0x000A),
            chr(0x000B): chr(0x000B),
            chr(0x000C): chr(0x000C),
            chr(0x000D): chr(0x000D),
            chr(0x000E): chr(0x000E),
            chr(0x000F): chr(0x000F),
            chr(0x0010): chr(0x0010),
            chr(0x0011): chr(0x0011),
            chr(0x0012): chr(0x0012),
            chr(0x0013): chr(0x0013),
            chr(0x0014): chr(0x0014),
            chr(0x0015): chr(0x0015),
            chr(0x0016): chr(0x0016),
            chr(0x0017): chr(0x0017),
            chr(0x0018): chr(0x0018),
            chr(0x0019): chr(0x0019),
            chr(0x001A): chr(0x001A),
            chr(0x001B): chr(0x001B),
            chr(0x001C): chr(0x001C),
            chr(0x001D): chr(0x001C),
            chr(0x001E): chr(0x001E),
            chr(0x001F): chr(0x001F),
            chr(0x0020): chr(0x0020),
            chr(0x0021): chr(0x0021),
            chr(0x0022): chr(0x0022),
            chr(0x0023): chr(0x0023),
            chr(0x0024): chr(0x0024),
            chr(0x0025): chr(0x0025),
            chr(0x0026): chr(0x0026),
            chr(0x0027): chr(0x0027),
            chr(0x0028): chr(0x0028),
            chr(0x0029): chr(0x0029),
            chr(0x002A): chr(0x002A),
            chr(0x002B): chr(0x002B),
            chr(0x002C): chr(0x002C),
            chr(0x002D): chr(0x002D),
            chr(0x002E): chr(0x002E),
            chr(0x002F): chr(0x002F),
            chr(0x0030): chr(0x0030),
            chr(0x0031): chr(0x0031),
            chr(0x0032): chr(0x0032),
            chr(0x0033): chr(0x0033),
            chr(0x0034): chr(0x0034),
            chr(0x0035): chr(0x0035),
            chr(0x0036): chr(0x0036),
            chr(0x0037): chr(0x0037),
            chr(0x0038): chr(0x0038),
            chr(0x0039): chr(0x0039),
            chr(0x003A): chr(0x003A),
            chr(0x003B): chr(0x003B),
            chr(0x003C): chr(0x003C),
            chr(0x003D): chr(0x003D),
            chr(0x003E): chr(0x003E),
            chr(0x003F): chr(0x003F),
            chr(0x0040): chr(0x0040),
            chr(0x0041): chr(0x0041),
            chr(0x0042): chr(0x0042),
            chr(0x0043): chr(0x0043),
            chr(0x0044): chr(0x0044),
            chr(0x0045): chr(0x0045),
            chr(0x0046): chr(0x0046),
            chr(0x0047): chr(0x0047),
            chr(0x0048): chr(0x0048),
            chr(0x0049): chr(0x0049),
            chr(0x004A): chr(0x004A),
            chr(0x004B): chr(0x004B),
            chr(0x004C): chr(0x004C),
            chr(0x004D): chr(0x004D),
            chr(0x004E): chr(0x004E),
            chr(0x004F): chr(0x004F),
            chr(0x0050): chr(0x0050),
            chr(0x0051): chr(0x0051),
            chr(0x0052): chr(0x0052),
            chr(0x0053): chr(0x0053),
            chr(0x0054): chr(0x0054),
            chr(0x0055): chr(0x0055),
            chr(0x0056): chr(0x0056),
            chr(0x0057): chr(0x0057),
            chr(0x0058): chr(0x0058),
            chr(0x0059): chr(0x0059),
            chr(0x005A): chr(0x005A),
            chr(0x005B): chr(0x005B),
            chr(0x005C): chr(0x005C),
            chr(0x005D): chr(0x005D),
            chr(0x005E): chr(0x005E),
            chr(0x005F): chr(0x005F),
            chr(0x0060): chr(0x0060),
            chr(0x0061): chr(0x0041),
            chr(0x0062): chr(0x0042),
            chr(0x0063): chr(0x0043),
            chr(0x0064): chr(0x0044),
            chr(0x0065): chr(0x0045),
            chr(0x0066): chr(0x0046),
            chr(0x0067): chr(0x0047),
            chr(0x0068): chr(0x0048),
            chr(0x0069): chr(0x0049),
            chr(0x006A): chr(0x004A),
            chr(0x006B): chr(0x004B),
            chr(0x006C): chr(0x004C),
            chr(0x006D): chr(0x004D),
            chr(0x006E): chr(0x004E),
            chr(0x006F): chr(0x004F),
            chr(0x0070): chr(0x0050),
            chr(0x0071): chr(0x0051),
            chr(0x0072): chr(0x0052),
            chr(0x0073): chr(0x0053),
            chr(0x0074): chr(0x0054),
            chr(0x0075): chr(0x0055),
            chr(0x0076): chr(0x0056),
            chr(0x0077): chr(0x0057),
            chr(0x0078): chr(0x0058),
            chr(0x0079): chr(0x0059),
            chr(0x007A): chr(0x005A),
            chr(0x007B): chr(0x007B),
            chr(0x007C): chr(0x007C),
            chr(0x007D): chr(0x007D),
            chr(0x007E): chr(0x007E),
            chr(0x007F): chr(0x007F),
            chr(0x0402): chr(0x0402),
            chr(0x0403): chr(0x0403),
            chr(0x201A): chr(0x201A),
            chr(0x0453): chr(0x0453),
            chr(0x201E): chr(0x201E),
            chr(0x2026): chr(0x2026),
            chr(0x2020): chr(0x2020),
            chr(0x2021): chr(0x2021),
            chr(0x20AC): chr(0x20AC),
            chr(0x2030): chr(0x2030),
            chr(0x0409): chr(0x0409),
            chr(0x2039): chr(0x2039),
            chr(0x040A): chr(0x040A),
            chr(0x040C): chr(0x040C),
            chr(0x040B): chr(0x040B),
            chr(0x040F): chr(0x040F),
            chr(0x0452): chr(0x0452),
            chr(0x2018): chr(0x2018),
            chr(0x2019): chr(0x2019),
            chr(0x201C): chr(0x201C),
            chr(0x201D): chr(0x201D),
            chr(0x2022): chr(0x2022),
            chr(0x2013): chr(0x2013),
            chr(0x2014): chr(0x2014),
            chr(0x0098): chr(0x0098),
            chr(0x2122): chr(0x2122),
            chr(0x0459): chr(0x0459),
            chr(0x203A): chr(0x203A),
            chr(0x045A): chr(0x045A),
            chr(0x045C): chr(0x045C),
            chr(0x045B): chr(0x045B),
            chr(0x045F): chr(0x045F),
            chr(0x00A0): chr(0x00A0),
            chr(0x040E): chr(0x040E),
            chr(0x045E): chr(0x040E),
            chr(0x0408): chr(0x0408),
            chr(0x00A4): chr(0x00A4),
            chr(0x0490): chr(0x0490),
            chr(0x00A6): chr(0x00A6),
            chr(0x00A7): chr(0x00A7),
            chr(0x0401): chr(0x0401),
            chr(0x00A9): chr(0x00A9),
            chr(0x0404): chr(0x0404),
            chr(0x00AB): chr(0x00AB),
            chr(0x00AC): chr(0x00AC),
            chr(0x00AD): chr(0x00AD),
            chr(0x00AE): chr(0x00AE),
            chr(0x0407): chr(0x0407),
            chr(0x00B0): chr(0x00B0),
            chr(0x00B1): chr(0x00B1),
            chr(0x0406): chr(0x0406),
            chr(0x0456): chr(0x0406),
            chr(0x0491): chr(0x0490),
            chr(0x00B5): chr(0x00B5),
            chr(0x00B6): chr(0x00B6),
            chr(0x00B7): chr(0x00B7),
            chr(0x0451): chr(0x0401),
            chr(0x2116): chr(0x2116),
            chr(0x0454): chr(0x0404),
            chr(0x00BB): chr(0x00BB),
            chr(0x0458): chr(0x0408),
            chr(0x0405): chr(0x0405),
            chr(0x0455): chr(0x0405),
            chr(0x0457): chr(0x0407),
            chr(0x0410): chr(0x0410),
            chr(0x0411): chr(0x0411),
            chr(0x0412): chr(0x0412),
            chr(0x0413): chr(0x0413),
            chr(0x0414): chr(0x0414),
            chr(0x0415): chr(0x0415),
            chr(0x0416): chr(0x0416),
            chr(0x0417): chr(0x0417),
            chr(0x0418): chr(0x0418),
            chr(0x0419): chr(0x0419),
            chr(0x041A): chr(0x041A),
            chr(0x041B): chr(0x041B),
            chr(0x041C): chr(0x041C),
            chr(0x041D): chr(0x041D),
            chr(0x041E): chr(0x041E),
            chr(0x041F): chr(0x041F),
            chr(0x0420): chr(0x0420),
            chr(0x0421): chr(0x0421),
            chr(0x0422): chr(0x0422),
            chr(0x0423): chr(0x0423),
            chr(0x0424): chr(0x0424),
            chr(0x0425): chr(0x0425),
            chr(0x0426): chr(0x0426),
            chr(0x0427): chr(0x0427),
            chr(0x0428): chr(0x0428),
            chr(0x0429): chr(0x0429),
            chr(0x042A): chr(0x042A),
            chr(0x042B): chr(0x042B),
            chr(0x042C): chr(0x042C),
            chr(0x042D): chr(0x042D),
            chr(0x042E): chr(0x042E),
            chr(0x042F): chr(0x042F),
            chr(0x0430): chr(0x0410),
            chr(0x0431): chr(0x0411),
            chr(0x0432): chr(0x0412),
            chr(0x0433): chr(0x0413),
            chr(0x0434): chr(0x0414),
            chr(0x0435): chr(0x0415),
            chr(0x0436): chr(0x0416),
            chr(0x0437): chr(0x0417),
            chr(0x0438): chr(0x0418),
            chr(0x0439): chr(0x0419),
            chr(0x043A): chr(0x041A),
            chr(0x043B): chr(0x041B),
            chr(0x043C): chr(0x041C),
            chr(0x043D): chr(0x041D),
            chr(0x043E): chr(0x041E),
            chr(0x043F): chr(0x041F),
            chr(0x0440): chr(0x0420),
            chr(0x0441): chr(0x0421),
            chr(0x0442): chr(0x0422),
            chr(0x0443): chr(0x0423),
            chr(0x0444): chr(0x0424),
            chr(0x0445): chr(0x0425),
            chr(0x0446): chr(0x0426),
            chr(0x0447): chr(0x0427),
            chr(0x0448): chr(0x0428),
            chr(0x0449): chr(0x0429),
            chr(0x044A): chr(0x042A),
            chr(0x044B): chr(0x042B),
            chr(0x044C): chr(0x042C),
            chr(0x044D): chr(0x042D),
            chr(0x044E): chr(0x042E),
            chr(0x044F): chr(0x042F)
        }
        return result

    def parse(self, text: str) -> None:
        """
        Parse the text for the uppercase table.

        :param text: Text to parse
        :return: None
        """

        parts = re.findall(r'\d+', text)
        if not parts:
            # Попалась пустая таблица
            return

        assert len(parts) == 256
        first = bytearray(int(x) for x in parts if x and x.isdigit())
        first = first.replace(b'\x98', b'\x20')  # Этот символ не мапится
        first_chars = list(first.decode(ANSI))
        second = bytearray(x for x in range(256))
        second = second.replace(b'\x98', b'\x20')  # Этот символ не мапится
        second_chars = list(second.decode(ANSI))
        for upper, lower in zip(first_chars, second_chars):
            self.mapping[lower] = upper

    def upper(self, text: str) -> str:
        """
        Convert the text to uppercase according the table.

        :param text: Text to convert
        :return: Converted text
        """
        result = []
        for char in text:
            if char in self.mapping:
                result.append(self.mapping[char])
            else:
                result.append(char)
        return ''.join(result)


def load_uppercase_table(filename: str) -> UpperCaseTable:
    """
    Load the uppercase table from the specified file.

    :param filename: Name of the file
    :return: Uppercase table
    """
    with open(filename, 'rt', encoding=ANSI) as stream:
        text = stream.read()
    result = UpperCaseTable()
    result.parse(text)
    return result


def read_uppercase_table(connection: Connection,
                         specification: Optional[FileSpecification] = None) -> UpperCaseTable:
    """
    Чтение таблицы преобразования в верхний регистр с сервера.

    :param connection: Подключение
    :param specification: Спецификация
    :return: Таблица
    """

    assert connection and isinstance(connection, Connection)

    if specification is None:
        specification = FileSpecification(SYSTEM, None, UpperCaseTable.FILENAME)

    with connection.read_text_stream(specification) as response:
        text = response.ansi_remaining_text()
        if text:
            result = UpperCaseTable()
            result.parse(text)
        else:
            result = UpperCaseTable.get_default()
        return result


Connection.read_uppercase_table = read_uppercase_table  # type: ignore


###############################################################################


class IrbisFileNotFoundError(IrbisError):
    __slots__ = ('filename',)

    def __init__(self, filename: Union[str, FileSpecification]) -> None:
        self.filename: str = str(filename)

    def __str__(self):
        return f'File not found: {self.filename}'


def require_alphabet_table(connection: Connection,
                           specification: Optional[FileSpecification] = None) -> AlphabetTable:
    """
    Чтение алфавитной таблицы с сервера.

    :param connection: Подключение
    :param specification: Спецификация
    :return: Таблица
    """

    assert connection and isinstance(connection, Connection)

    if specification is None:
        specification = FileSpecification(SYSTEM, None, AlphabetTable.FILENAME)

    with connection.read_text_stream(specification) as response:
        text = response.ansi_remaining_text()
        if not text:
            raise IrbisFileNotFoundError(specification)
        if text:
            result = AlphabetTable()
            result.parse(text)
        else:
            result = AlphabetTable.get_default()
        return result


Connection.require_alphabet_table = require_alphabet_table  # type: ignore


def require_menu(connection: Connection,
                 specification: Union[FileSpecification, str]) -> MenuFile:
    """
    Чтение меню с сервера.

    :param connection: Подключение
    :param specification: Спецификация файла
    :return: Меню
    """
    assert connection and isinstance(connection, Connection)

    with connection.read_text_stream(specification) as response:
        result = MenuFile()
        text = irbis_to_lines(response.ansi_remaining_text())
        if not text:
            raise IrbisFileNotFoundError(specification)
        result.parse(text)
        return result


Connection.require_menu = require_menu  # type: ignore


def require_opt_file(connection: Connection,
                     specification: Union[FileSpecification, str]) -> OptFile:
    """
    Получение файла оптимизации рабочих листов с сервера.

    :param connection: Подключение
    :param specification: Спецификация
    :return: Файл оптимизации
    """
    assert connection and isinstance(connection, Connection)

    with connection.read_text_stream(specification) as response:
        result = OptFile()
        text = irbis_to_lines(response.ansi_remaining_text())
        if not text:
            raise IrbisFileNotFoundError(specification)
        result.parse(text)
        return result


Connection.require_opt_file = require_opt_file  # type: ignore


def require_par_file(connection: Connection,
                     specification: Union[FileSpecification, str]) -> ParFile:
    """
    Получение PAR-файла с сервера.

    :param connection: Подключение
    :param specification: Спецификация или имя файла (если он лежит в папке DATA)
    :return: Полученный файл
    """
    assert connection and isinstance(connection, Connection)

    if isinstance(specification, str):
        specification = FileSpecification(DATA, None, specification)

    with connection.read_text_stream(specification) as response:
        result = ParFile()
        text = irbis_to_lines(response.ansi_remaining_text())
        if not text:
            raise IrbisFileNotFoundError(specification)
        result.parse(text)
        return result


Connection.require_par_file = require_par_file  # type: ignore


def require_text_file(connection: Connection, specification: FileSpecification) -> str:
    """
    Чтение текстового файла с сервера.

    :param connection: Подключение
    :param specification: Спецификация
    :return: Содержимое файла
    """

    assert connection and isinstance(connection, Connection)

    result = connection.read_text_file(specification)
    if not result:
        raise IrbisFileNotFoundError(specification)

    return result


Connection.require_text_file = require_text_file  # type: ignore


def require_tree_file(connection: Connection,
                      specification: Union[FileSpecification, str]) -> TreeFile:
    """
    Чтение TRE-файла с сервера.

    :param connection: Подключение
    :param specification:  Спецификация
    :return: Дерево
    """

    assert connection and isinstance(connection, Connection)

    with connection.read_text_stream(specification) as response:
        text = response.ansi_remaining_text()
        if not text:
            raise IrbisFileNotFoundError(specification)
        text = [line for line in irbis_to_lines(text) if line]
        result = TreeFile()
        result.parse(text)
        return result


Connection.require_tree_file = require_tree_file  # type: ignore


###############################################################################

class Resource:
    """
    Текстовый файл на сервере.
    """

    __slots__ = ('name', 'content')

    def __init__(self, name: str, content: str) -> None:
        self.name: str = name
        self.content: str = content

    def __str__(self) -> str:
        return f"{self.name}: {self.content}"


class ResourceDictionary:
    """
    Словарь текстовых ресурсов.
    """

    __slots__ = ('dictionary',)

    def __init__(self) -> None:
        self.dictionary: Dict[str, Resource] = {}

    def add(self, name: str, content: str) -> 'ResourceDictionary':
        """
        Регистрация ресурса в словаре.
        :param name: Имя
        :param content: Содержимое
        :return: Словарь
        """
        self.dictionary[name] = Resource(name, content)
        return self

    def all(self) -> List[Resource]:
        """
        Все зарегистрированные ресурсы в виде массива.
        :return: Массив
        """
        result = []
        for item in self.dictionary.values():
            result.append(item)
        return result

    def clear(self) -> 'ResourceDictionary':
        """
        Очистка словаря.
        :return: Словарь
        """
        self.dictionary.clear()
        return self

    def count(self) -> int:
        """
        Вычисление длины словаря.
        :return: Число хранимых ресурсов
        """
        return len(self.dictionary)

    def get(self, name: str) -> Optional[str]:
        """
        Получение ресурса из словаря по имени.
        :param name: Имя
        :return: Содержимое ресурса либо None
        """
        if name in self.dictionary:
            return self.dictionary[name].content
        return None

    def have(self, name: str) -> bool:
        """
        Есть ли элемент с указанным именем в словаре?
        :param name: Имя
        :return: Наличие в словаре
        """
        return name in self.dictionary

    def put(self, name: str, content: str) -> 'ResourceDictionary':
        """
        Добавление ресурса в словарь.
        :param name: Имя
        :param content: Содержимое
        :return: Словарь
        """
        self.dictionary[name] = Resource(name, content)
        return self

    def remove(self, name: str) -> 'ResourceDictionary':
        """
        Удаление ресурса из словаря.
        :param name: Имя
        :return: Словарь
        """
        del self.dictionary[name]
        return self


###############################################################################


__all__ = ['MenuEntry', 'MenuFile', 'load_menu', 'ParFile', 'load_par_file',
           'TermPosting', 'TermInfo', 'TermParameters', 'PostingParameters',
           'TreeNode', 'TreeFile', 'load_tree_file', 'SearchScenario',
           'UserInfo', 'OptLine', 'OptFile', 'load_opt_file', 'ClientInfo',
           'ServerStat', 'DatabaseInfo', 'TableDefinition', 'AlphabetTable',
           'load_alphabet_table', 'UpperCaseTable', 'load_uppercase_table',
           'IrbisFileNotFoundError', 'Resource', 'ResourceDictionary']

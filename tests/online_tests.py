import unittest

from pyirbis.ext import *


class TestConnect(unittest.TestCase):

    def setUp(self):
        self.connection: IrbisConnection = IrbisConnection()
        self.connection.parse_connection_string('host=127.0.0.1;port=6666;user=1;password=1;db=ISTU;arm=A;')
        self.connection.connect()

    def tearDown(self):
        self.connection.disconnect()
        self.connection = None

    def test_01_simple_connection(self):
        print('Connection')
        print('Server version:', self.connection.server_version)
        print('Connected:', bool(self.connection))
        print(self.connection.ini_file['MAIN']['STTMNU'])

    def test_02_nop(self):
        self.connection.nop()
        print('NOP')

    def test_03_push_database(self):
        saved = self.connection.push_database('IBIS')
        self.assertEqual(saved, 'ISTU')
        self.assertEqual(self.connection.database, 'IBIS')
        saved = self.connection.pop_database()
        self.assertEqual(saved, 'IBIS')
        self.assertEqual(self.connection.database, 'ISTU')
        print('Push database')

    def test_04_get_max_mfn(self):
        max_mfn = self.connection.get_max_mfn()
        print('MaxMFN(ISTU)=', max_mfn, sep='')
        max_mfn = self.connection.get_max_mfn('IBIS')
        print('MaxMFN(IBIS)=', max_mfn, sep='')

    def test_05_update_ini_file(self):
        lines = ['[TEST]', 'FIRST=01', 'SECOND=02', 'THIRD=03']
        self.connection.update_ini_file(lines)
        print('Update INI file')

    def test_06_read_record(self):
        record = self.connection.read_record(1)
        print()
        print('Read record:')
        print(record.fm(200, 'a'))
        print(record)
        print()

    def test_07_read_text_file(self):
        text = self.connection.read_text_file('dn.mnu')
        print()
        print('Read text file')
        print(text)
        print()

    def test_08_unlock_records(self):
        self.connection.unlock_records([1, 2, 3])
        print('Unlock records')

    def test_09_search(self):
        found = self.connection.search('K=бетон')
        print('Search')
        print(found)
        print()

    def test_10_format_record(self):
        text = self.connection.format_record(BRIEF, 1)
        print('Format record')
        print(text)
        print()

    def test_11_get_server_version(self):
        version = self.connection.get_server_version()
        print('Server version')
        print(version)
        print()

    def test_12_list_files(self):
        found = self.connection.list_files('*.xlt', '*.ini')
        print('List files')
        print(found)
        print()

    def test_13_to_connection_string(self):
        cs = self.connection.to_connection_string()
        print('Connection string')
        print(cs)
        print()

    def test_14_write_record(self):
        record = MarcRecord()
        record.add(200, SubField('a', 'Сгенерированная запись'))
        record.add(300, 'Комментарий')
        record.add(700, SubField('a', 'Пайтон'), SubField('b', 'М.'),
                   SubField('g', 'Монти'))
        record.add(910, SubField('a', '0'), SubField('b', '1'),
                   SubField('c', '?'), SubField('d', 'ФКХ'))
        print('Write record')
        max_mfn = self.connection.write_record(record)
        print('New max MFN=', max_mfn, sep='')
        print(record)
        print()

    def test_15_write_text_file(self):
        specification = self.connection.near_master('no_such_file.txt')
        specification.content = 'No such file'
        self.connection.write_text_file(specification)
        print('Write text file')

    def test_16_read_menu(self):
        menu = self.connection.read_menu('stamp.mnu')
        print('Read menu')
        print(menu['1'])
        for item in menu:
            print(item)
        print()

    def test_16_read_par_file(self):
        par = self.connection.read_par_file('istu.par')
        print('Read PAR file')
        print(par)
        print()

    def test_17_read_terms(self):
        terms = self.connection.read_terms('K=БЕТОН')
        print('Read terms and postings')
        for term in terms:
            print(term)
            postings = self.connection.read_postings(term.text, 'v200^a')
            for posting in postings:
                print('\t', posting)

    def test_18_read_tree_file(self):
        tree = self.connection.read_tree_file('ii.tre')
        print('Read tree')
        print(tree)
        print()

    def test_19_read_ini_file(self):
        ini = self.connection.read_ini_file('istu.ini')
        print('Read INI file')
        for section in ini:
            print('Section:', section.name)
        print('ItemNumb=', ini['SEARCH']['ItemNumb'], sep='')
        print()

    def test_20_get_user_list(self):
        users = self.connection.get_user_list()
        print('Get user list')
        for user in users:
            print(user)
        print()

    def test_21_list_processes(self):
        processes = self.connection.list_processes()
        print('List processes')
        print(len(processes))
        for process in processes:
            print(process)
            print()
        print()

    def test_22_read_opt_file(self):
        opt = self.connection.read_opt_file('WS31.OPT')
        print('Read OPT')
        resolved = opt.resolve_worksheet('HELLO')
        print(resolved)
        print(opt)
        print()

    def test_23_read_search_scenario(self):
        scenarios = self.connection.read_search_scenario('istu.ini')
        print('Read search scenario')
        for scenario in scenarios:
            print(scenario)
        print()

    def test_24_get_server_stat(self):
        stat = self.connection.get_server_stat()
        print('Get server stat')
        print(stat)
        for x in stat.running_clients:
            print(x)
        print()

    def test_25_get_database_info(self):
        info = self.connection.get_database_info()
        print('Get database info')
        print(info, info.max_mfn)
        print()

    def test_26_print_table(self):
        definition = TableDefinition()
        definition.table = "@tabf1w"
        definition.search = "K=молоко"
        text = self.connection.print_table(definition)
        print('Print table')
        print(text)
        print()

    def test_27_read_alphabet_table(self):
        table = self.connection.read_alphabet_table()
        print('Read alphabet table')
        print(table.split_words('Не слышны в саду даже шорохи!'))
        print(table.split_words('Quick brown fox jumps over the lazy dog?'))
        print(table.trim('___Удаление лишних символов!!!'))
        print()

    def test_28_read_uppercase_table(self):
        table = self.connection.read_uppercase_table()
        print('Read uppercase table')
        print(table.upper('Не слышны в саду даже шорохи!'))
        print(table.upper('Quick brown fox jumps over the lazy dog?'))
        print()

    def test_29_read_search_scenario(self):
        specification = self.connection.near_master('istu.ini')
        scenarios = self.connection.read_search_scenario(specification)
        print('Read search scenario')
        print(len(scenarios))
        for scenario in scenarios:
            print(scenario)
        print()

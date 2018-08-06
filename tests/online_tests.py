import unittest

from pyirbis import *


class TestConnect(unittest.TestCase):

    def setUp(self):
        self.connection: IrbisConnection = IrbisConnection()
        self.connection.parse_connection_string('host=127.0.0.1;port=6666;user=1;password=1;db=ISTU;arm=A;')
        self.connection.connect()

    def tearDown(self):
        self.connection.disconnect()
        self.connection = None

    def test_01_simple_connection(self):
        print('Simple connection')
        print('Server version:', self.connection.server_version)

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

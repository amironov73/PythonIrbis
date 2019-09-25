# coding: utf-8

"""
Tests that requires the IRBIS server connection.
"""

import unittest
import time

from irbis import Connection, SubField, Record, FileSpecification, BRIEF


class TestConnect(unittest.TestCase):

    def setUp(self):
        self.connection: Connection = Connection()
        self.connection.parse_connection_string \
            ('host=192.168.7.13;port=6666;user=librarian;' +
             'password=secret;db=ISTU;arm=A;')
        self.connection.connect()

    def tearDown(self):
        self.connection.disconnect()
        self.connection = None

    @staticmethod
    def wait_for_a_while():
        print('Waiting')
        for _ in range(5):
            time.sleep(1)
            print('.', end='')
        print()

    def test_01_simple_connection(self):
        print('Connection')
        print('Server version:', self.connection.server_version)
        print('Connected:', bool(self.connection))
        print(self.connection.ini_file['MAIN']['DBNNAMECAT'])

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


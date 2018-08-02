import unittest

from pyirbis import *


class TestConnect(unittest.TestCase):

    def test_connection(self):
        connection = IrbisConnection()
        connection.host = '127.0.0.1'
        connection.port = 6666
        connection.username = '1'
        connection.password = '1'
        connection.database = 'ISTU'
        connection.workstation = 'C'
        connection.connect()
        print('Connected')

        version = connection.get_server_version()
        print(version)

        # processes = connection.list_processes()
        # for process in processes:
        #     print(process)
        #     print()

        par = connection.read_par('istu.par')
        print()
        print(par)
        print()

        # opt = connection.read_opt('WS31.OPT')
        # print()
        # print(opt)
        # print()
        # resolved = opt.resolve_worksheet('HELLO')
        # print(resolved)
        # print()

        # menu = connection.read_menu('stamp.mnu')
        # print()
        # print(menu)
        # print()

        # max_mfn = connection.get_max_mfn()
        # print('Max MFN:', max_mfn)

        # connection.nop()
        # print('Nop')

        # record = connection.read_record(1)
        # print(record)
        # print()
        # print(record.fm(200, 'a'))

        # terms = connection.read_terms('K=БЕТОН')
        # for term in terms:
        #     print(term)

        # parameters = TermParameters('K=БЕТОН')
        # terms = connection.read_terms(parameters)
        # for term in terms:
        #     print(term)

        # found = connection.search('K=бетон')
        # print(found)

        # for mfn in found:
        #     line = connection.format_record("@sbrief", mfn)
        #     print(line)

        connection.disconnect()
        print('Disconnected')


if __name__ == '__main__':
    unittest.main()

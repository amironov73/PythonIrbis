import unittest

from pyirbis import *


class TestConnect(unittest.TestCase):

    def test_connection(self):
        connection = IrbisConnection()
        connection.parse_connection_string('host=127.0.0.1;port=6666;user=1;password=1;db=ISTU;arm=A;')
        # connection.host = '127.0.0.1'
        # connection.port = 6666
        # connection.username = '1'
        # connection.password = '1'
        # connection.database = 'ISTU'
        # connection.workstation = 'C'
        connection.connect()
        print('Connected')

        version = connection.get_server_version()
        print(version)

        # definition = TableDefinition()
        # definition.search = "К=молоко"
        # text = connection.print_table(definition)
        # print()
        # print(text)
        # print()

        # processes = connection.list_processes()
        # print()
        # print(len(processes))
        # for process in processes:
        #     print(process)
        #     print()
        # print()
        #
        # users = connection.get_user_list()
        # print()
        # for user in users:
        #     print(user)
        # print()

        # stat = connection.get_server_stat()
        # print()
        # print(stat)
        # for x in stat.running_clients:
        #     print(x)
        # print()

        # info = connection.get_database_info()
        # print()
        # print(info, info.max_mfn)
        # print()

        # par = connection.read_par('istu.par')
        # print()
        # print(par)
        # print()

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
        #     postings = connection.read_postings(term.text, 'v200^a')
        #     for posting in postings:
        #         print('\t', posting)

        # parameters = TermParameters('K=БЕТОН')
        # terms = connection.read_terms(parameters)
        # for term in terms:
        #     print(term)

        # found = connection.search('K=бетон')
        # print(found)

        # for mfn in found:
        #     line = connection.format_record("@sbrief", mfn)
        #     print(line)

        # record = MarcRecord()
        # record.add(200, SubField('a', 'Сгенерированная запись'))
        # record.add(300, 'Комментарий')
        # record.add(700, SubField('a', 'Пайтон'), SubField('b', 'М.'),
        #            SubField('g', 'Монти'))
        # record.add(910, SubField('a', '0'), SubField('b', '1'),
        #            SubField('c', '?'), SubField('d', 'ФКХ'))
        # print()
        # print(record)
        # connection.write_record(record)
        # print()
        # print(record)
        # print()

        specification = FileSpecification(MASTER_FILE, 'IBIS', 'no_such_file.txt')
        specification.content = 'No such file'
        connection.write_text_file(specification)

        connection.disconnect()
        print('Disconnected')


if __name__ == '__main__':
    unittest.main()

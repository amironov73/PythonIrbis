import unittest
from pyirbis.IrbisConnection import IrbisConnection
from pyirbis.TermParameters import TermParameters
from pyirbis.SearchParameters import SearchParameters


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
        max_mfn = connection.get_max_mfn()
        print('Max MFN:', max_mfn)
        connection.nop()
        print('Nop')

        parameters = TermParameters('К=БЕТОН')
        terms = connection.read_terms(parameters)
        for term in terms:
            print(term)

        parameters = SearchParameters()
        parameters.expression = "K=бетон"
        found = connection.search(parameters)
        print(found)

        for mfn in found:
            line = connection.format_record("@sbrief", mfn)
            print(line)

        connection.disconnect()
        print('Disconnected')


if __name__ == '__main__':
    unittest.main()

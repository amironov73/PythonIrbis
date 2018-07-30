import unittest
from pyirbis.IrbisConnection import IrbisConnection


class TestConnect(unittest.TestCase):
    connection = IrbisConnection()
    connection.host = '127.0.0.1'
    connection.port = 6666
    connection.username = '1'
    connection.password = '1'
    connection.workstation = 'C'
    connection.connect()
    connection.disconnect()
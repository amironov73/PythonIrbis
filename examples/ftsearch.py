# coding: utf-8

"""
Простая программа, демонстрирующая полнотекстовый поиск,
появившийся в ИРБИС64+ (проще говоря, в ИРБИС 2018.1).
"""

import sys

from irbis import Connection, SearchParameters, TextParameters

if len(sys.argv) < 4:
    print('Usage: ftsearch <connection-string> <search query> <fulltext words>')
    exit(-1)

with Connection() as connection:
    try:
        connection.parse_connection_string(sys.argv[1])
        connection.connect()

        if not connection.connected:
            print("Can't connect")
            exit(-1)

        search = SearchParameters()
        fulltext = TextParameters()
        search.database = connection.database
        search.expression = sys.argv[2]
        fulltext.request = ' '.join(sys.argv[3:])

        found = connection.fulltext_search(search, fulltext)
        print('Найдено: ', len(found))

    except Exception as ex:
        print("Exception occurred:", type(ex))
        print(ex)
        exit(-1)

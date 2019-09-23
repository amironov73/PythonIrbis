# coding: utf-8

"""
Простая программа, проверяющая возможность доступа
к конкретному серверу ИРБИС и конкретной базе данных.

В случае успеха выходит с кодом 0.
Любой другой код -- что-то пошло не так.
"""

import sys

# import os
# parent_dir = os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..'))
# sys.path.append(parent_dir)

from irbis import Connection

if len(sys.argv) != 2:
    print('Usage: irbis_ping <connection-string>')
    exit(-1)

with Connection() as connection:
    try:
        connection.parse_connection_string(sys.argv[1])
        connection.connect()

        if not connection.connected:
            print("Can't connect")
            exit(-1)

        max_mfn = connection.get_max_mfn()
        print("MAX MFN=", str(max_mfn), sep='')

        if max_mfn < 1:
            exit(-1)

    except Exception as ex:
        print("Exception occurred:", type(ex))
        print(ex)
        exit(-1)

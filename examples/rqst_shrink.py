# coding: utf-8

"""
Простая программа, удаляющая из базы данных RQST
все выполненные заказы (для уменьшения нагрузки
на сеть и сервер со стороны АРМ "Книговыдачи").
"""

import sys
from datetime import datetime
import irbis

if len(sys.argv) != 2:
    print('Usage: irbis_ping <connection-string>')
    exit(-1)

start = datetime.now()

with irbis.Connection(connection_string=sys.argv[1]) as connection:
    try:
        if not connection.connected:
            print("Can't connect")
            exit(-1)

        if connection.workstation != irbis.ADMINISTRATOR:
            print("Not administrator! Exiting")
            exit(-1)

        max_mfn = connection.get_max_mfn()
        if max_mfn < 1:
            print(f"Max MFN={max_mfn}, exiting")
            exit(-1)

        # Невыполненные и зарезервированные заказы
        expression = '"I=0" + "I=2"'
        found = connection.search(expression)
        if len(found) == max_mfn:
            print("No truncation needed, exiting")
            exit(-1)

        good_records = connection.read_records(*found)
        print("Good records loaded:", len(good_records))

        # Ресетим записи
        for record in good_records:
            record.reset()
            record.database = connection.database

        connection.truncate_database(connection.database)
        if connection.get_max_mfn(connection.database) > 1:
            print("Error while truncating the database, exiting")
            exit(-1)

        connection.write_records(good_records)
        print("Good records restored")

    except Exception as ex:
        print("Exception occurred:", type(ex))
        print(ex)
        exit(-1)

elapsed = datetime.now() - start
print(f"Elapsed time: {elapsed}")

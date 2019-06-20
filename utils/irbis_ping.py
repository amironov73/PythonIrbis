# coding: utf-8

import sys
import os

parent_dir = os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..'))
sys.path.append(parent_dir)
# print(sys.path)

from irbis.core import Connection

if len(sys.argv) != 2:
    print('Usage: irbis_ping <connection-string>')
    exit(-1)

with Connection() as connection:
    try:
        connection.parse_connection_string(sys.argv[1])
        connection.connect()
        max_mfn = connection.get_max_mfn()
        print("MAX MFN=", str(max_mfn), sep='')
    except Exception as ex:
        print(ex)
        exit(-1)

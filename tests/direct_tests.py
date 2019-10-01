# coding: utf-8

"""
Direct database access test.
"""

import os
import os.path

from irbis.direct import DirectAccess


#############################################################################


def script_path() -> str:
    return os.path.dirname(os.path.realpath(__file__))


def relative_path(filename: str) -> str:
    return os.path.realpath(os.path.join(script_path(), filename))


def ibis_file(filename: str) -> str:
    return relative_path('data/irbis64/datai/ibis/' + filename)


#############################################################################


master_file_name = ibis_file('ibis.mst')

with DirectAccess(master_file_name) as access:
    def show_record(mfn: int):
        record = access.read_record(mfn)
        print(record)
        print('=' * 78)
        print()

    print(f"{access}")
    print()
    show_record(1)
    show_record(2)
    show_record(321)

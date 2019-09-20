# coding: utf-8

"""
Tests that doesn't require the IRBIS server connection.
"""

import random
import os
import os.path
import unittest
from sys import platform

from irbis import *

#############################################################################


def script_path():
    return os.path.dirname(os.path.realpath(__file__))


def relative_path(filename: str):
    return os.path.realpath(os.path.join(script_path(), filename))


def random_text_file():
    import tempfile
    result = tempfile.NamedTemporaryFile(mode='wt', encoding='utf-8', delete=False)
    return result


def random_binary_file():
    import tempfile
    result = tempfile.NamedTemporaryFile(mode='wb', delete=False)
    return result


def random_file_name():
    if platform == 'linux':
        tempdir = '/tmp'
    elif platform == 'darwin':
        tempdir = '/tmp'  # ???
    elif platform == 'win32':
        tempdir = os.environ['TMP']
    else:
        raise Exception('Unknown system')
    filename = str(random.randint(1111111, 9999999))
    result = os.path.join(tempdir, filename)
    return result


#############################################################################


class TestSubField(unittest.TestCase):

    def test_init_1(self):
        sf = SubField()
        self.assertEqual(sf.code, SubField.DEFAULT_CODE)
        self.assertIsNone(sf.value)

    def test_init_2(self):
        sf = SubField('a')
        self.assertEqual(sf.code, 'a')
        self.assertIsNone(sf.value)

    def test_init_3(self):
        sf = SubField('a', 'Some text')
        self.assertEqual(sf.code, 'a')
        self.assertEqual(sf.value, 'Some text')

    def test_clone_1(self):
        original = SubField('a', 'Some text')
        clone = original.clone()
        self.assertEqual(clone.code, original.code)
        self.assertEqual(clone.value, original.value)

    def test_str_1(self):
        sf = SubField('a', 'Some text')
        self.assertEqual(str(sf), '^aSome text')

    def test_str_2(self):
        sf = SubField('a')
        self.assertEqual(str(sf), '^a')

    def test_str_3(self):
        sf = SubField()
        self.assertEqual(str(sf), '')

    def test_assign_1(self):
        first = SubField('a', 'Some text')
        second = SubField('b', 'Other text')
        second.assign_from(first)
        self.assertEqual(first.code, second.code)
        self.assertEqual(first.value, second.value)

    def test_bool_1(self):
        sf = SubField('a', 'Some text')
        self.assertTrue(bool(sf))

    def test_bool_2(self):
        sf = SubField('a')
        self.assertFalse(bool(sf))

    def test_bool_3(self):
        sf = SubField()
        self.assertFalse(bool(sf))


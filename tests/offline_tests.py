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

#############################################################################


class TestField(unittest.TestCase):

    def test_init_1(self):
        field = Field()
        self.assertEqual(field.tag, Field.DEFAULT_TAG)
        self.assertIsNone(field.value)
        self.assertEqual(len(field.subfields), 0)

    def test_init_2(self):
        field = Field(100)
        self.assertEqual(field.tag, 100)
        self.assertIsNone(field.value)
        self.assertEqual(len(field.subfields), 0)

    def test_init_3(self):
        field = Field(100, 'Some value')
        self.assertEqual(field.tag, 100)
        self.assertEqual(field.value, 'Some value')
        self.assertEqual(len(field.subfields), 0)

    def test_init_4(self):
        field = Field(100, SubField('a', 'Some value'))
        self.assertEqual(field.tag, 100)
        self.assertIsNone(field.value)
        self.assertEqual(1, len(field.subfields))

    # def test_init_5(self):
    #     field = Field(100, SubField('a', 'Some value'), SubField('b', 'Other value'))
    #     self.assertEqual(field.tag, 100)
    #     self.assertIsNone(field.value)
    #     self.assertEqual(2, len(field.subfields))

    def test_add_1(self):
        field = Field()
        field.add('a', 'Some text')
        self.assertEqual(len(field.subfields), 1)
        self.assertEqual(field.subfields[0].code, 'a')
        self.assertEqual(field.subfields[0].value, 'Some text')

    def test_add_non_empty_1(self):
        field = Field()
        field.add_non_empty('a', None)
        self.assertEqual(len(field.subfields), 0)
        field.add_non_empty('a', '')
        self.assertEqual(len(field.subfields), 0)
        field.add_non_empty('a', 'Value')
        self.assertEqual(len(field.subfields), 1)

    def test_all_1(self):
        field = Field()
        field.add('a', 'A1').add('a', 'A2').add('b', 'B1')
        self.assertEqual(2, len(field.all('A')))
        self.assertEqual(1, len(field.all('B')))

    def test_all_values_1(self):
        field = Field()
        field.add('a', 'A1').add('a', 'A2').add('b', 'B1')
        self.assertEqual(2, len(field.all_values('A')))
        self.assertEqual(1, len(field.all_values('B')))

    def test_assign_from_1(self):
        first = Field(100, 'Some value').add('a', 'SubA')
        second = Field(200, 'Other value').add('b', 'SubB')
        second.assign_from(first)
        self.assertEqual(second.tag, 200)
        self.assertEqual(first.value, second.value)
        self.assertEqual(len(first.subfields), len(second.subfields))
        self.assertEqual(first.subfields[0].code, second.subfields[0].code)
        self.assertEqual(first.subfields[0].value, second.subfields[0].value)

    def test_clone_1(self):
        original = Field(100, 'Some value')
        original.add('a', 'Some text')
        clone = original.clone()
        self.assertEqual(original.tag, clone.tag)
        self.assertEqual(original.value, clone.value)
        self.assertEqual(len(original.subfields), len(clone.subfields))

    def test_clear_1(self):
        field = Field(100, 'Some value')
        field.add('a', 'Some text')
        field.clear()
        self.assertEqual(len(field.subfields), 0)

    def test_first_1(self):
        sf1 = SubField('a', 'First value')
        sf2 = SubField('b', 'Second value')
        field = Field(100)
        field.subfields.append(sf1)
        field.subfields.append(sf2)
        self.assertIs(field.first('a'), sf1)
        self.assertIs(field.first('b'), sf2)
        self.assertIsNone(field.first('c'))

    def test_first_value_1(self):
        sf1 = SubField('a', 'First value')
        sf2 = SubField('b', 'Second value')
        field = Field(100)
        field.subfields.append(sf1)
        field.subfields.append(sf2)
        self.assertEqual(field.first_value('a'), sf1.value)
        self.assertEqual(field.first_value('b'), sf2.value)
        self.assertIsNone(field.first_value('c'))

    def test_get_embedded_fields_1(self):
        field = Field(200)
        found = field.get_embedded_fields()
        self.assertEqual(len(found), 0)

    def test_get_embedded_fields_2(self):
        field = Field(461)
        field.add('a', 'SubA')
        field.add('1', '200#1')
        field.add('a', 'Златая цепь')
        field.add('e', 'Записки. Повести. Рассказы')
        field.add('f', 'Бондарин С. А.')
        field.add('v', 'С. 76-132')
        found = field.get_embedded_fields()
        self.assertEqual(len(found), 1)

    def test_str_1(self):
        field = Field(100, 'Some value')
        field.add('a', 'Some text')
        field.add('b', 'Other text')
        self.assertEqual(str(field), '100#Some value^aSome text^bOther text')

    def test_str_2(self):
        field = Field()
        self.assertEqual(str(field), '')

    def test_iter_1(self):
        field = Field(100).add('a', 'SubA').add('b', 'SubB')
        s = list(field)
        self.assertEqual(len(s), 2)
        self.assertEqual(s[0].code, field.subfields[0].code)
        self.assertEqual(s[0].value, field.subfields[0].value)
        self.assertEqual(s[1].code, field.subfields[1].code)
        self.assertEqual(s[1].value, field.subfields[1].value)

    def test_iter_2(self):
        field = Field()
        s = list(field)
        self.assertEqual(len(s), 0)

    def test_iter_3(self):
        field = Field(100).add('a', 'SubA').add('b', 'SubB')
        i = iter(field)
        sf = next(i)
        self.assertEqual(sf.code, 'a')
        self.assertEqual(sf.value, 'SubA')
        sf = next(i)
        self.assertEqual(sf.code, 'b')
        self.assertEqual(sf.value, 'SubB')
        ok = False
        try:
            next(i)
        except StopIteration:
            ok = True
        self.assertTrue(ok)

    def test_iadd_1(self):
        field = Field(100)
        self.assertEqual(len(field.subfields), 0)
        field += SubField('a', 'SubA')
        self.assertEqual(len(field.subfields), 1)
        field += SubField('b', 'SubB')
        self.assertEqual(len(field.subfields), 2)
        self.assertEqual(str(field), '100#^aSubA^bSubB')

    def test_iadd_2(self):
        field = Field(100)
        field += (SubField('a', 'SubA'), SubField('b', 'SubB'))
        self.assertEqual(len(field.subfields), 2)
        self.assertEqual(str(field), '100#^aSubA^bSubB')

    # noinspection DuplicatedCode
    def test_isub_1(self):
        sfa = SubField('a', 'SubA')
        sfb = SubField('b', 'SubB')
        field = Field(100)
        field.subfields.append(sfa)
        field.subfields.append(sfb)
        self.assertEqual(len(field.subfields), 2)
        field -= sfa
        self.assertEqual(len(field.subfields), 1)
        field -= sfa
        self.assertEqual(len(field.subfields), 1)
        field -= sfb
        self.assertEqual(len(field.subfields), 0)
        field -= sfb
        self.assertEqual(len(field.subfields), 0)

    def test_isub_2(self):
        sfa = SubField('a', 'SubA')
        sfb = SubField('b', 'SubB')
        field = Field(100)
        field.subfields.append(sfa)
        field.subfields.append(sfb)
        field -= (sfa, sfb)
        self.assertEqual(len(field.subfields), 0)
        field -= (sfa, sfb)
        self.assertEqual(len(field.subfields), 0)

    def test_getitem_1(self):
        sfa = SubField('a', 'SubA')
        sfb = SubField('b', 'SubB')
        field = Field(100)
        field.subfields.append(sfa)
        field.subfields.append(sfb)
        found = field['a']
        self.assertIs(found, sfa)
        found = field['b']
        self.assertIs(found, sfb)
        found = field['c']
        self.assertIsNone(found)

    def test_getitem_2(self):
        sfa = SubField('a', 'SubA')
        sfb = SubField('b', 'SubB')
        field = Field(100)
        field.subfields.append(sfa)
        field.subfields.append(sfb)
        found = field[0]
        self.assertIs(found, sfa)
        found = field[1]
        self.assertIs(found, sfb)

    def test_setitem_1(self):
        sfa = SubField('a', 'SubA')
        sfb = SubField('b', 'SubB')
        field = Field(100)
        field.subfields.append(sfa)
        field.subfields.append(sfb)
        new_value = 'New value'
        field['a'] = new_value
        self.assertEqual(sfa.value, new_value)
        field['b'] = new_value
        self.assertEqual(sfb.value, new_value)
        field['c'] = new_value
        self.assertEqual(len(field.subfields), 3)
        sfc = field.subfields[2]
        self.assertEqual(sfc.value, new_value)

    def test_setitem_2(self):
        sfa = SubField('a', 'SubA')
        sfb = SubField('b', 'SubB')
        field = Field(100)
        field.subfields.append(sfa)
        field.subfields.append(sfb)
        self.assertEqual(len(field.subfields), 2)
        field['a'] = None
        self.assertEqual(len(field.subfields), 1)
        field['b'] = None
        self.assertEqual(len(field.subfields), 0)
        field['c'] = None
        self.assertEqual(len(field.subfields), 0)

    def test_len_1(self):
        field = Field(100, SubField('a', 'SubA')).add('b', 'SubB')
        self.assertEqual(len(field), 2)

    def test_len_2(self):
        field = Field()
        self.assertEqual(len(field), 0)

    def test_bool_1(self):
        field = Field(100, SubField('a', 'SubA')).add('b', 'SubB')
        self.assertTrue(bool(field))

    def test_bool_2(self):
        field = Field(100, 'Value')
        self.assertTrue(bool(field))

    def test_bool_3(self):
        field = Field(100)
        self.assertFalse(bool(field))

    def test_bool_4(self):
        field = Field()
        field.value = 'Value'
        self.assertFalse(bool(field))

#############################################################################


class TestMarcRecord(unittest.TestCase):

    def test_init_1(self):
        record = Record()
        self.assertIsNone(record.database)
        self.assertEqual(record.mfn, 0)
        self.assertEqual(record.version, 0)
        self.assertEqual(record.status, 0)
        self.assertEqual(len(record.fields), 0)

    def test_init_2(self):
        f100 = Field(100, 'Field 100')
        f200 = Field(200, 'Field 200')
        record = Record(f100, f200)
        self.assertEqual(len(record.fields), 2)
        self.assertEqual(record.fields[0].tag, 100)
        self.assertEqual(record.fields[1].tag, 200)

    def test_add_1(self):
        record = Record()
        record.add(100, 'Some value')
        self.assertEqual(len(record.fields), 1)

    def test_add_2(self):
        record = Record()
        record.add(100).add('a', 'SubA').add('b', 'SubB')
        self.assertEqual(len(record.fields), 1)
        self.assertEqual(len(record.fields[0].subfields), 2)

    def test_all_1(self):
        record = Record()
        record.add(100, 'Field100')
        record.add(200, 'Field200')
        record.add(300, 'Field300/1')
        record.add(300, 'Field300/2')
        self.assertEqual(len(record.fields), 4)
        self.assertEqual(len(record.all(100)), 1)
        self.assertEqual(len(record.all(200)), 1)
        self.assertEqual(len(record.all(300)), 2)
        self.assertEqual(len(record.all(400)), 0)

    def test_clear_1(self):
        record = Record()
        record.add(100, 'Some value')
        record.clear()
        self.assertEqual(len(record.fields), 0)

    def test_clone_1(self):
        original = Record()
        original.add(100, 'Some value')
        original.database = 'IBIS'
        clone = original.clone()
        self.assertEqual(original.database, clone.database)
        self.assertEqual(original.mfn, clone.mfn)
        self.assertEqual(original.status, clone.status)
        self.assertEqual(original.version, clone.version)
        self.assertEqual(len(original.fields), len(clone.fields))

    def test_encode_1(self):
        record = Record()
        record.mfn = 123
        record.version = 321
        record.status = LAST
        record.add(100, 'Field100')
        record.add(200).add('a', 'SubA').add('b', 'SubB')
        self.assertEqual(record.encode(),
                         ['123#32', '0#321', '100#Field100',
                          '200#^aSubA^bSubB'])

    def test_fm_1(self):
        record = Record()
        record.add(100, 'Field 100')
        record.add(200, 'Field 200')
        self.assertEqual('Field 100', record.fm(100))
        self.assertEqual('Field 200', record.fm(200))
        self.assertIsNone(record.fm(300))

    def test_fm_2(self):
        record = Record()
        record.add(100).add('a', '100A').add('b', '100B')
        record.add(200).add('b', '200B').add('c', '200C')
        self.assertEqual('100A', record.fm(100, 'a'))
        self.assertEqual('100B', record.fm(100, 'b'))
        self.assertIsNone(record.fm(100, 'c'))
        self.assertIsNone(record.fm(200, 'a'))
        self.assertEqual('200B', record.fm(200, 'b'))
        self.assertEqual('200C', record.fm(200, 'c'))

    def test_fma_1(self):
        record = Record()
        record.add(100, 'Field 100/1')
        record.add(100, 'Field 100/2')
        record.add(200).add('a', 'SubA/1').add('b', 'SubB/1')
        record.add(200).add('a', 'SubA/2').add('b', 'SubB/2')
        self.assertEqual(record.fma(100), ['Field 100/1', 'Field 100/2'])
        self.assertEqual(record.fma(200, 'a'), ['SubA/1', 'SubA/2'])
        self.assertEqual(record.fma(200, 'b'), ['SubB/1', 'SubB/2'])
        self.assertEqual(record.fma(200, 'c'), [])
        self.assertEqual(record.fma(300), [])
        self.assertEqual(record.fma(300, 'a'), [])

    def test_is_deleted_1(self):
        record = Record()
        self.assertFalse(record.is_deleted())
        record.status = LOGICALLY_DELETED
        self.assertTrue(record.is_deleted())
        record.status = PHYSICALLY_DELETED
        self.assertTrue(record.is_deleted())
        record.status = LAST
        self.assertFalse(record.is_deleted())

    def test_record_parse_1(self):
        record = Record()
        text = ['123#32', '0#321', '100#Field 100', '200#^aSubA^bSubB']
        record.parse(text)
        self.assertEqual(len(record.fields), 2)
        self.assertEqual(record.mfn, 123)
        self.assertEqual(record.status, LAST)
        self.assertEqual(record.version, 321)
        self.assertEqual(record.fields[0].tag, 100)
        self.assertEqual(record.fields[0].value, 'Field 100')
        self.assertEqual(len(record.fields[0].subfields), 0)
        self.assertEqual(record.fields[1].tag, 200)
        self.assertIsNone(record.fields[1].value)
        self.assertEqual(len(record.fields[1].subfields), 2)
        self.assertEqual(record.fields[1].subfields[0].code, 'a')
        self.assertEqual(record.fields[1].subfields[0].value, 'SubA')
        self.assertEqual(record.fields[1].subfields[1].code, 'b')
        self.assertEqual(record.fields[1].subfields[1].value, 'SubB')

    def test_str_1(self):
        record = Record()
        record.add(100, 'Field 100')
        record.add(200, 'Field 200').add('a', 'Subfield A')
        self.assertEqual('100#Field 100\n200#Field 200^aSubfield A',
                         str(record))

    def test_iter_1(self):
        record = Record()
        record.add(100, 'Field 100')
        record.add(200).add('a', 'SubA').add('b', 'SubB')
        s = list(record)
        self.assertEqual(len(s), 2)
        self.assertEqual(s[0].tag, 100)
        self.assertEqual(s[1].tag, 200)

    def test_iter_2(self):
        record = Record()
        record.add(100, 'Field 100')
        record.add(200).add('a', 'SubA').add('b', 'SubB')
        i = iter(record)
        f = next(i)
        self.assertEqual(f.tag, 100)
        f = next(i)
        self.assertEqual(f.tag, 200)
        ok = False
        try:
            next(i)
        except StopIteration:
            ok = True
        self.assertTrue(ok)

    def test_iadd_1(self):
        record = Record()
        self.assertEqual(len(record.fields), 0)
        record += Field(100, 'Field 100')
        self.assertEqual(len(record.fields), 1)
        record += Field(200, SubField('a', 'SubA'))
        self.assertEqual(len(record.fields), 2)

    def test_iadd_2(self):
        record = Record()
        record += (Field(100, 'Field 100'), Field(200, 'Field 200'))
        self.assertEqual(len(record.fields), 2)

    def test_isub_1(self):
        f100 = Field(100, 'Field 100')
        f200 = Field(200, SubField('a', 'SubA'))
        record = Record(f100, f200)
        record -= (f100, f200)
        self.assertEqual(len(record.fields), 0)
        record -= (f100, f200)
        self.assertEqual(len(record.fields), 0)

    def test_isub_2(self):
        f100 = Field(100, 'Field 100')
        f200 = Field(200).add('a', 'SubA')
        record = Record(f100, f200)
        record -= f100
        self.assertEqual(len(record.fields), 1)
        record -= f100
        self.assertEqual(len(record.fields), 1)
        record -= f200
        self.assertEqual(len(record.fields), 0)
        record -= f200
        self.assertEqual(len(record.fields), 0)

    def test_getitem_1(self):
        record = Record()
        record.add(100, 'Field 100')
        field = Field(200).add('a', 'SubA').add('b', 'SubB')
        record.fields.append(field)
        self.assertEqual(record[100], 'Field 100')
        self.assertIsNone(record[200])
        self.assertIsNone(record[300])

    def test_setitem_1(self):
        f100 = Field(100, 'Field 100')
        f200 = Field(200).add('a', 'SubA').add('b', 'SubB')
        record = Record()
        record.fields.append(f100)
        record.fields.append(f200)
        new_value = 'New value'
        record[100] = new_value
        self.assertEqual(f100.value, new_value)
        record[200] = '^aNewA^bNewB'
        self.assertEqual(f200.subfields[0].value, 'NewA')
        self.assertEqual(f200.subfields[1].value, 'NewB')
        record[300] = new_value
        self.assertEqual(len(record.fields), 3)
        self.assertEqual(record.fields[2].tag, 300)
        self.assertEqual(record.fields[2].value, new_value)
        record[400] = Field().add('a', 'NewA').add('b', 'NewB')
        self.assertEqual(len(record.fields), 4)
        self.assertEqual(record.fields[3].tag, 400)
        self.assertEqual(record.fields[3].subfields[0].value, 'NewA')
        self.assertEqual(record.fields[3].subfields[1].value, 'NewB')
        record[300] = SubField('a', 'OtherA')
        self.assertEqual(len(record.fields), 4)
        self.assertEqual(record.fields[2].tag, 300)
        self.assertIsNone(record.fields[2].value)
        self.assertEqual(record.fields[2].subfields[0].value, 'OtherA')

    def test_setitem_2(self):
        f100 = Field(100, 'Field 100')
        f200 = Field(200).add('a', 'SubA').add('b', 'SubB')
        record = Record()
        record.fields.append(f100)
        record.fields.append(f200)
        self.assertEqual(len(record.fields), 2)
        record[100] = None
        self.assertEqual(len(record.fields), 1)
        record[200] = None
        self.assertEqual(len(record.fields), 0)

    def test_len_1(self):
        record = Record()
        self.assertEqual(len(record), 0)
        record.add(100, 'Field 100')
        self.assertEqual(len(record), 1)
        record.add(200, 'Field 200')
        self.assertEqual(len(record), 2)

    def test_bool_1(self):
        record = Record()
        self.assertFalse(bool(record))
        record.add(100, 'Field 100')
        self.assertTrue(bool(record))

#############################################################################

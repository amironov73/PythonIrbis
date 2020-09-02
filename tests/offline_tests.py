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
from irbis._common import same_string, safe_str, safe_int, irbis_to_dos, \
    irbis_to_lines, short_irbis_to_lines
from irbis.builder import author, bbk, document_kind, keyword, language, \
    magazine, mhr, number, place, publisher, rzn, Search, subject, title, \
    udc, year

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


class TestCommon(unittest.TestCase):

    def test_same_string_1(self):
        self.assertFalse(same_string(None, None))
        self.assertFalse(same_string(None, ''))
        self.assertTrue(same_string('', ''))
        self.assertTrue(same_string('Hello', 'hello'))
        self.assertFalse(same_string('Hello', 'hell'))

    def test_safe_str_1(self):
        self.assertEqual(safe_str(None), '')
        self.assertEqual(safe_str(''), '')
        self.assertEqual(safe_str('Hello'), 'Hello')
        self.assertEqual(safe_str(1), '1')

    def test_safe_int_1(self):
        self.assertEqual(safe_int(''), 0)
        self.assertEqual(safe_int('Hello'), 0)
        self.assertEqual(safe_int('123'), 123)
        self.assertEqual(safe_int('-123'), -123)

    def test_irbis_to_dos_1(self):
        self.assertEqual(irbis_to_dos('123\x1F\x1E456'), '123\n456')
        self.assertEqual(irbis_to_dos('123456'), '123456')

    def test_irbis_to_lines_1(self):
        self.assertEqual(irbis_to_lines('123\x1F\x1E456'), ['123', '456'])
        self.assertEqual(irbis_to_lines('123456'), ['123456'])

    def test_short_irbis_to_lines_1(self):
        self.assertEqual(short_irbis_to_lines('123\x1E456'), ['123', '456'])
        self.assertEqual(short_irbis_to_lines('123456'), ['123456'])


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

    def test_add_duplicate_1(self):
        field = Field()
        field.add('a', 'Some text')
        subfield = SubField('a', 'Some text')
        self.assertIn(subfield, field.subfields)
        self.assertRaises(ValueError, field.add, 'a', 'Some text')

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
        self.assertEqual(s[0][0], field.subfields[0].code)
        self.assertEqual(s[0][1], field.subfields[0].value)
        self.assertEqual(s[1][0], field.subfields[1].code)
        self.assertEqual(s[1][1], field.subfields[1].value)

    def test_iter_2(self):
        field = Field()
        s = list(field)
        self.assertEqual(len(s), 1)
        self.assertEqual(s[0][0], '')
        self.assertIsNone(s[0][1])

    def test_iter_3(self):
        field = Field(100).add('a', 'SubA').add('b', 'SubB')
        i = iter(field)
        sf = next(i)
        self.assertEqual(sf[0], 'a')
        self.assertEqual(sf[1], 'SubA')
        sf = next(i)
        self.assertEqual(sf[0], 'b')
        self.assertEqual(sf[1], 'SubB')
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
        self.assertEqual(found, 'SubA')
        found = field['b']
        self.assertEqual(found, 'SubB')
        found = field['c']
        self.assertEqual(found, '')

    def test_getitem_2(self):
        sfa = SubField('a', 'SubA')
        sfb = SubField('b', 'SubB')
        field = Field(100)
        field.subfields.append(sfa)
        field.subfields.append(sfb)
        found = field[0]
        self.assertEqual(found, sfa.value)
        found = field[1]
        self.assertEqual(found, sfb.value)

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

    def test_eq_1(self):
        f1 = Field(100, 'Value 100-A')
        f2 = Field(100, 'Value 100-A')
        f3 = Field(100, 'Value 100-B')
        self.assertEqual(f1, f2)
        self.assertNotEqual(f2, f3)

    def test_eq_2(self):
        f1 = Field(700, {'a': 'A', 'g': 'G', 'b': 'B'})
        f2 = Field(700, {'b': 'B', 'a': 'A', 'g': 'G'})
        f3 = Field(700, {'a': 'X', 'g': 'G', 'b': 'B'})
        self.assertEqual(f1, f2)
        self.assertNotEqual(f2, f3)

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

    def test_text_1(self):
        field = Field()
        self.assertEqual(field.text(), '')

    def test_text_2(self):
        field = Field(100)
        self.assertEqual(field.text(), '')

    def test_text_3(self):
        field = Field(100, 'Value')
        self.assertEqual(field.text(), 'Value')

    def test_text_4(self):
        field = Field(100, SubField('a', 'SubA')).add('b', 'SubB')
        self.assertEqual(field.text(), '^aSubA^bSubB')

    def test_to_dict_1(self):
        field = Field()
        d = field.to_dict()
        self.assertEqual(len(d), 0)

    def test_to_dict_2(self):
        field = Field(100)
        d = field.to_dict()
        self.assertEqual(len(d), 0)

    def test_to_dict_3(self):
        field = Field(100, 'Value')
        d = field.to_dict()
        self.assertEqual(len(d), 0)

    def test_to_dict_4(self):
        field = Field(100, SubField('a', 'SubA')).add('b', 'SubB')
        d = field.to_dict()
        self.assertEqual(len(d), 2)
        self.assertEqual(d['a'], 'SubA')
        self.assertEqual(d['b'], 'SubB')

    def test_keys_1(self):
        field = Field(100)
        d = field.keys()
        self.assertEqual(d, set())

    def test_keys_2(self):
        field = Field(100, 'Value')
        d = field.keys()
        self.assertEqual(d, set())

    def test_keys_3(self):
        field = Field(100).add('a', 'SubA').add('b', 'SubB')
        d = field.keys()
        self.assertEqual(len(d), 2)
        self.assertIn('a', d)
        self.assertIn('b', d)

    def test_keys_4(self):
        field = Field(100).add('a', 'SubA1').add('a', 'SubA2')
        d = field.keys()
        self.assertEqual(len(d), 1)
        self.assertIn('a', d)


#############################################################################


# noinspection DuplicatedCode
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

    def test_init_3(self):
        subfield = SubField('a', 'A')
        self.assertRaises(TypeError, Record, subfield)

    def test_set_item_1(self):
        record = Record()
        record[100] = 'Field 100'
        record[200] = 'Field 200'
        self.assertEqual(len(record.fields), 2)
        self.assertEqual(record.fields[0].tag, 100)
        self.assertEqual(record.fields[1].tag, 200)
        self.assertEqual(record.fields[0].value, 'Field 100')
        self.assertEqual(record.fields[1].value, 'Field 200')

    def test_set_item_2(self):
        record = Record()
        record[100] = 'Field 100-A'
        record[100] = 'Field 100-B'
        self.assertEqual(record.fields[0].value, 'Field 100-B')

    def test_set_item_3(self):
        record = Record()
        record[100] = ['Field 100-A', 'Field 100-B', 'Field 100-C']
        record[200] = ['Field 200']
        self.assertEqual(len(record.fields), 4)
        self.assertEqual(record.fields[0].value, 'Field 100-A')
        self.assertEqual(record.fields[1].value, 'Field 100-B')
        self.assertEqual(record.fields[2].value, 'Field 100-C')

    def test_set_item_4(self):
        record = Record()
        record[100] = {'a': 'Field 100-A', 'b': 'Field 100-B', 'c': 'Field 100-C'}
        self.assertEqual(len(record.fields), 1)
        self.assertEqual(record[100]['a'], 'Field 100-A')
        self.assertEqual(record[100]['b'], 'Field 100-B')
        self.assertEqual(record[100]['c'], 'Field 100-C')

    def test_add_1(self):
        record = Record()
        record.add(100, 'Some value')
        self.assertEqual(len(record.fields), 1)

    def test_add_2(self):
        record = Record()
        record.add(100).add('a', 'SubA').add('b', 'SubB')
        self.assertEqual(len(record.fields), 1)
        self.assertEqual(len(record.fields[0].subfields), 2)

    def test_add_duplicate_1(self):
        record = Record()
        record.add(100, 'Some value')
        field = Field(100, 'Some value')
        self.assertIn(field, record.fields)
        self.assertRaises(ValueError, record.add, 100, 'Some value')

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

    def test_all_as_dict_1(self):
        record = Record()
        v = record.first_as_dict(700)
        self.assertEqual(len(v), 0)

    def test_all_as_dict_2(self):
        record = Record()
        record.add(100, 'Field100')
        v = record.all_as_dict(100)
        self.assertEqual(len(v), 1)
        self.assertEqual(len(v[0]), 0)

    def test_all_as_dict_3(self):
        record = Record()
        record.add(100).add('a', 'SubA').add('b', 'SubB')
        v = record.all_as_dict(100)
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0]['a'], 'SubA')
        self.assertEqual(v[0]['b'], 'SubB')

    def test_all_as_dict_4(self):
        record = Record()
        record.add(100).add('a', 'SubA').add('b', 'SubB')
        record.add(100).add('c', 'SubC').add('d', 'SubD')
        v = record.all_as_dict(100)
        self.assertEqual(len(v), 2)
        self.assertEqual(v[0]['a'], 'SubA')
        self.assertEqual(v[0]['b'], 'SubB')
        self.assertEqual(v[1]['c'], 'SubC')
        self.assertEqual(v[1]['d'], 'SubD')

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

    def test_first_1(self):
        record = Record()
        v = record.first(100)
        self.assertIsNone(v)

    def test_first_2(self):
        record = Record()
        v100 = Field(100)
        record.fields.append(v100)
        v = record.first(100)
        self.assertIs(v, v100)

    def test_first_3(self):
        record = Record()
        v100_1 = Field(100)
        record.fields.append(v100_1)
        v100_2 = Field(100)
        record.fields.append(v100_2)
        v = record.first(100)
        self.assertIs(v, v100_1)

    def test_first_as_dict_1(self):
        record = Record()
        v = record.first_as_dict(100)
        self.assertEqual(len(v), 0)

    def test_first_as_dict_2(self):
        record = Record()
        record.add(100).add('a', 'SubA').add('b', 'SubB')
        v = record.first_as_dict(100)
        self.assertEqual(len(v), 2)
        self.assertEqual(v['a'], 'SubA')
        self.assertEqual(v['b'], 'SubB')

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
        s = dict(record)
        self.assertEqual(len(s), 2)
        self.assertEqual(s[100], 'Field 100')
        self.assertEqual(s[200]['a'], 'SubA')
        self.assertEqual(s[200]['b'], 'SubB')

    def test_iter_2(self):
        record = Record()
        record.add(100, 'Field 100')
        record.add(200).add('a', 'SubA').add('b', 'SubB')
        i = iter(record)
        f = next(i)
        self.assertEqual(f[0], 100)
        self.assertEqual(f[1], 'Field 100')
        f = next(i)
        self.assertEqual(f[0], 200)
        self.assertEqual(f[1]['a'], 'SubA')
        self.assertEqual(f[1]['b'], 'SubB')
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
        self.assertEqual(record[200]['a'], 'SubA')
        self.assertEqual(record[300], '')

    def test_setitem_1(self):
        f100 = Field(100, 'Field 100')
        f200 = Field(200).add('a', 'SubA').add('b', 'SubB')
        record = Record()
        record.fields.append(f100)
        record.fields.append(f200)
        new_value = 'New value'
        record[100] = new_value
        self.assertEqual(record[100], new_value)
        record[200] = '^aNewA^bNewB'
        self.assertEqual(record[200]['a'], 'NewA')
        self.assertEqual(record[200]['b'], 'NewB')
        record[300] = new_value
        self.assertEqual(len(record.fields), 3)
        self.assertIn(300, record.keys())
        self.assertEqual(record.fields[2].value, new_value)
        record[400] = Field(tag=400).add('a', 'NewA').add('b', 'NewB')
        self.assertEqual(len(record.fields), 4)
        self.assertIn(400, record.keys())
        self.assertEqual(record[400]['a'], 'NewA')
        self.assertEqual(record[400]['b'], 'NewB')
        record[300] = SubField('a', 'OtherA')
        self.assertEqual(len(record.fields), 4)
        self.assertIn(300, record.keys())
        self.assertNotIn('', record[300])
        self.assertEqual(record[300]['a'], 'OtherA')

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

    def test_eq_1(self):
        r1 = Record(
            Field(100, 'Value 100-A'),
            Field(701, {'a': 'A1', 'g': 'G1', 'b': 'B1'}),
            Field(701, {'a': 'A2', 'g': 'G2', 'b': 'B2'}),
        )
        r2 = Record(
            Field(701, {'g': 'G2', 'b': 'B2', 'a': 'A2'}),
            Field(701, {'b': 'B1', 'a': 'A1', 'g': 'G1'}),
            Field(100, 'Value 100-A'),
        )
        r3 = Record(
            Field(100, 'Value 100-B'),
            Field(701, {'g': 'G2', 'b': 'B2', 'a': 'A2'}),
            Field(701, {'b': 'B1', 'a': 'A1', 'g': 'G1'}),
        )
        r4 = Record(
            Field(100, 'Value 100-A'),
            Field(701, {'g': 'X', 'b': 'B2', 'a': 'A2'}),
            Field(701, {'b': 'B1', 'a': 'A1', 'g': 'G1'}),
        )
        r5 = Record(
            Field(100, 'Value 100-A'),
            Field(701, {'g': 'G2', 'b': 'B2', 'a': 'A2'}),
            Field(701, {'b': 'B1', 'a': 'A1'}),
        )
        self.assertEqual(r1, r2)
        self.assertNotEqual(r2, r3)
        self.assertNotEqual(r2, r4)
        self.assertNotEqual(r2, r5)

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


class TestFileSpecification(unittest.TestCase):

    def test_init_1(self):
        spec = FileSpecification(1, '', 'file.ext')
        self.assertEqual(spec.binary, False)
        self.assertEqual(spec.path, 1)
        self.assertEqual(spec.database, '')
        self.assertEqual(spec.filename, 'file.ext')
        self.assertEqual(spec.content, None)

    def test_parse_1(self):
        spec = FileSpecification.parse('0..hello.txt')
        self.assertEqual(spec.binary, False)
        self.assertEqual(spec.path, 0)
        self.assertEqual(spec.database, '')
        self.assertEqual(spec.filename, 'hello.txt')
        self.assertEqual(spec.content, None)

    def test_parse_2(self):
        spec = FileSpecification.parse('3.IBIS.&file.txt&Content')
        self.assertEqual(spec.binary, False)
        self.assertEqual(spec.path, 3)
        self.assertEqual(spec.database, 'IBIS')
        self.assertEqual(spec.filename, 'file.txt')
        self.assertEqual(spec.content, 'Content')

    def test_parse_3(self):
        spec = FileSpecification.parse('3.IBIS.@file.txt&Content')
        self.assertEqual(spec.binary, True)
        self.assertEqual(spec.path, 3)
        self.assertEqual(spec.database, 'IBIS')
        self.assertEqual(spec.filename, 'file.txt')
        self.assertEqual(spec.content, 'Content')

    def test_system_1(self):
        spec = FileSpecification.system('hello.txt')
        self.assertEqual(spec.binary, False)
        self.assertEqual(spec.path, 0)
        self.assertEqual(spec.database, None)
        self.assertEqual(spec.filename, 'hello.txt')
        self.assertEqual(spec.content, None)
        self.assertEqual(str(spec), '0..hello.txt')

    def test_str_1(self):
        spec = FileSpecification(1, '', 'file.ext')
        self.assertEqual(str(spec), '1..file.ext')

    def test_str_2(self):
        spec = FileSpecification(6, 'IBIS', 'file.ext')
        self.assertEqual(str(spec), '6.IBIS.file.ext')

    def test_str_3(self):
        spec = FileSpecification(6, 'IBIS', 'file.ext')
        spec.content = 'Content'
        self.assertEqual(str(spec), '6.IBIS.&file.ext&Content')

    def test_str_4(self):
        spec = FileSpecification(6, 'IBIS', 'file.ext')
        spec.content = 'Content'
        spec.binary = True
        self.assertEqual(str(spec), '6.IBIS.@file.ext&Content')

#############################################################################


class TestIrbisFormat(unittest.TestCase):

    def test_comments_1(self):
        self.assertEqual("", remove_comments(""))
        self.assertEqual(" ", remove_comments(" "))
        self.assertEqual("v100,/,v200", remove_comments("v100,/,v200"))
        self.assertEqual("\tv100\r\n", remove_comments("\tv100\r\n"))
        self.assertEqual("v100\r\nv200", remove_comments("v100/* Comment\r\nv200"))
        self.assertEqual("v100, '/* Not comment', v200",
                         remove_comments("v100, '/* Not comment', v200"))
        self.assertEqual("v100, |/* Not comment|, v200",
                         remove_comments("v100, |/* Not comment|, v200"))
        self.assertEqual("v100, '/* Not comment', v200, \r\nv300",
                         remove_comments("v100, '/* Not comment', v200, /*comment\r\nv300"))

    def test_prepare_1(self):
        self.assertEqual("", prepare_format(""))
        self.assertEqual(" ", prepare_format(" "))
        self.assertEqual("", prepare_format("\r\n"))
        self.assertEqual("v100,/,v200", prepare_format("v100,/,v200"))
        self.assertEqual("v100", prepare_format("\tv100\r\n"))
        self.assertEqual("v100v200",
                         prepare_format("v100/*comment\r\nv200"))
        self.assertEqual("v100",
                         prepare_format("v100/*comment"))

#############################################################################


class TestSearchBuilder(unittest.TestCase):

    def test_init_1(self):
        builder = Search()
        self.assertEqual(str(builder), '')

    def test_all_1(self):
        self.assertEqual(str(Search.all()), 'I=$')

    def test_and_1(self):
        builder = author('Byron$').and_(title('Poems$'))
        self.assertEqual(str(builder), '(A=Byron$ * T=Poems$)')

    def test_and_2(self):
        builder = author('Byron$').and_(title('Poems$'), number(100))
        self.assertEqual(str(builder), '(A=Byron$ * T=Poems$ * IN=100)')

    def test_author_1(self):
        builder = author('Byron')
        self.assertEqual(str(builder), 'A=Byron')

    def test_author_2(self):
        builder = author('Byron', 'Tolstoy')
        self.assertEqual(str(builder), '(A=Byron + A=Tolstoy)')

    def test_bbk_1(self):
        builder = bbk('11')
        self.assertEqual(str(builder), 'BBK=11')

    def test_bbk_2(self):
        builder = bbk('22', '33')
        self.assertEqual(str(builder), '(BBK=22 + BBK=33)')

    def test_document_kind_1(self):
        builder = document_kind('J')
        self.assertEqual(str(builder), 'V=J')

    def test_document_kind_2(self):
        builder = document_kind('J', 'KN')
        self.assertEqual(str(builder), '(V=J + V=KN)')

    def test_equals_1(self):
        builder = Search.equals('PREFIX=', 'Value$')
        self.assertEqual(str(builder), 'PREFIX=Value$')

    def test_equals_2(self):
        builder = Search.equals('PREFIX=', 'Hello, world')
        self.assertEqual(str(builder), '"PREFIX=Hello, world"')

    def test_equals_3(self):
        builder = Search.equals('PREFIX=', 'Hello', 'world')
        self.assertEqual(str(builder), '(PREFIX=Hello + PREFIX=world)')

    def test_keyword_1(self):
        builder = keyword('Hello')
        self.assertEqual(str(builder), 'K=Hello')

    def test_keyword_2(self):
        builder = keyword('Hello', 'world')
        self.assertEqual(str(builder), '(K=Hello + K=world)')

    def test_language_1(self):
        builder = language('rus')
        self.assertEqual(str(builder), 'J=rus')

    def test_language_2(self):
        builder = language('rus', 'eng')
        self.assertEqual(str(builder), '(J=rus + J=eng)')

    def test_magazine_1(self):
        builder = magazine('Neva')
        self.assertEqual(str(builder), 'TJ=Neva')

    def test_magazine_2(self):
        builder = magazine('Neva', 'Moscow')
        self.assertEqual(str(builder), '(TJ=Neva + TJ=Moscow)')

    def test_mhr_1(self):
        builder = mhr('CHZ')
        self.assertEqual(str(builder), 'MHR=CHZ')

    def test_mhr_2(self):
        builder = mhr('CHZ', 'AB')
        self.assertEqual(str(builder), '(MHR=CHZ + MHR=AB)')

    def test_need_wrap_1(self):
        self.assertTrue(Search.need_wrap(''))
        self.assertFalse(Search.need_wrap('Hello'))
        self.assertTrue(Search.need_wrap('Hello, world!'))

    def test_need_wrap_2(self):
        self.assertFalse(Search.need_wrap('"Hello"'))
        self.assertFalse(Search.need_wrap('(Hello)'))

    def test_not_1(self):
        builder = author('Byron$').not_(title('Poems$'))
        self.assertEqual(str(builder), '(A=Byron$ ^ T=Poems$)')

    def test_number_1(self):
        builder = number(123)
        self.assertEqual(str(builder), 'IN=123')

    def test_number_2(self):
        builder = number(123, 456)
        self.assertEqual(str(builder), '(IN=123 + IN=456)')

    def test_or_1(self):
        builder = author('Byron$').or_(title('Poems$'))
        self.assertEqual(str(builder), '(A=Byron$ + T=Poems$)')

    def test_or_2(self):
        builder = author('Byron$').or_(title('Poems$'), number(100))
        self.assertEqual(str(builder), '(A=Byron$ + T=Poems$ + IN=100)')

    def test_place_1(self):
        builder = place('Irkutsk')
        self.assertEqual(str(builder), 'MI=Irkutsk')

    def test_place_2(self):
        builder = place('Irkutsk', 'Moscow')
        self.assertEqual(str(builder), '(MI=Irkutsk + MI=Moscow)')

    def test_publisher_1(self):
        builder = publisher('ISTU')
        self.assertEqual(str(builder), 'O=ISTU')

    def test_publisher_2(self):
        builder = publisher('ISTU', 'ISU')
        self.assertEqual(str(builder), '(O=ISTU + O=ISU)')

    def test_rzn_1(self):
        builder = rzn(1)
        self.assertEqual(str(builder), 'RZN=1')

    def test_rzn_2(self):
        builder = rzn(1, 2)
        self.assertEqual(str(builder), '(RZN=1 + RZN=2)')

    def test_same_field_1(self):
        builder = author('Byron$').same_field(title('Poems$'))
        self.assertEqual(str(builder), '(A=Byron$ (G) T=Poems$)')

    def test_same_field_2(self):
        builder = author('Byron$').same_field(title('Poems$'), number(100))
        self.assertEqual(str(builder), '(A=Byron$ (G) T=Poems$ (G) IN=100)')

    def test_same_repeat_1(self):
        builder = author('Byron$').same_repeat(title('Poems$'))
        self.assertEqual(str(builder), '(A=Byron$ (F) T=Poems$)')

    def test_same_repeat_2(self):
        builder = author('Byron$').same_repeat(title('Poems$'), number(100))
        self.assertEqual(str(builder), '(A=Byron$ (F) T=Poems$ (F) IN=100)')

    def test_subject_1(self):
        builder = subject('concrete')
        self.assertEqual(str(builder), 'S=concrete')

    def test_subject_2(self):
        builder = subject('concrete', 'steel')
        self.assertEqual(str(builder), '(S=concrete + S=steel)')

    def test_title_1(self):
        builder = title('Novels')
        self.assertEqual(str(builder), 'T=Novels')

    def test_title_2(self):
        builder = title('Novels', 'Poems')
        self.assertEqual(str(builder), '(T=Novels + T=Poems)')

    def test_udc_1(self):
        builder = udc('11')
        self.assertEqual(str(builder), 'U=11')

    def test_udc_2(self):
        builder = udc('11', '22')
        self.assertEqual(str(builder), '(U=11 + U=22)')

    def test_wrap_1(self):
        self.assertEqual(Search.wrap(''), '""')
        self.assertEqual(Search.wrap('Hello'), 'Hello')
        self.assertEqual(Search.wrap('Hello, world'), '"Hello, world"')

    def test_year_1(self):
        builder = year(2000)
        self.assertEqual(str(builder), 'G=2000')

    def test_year_2(self):
        builder = year(2000, 2019)
        self.assertEqual(str(builder), '(G=2000 + G=2019)')

#############################################################################

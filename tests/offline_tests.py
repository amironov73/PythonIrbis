# coding: utf-8

"""
Tests that doesn't require the IRBIS server connection.
"""

import random
import os
import os.path
import unittest

from pyirbis.core import SubField, RecordField, MarcRecord, FileSpecification, IrbisConnection, \
    LOGICALLY_DELETED, PHYSICALLY_DELETED, LAST, remove_comments, prepare_format
from pyirbis.ext import OptLine, OptFile, load_opt_file, MenuFile, load_menu, ParFile, \
    load_par_file, TreeFile, load_tree_file, AlphabetTable, load_alphabet_table, UpperCaseTable, \
    load_uppercase_table
from pyirbis.export import read_text_record, write_text_record

import pyirbis.iso2709 as iso


def script_path():
    return os.path.dirname(os.path.realpath(__file__))


def relative_path(filename: str):
    return os.path.realpath(os.path.join(script_path(), filename))


def random_text_file():
    import tempfile
    result = tempfile.NamedTemporaryFile(mode='wt', encoding='utf-8', delete=False)
    return result


def random_file_name():
    tempdir = os.environ['TMP']
    filename = str(random.randint(1111111, 9999999))
    result = os.path.join(tempdir, filename)
    return result


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


class TestRecordField(unittest.TestCase):

    def test_init_1(self):
        field = RecordField()
        self.assertEqual(field.tag, RecordField.DEFAULT_TAG)
        self.assertIsNone(field.value)
        self.assertEqual(len(field.subfields), 0)

    def test_init_2(self):
        field = RecordField(100)
        self.assertEqual(field.tag, 100)
        self.assertIsNone(field.value)
        self.assertEqual(len(field.subfields), 0)

    def test_init_3(self):
        field = RecordField(100, 'Some value')
        self.assertEqual(field.tag, 100)
        self.assertEqual(field.value, 'Some value')
        self.assertEqual(len(field.subfields), 0)

    def test_init_4(self):
        field = RecordField(100, SubField('a', 'Some value'))
        self.assertEqual(field.tag, 100)
        self.assertIsNone(field.value)
        self.assertEqual(1, len(field.subfields))

    def test_init_5(self):
        field = RecordField(100, SubField('a', 'Some value'), SubField('b', 'Other value'))
        self.assertEqual(field.tag, 100)
        self.assertIsNone(field.value)
        self.assertEqual(2, len(field.subfields))

    def test_add_1(self):
        field = RecordField()
        field.add('a', 'Some text')
        self.assertEqual(len(field.subfields), 1)
        self.assertEqual(field.subfields[0].code, 'a')
        self.assertEqual(field.subfields[0].value, 'Some text')

    def test_all_1(self):
        field = RecordField()
        field.add('a', 'A1').add('a', 'A2').add('b', 'B1')
        self.assertEqual(2, len(field.all('A')))
        self.assertEqual(1, len(field.all('B')))

    def test_all_values_1(self):
        field = RecordField()
        field.add('a', 'A1').add('a', 'A2').add('b', 'B1')
        self.assertEqual(2, len(field.all_values('A')))
        self.assertEqual(1, len(field.all_values('B')))

    def test_assign_from_1(self):
        first = RecordField(100, 'Some value', SubField('a', 'SubA'))
        second = RecordField(200, 'Other value', SubField('b', 'SubB'))
        second.assign_from(first)
        self.assertEqual(second.tag, 200)
        self.assertEqual(first.value, second.value)
        self.assertEqual(len(first.subfields), len(second.subfields))
        self.assertEqual(first.subfields[0].code, second.subfields[0].code)
        self.assertEqual(first.subfields[0].value, second.subfields[0].value)

    def test_clone_1(self):
        original = RecordField(100, 'Some value')
        original.add('a', 'Some text')
        clone = original.clone()
        self.assertEqual(original.tag, clone.tag)
        self.assertEqual(original.value, clone.value)
        self.assertEqual(len(original.subfields), len(clone.subfields))

    def test_clear_1(self):
        field = RecordField(100, 'Some value')
        field.add('a', 'Some text')
        field.clear()
        self.assertEqual(len(field.subfields), 0)

    def test_first_1(self):
        sf1 = SubField('a', 'First value')
        sf2 = SubField('b', 'Second value')
        field = RecordField(100, sf1, sf2)
        self.assertIs(field.first('a'), sf1)
        self.assertIs(field.first('b'), sf2)
        self.assertIsNone(field.first('c'))

    def test_first_value_1(self):
        sf1 = SubField('a', 'First value')
        sf2 = SubField('b', 'Second value')
        field = RecordField(100, sf1, sf2)
        self.assertEqual(field.first_value('a'), sf1.value)
        self.assertEqual(field.first_value('b'), sf2.value)
        self.assertIsNone(field.first_value('c'))

    def test_str_1(self):
        field = RecordField(100, 'Some value')
        field.add('a', 'Some text')
        field.add('b', 'Other text')
        self.assertEqual(str(field), '100#Some value^aSome text^bOther text')

    def test_str_2(self):
        field = RecordField()
        self.assertEqual(str(field), '')

    def test_iter_1(self):
        field = RecordField(100, SubField('a', 'SubA'), SubField('b', 'SubB'))
        s = list(field)
        self.assertEqual(len(s), 2)
        self.assertEqual(s[0].code, field.subfields[0].code)
        self.assertEqual(s[0].value, field.subfields[0].value)
        self.assertEqual(s[1].code, field.subfields[1].code)
        self.assertEqual(s[1].value, field.subfields[1].value)

    def test_iter_2(self):
        field = RecordField()
        s = list(field)
        self.assertEqual(len(s), 0)

    def test_iter_3(self):
        field = RecordField(100, SubField('a', 'SubA'), SubField('b', 'SubB'))
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
        field = RecordField(100)
        self.assertEqual(len(field.subfields), 0)
        field += SubField('a', 'SubA')
        self.assertEqual(len(field.subfields), 1)
        field += SubField('b', 'SubB')
        self.assertEqual(len(field.subfields), 2)
        self.assertEqual(str(field), '100#^aSubA^bSubB')

    def test_iadd_2(self):
        field = RecordField(100)
        field += (SubField('a', 'SubA'), SubField('b', 'SubB'))
        self.assertEqual(len(field.subfields), 2)
        self.assertEqual(str(field), '100#^aSubA^bSubB')

    def test_isub_1(self):
        sfa = SubField('a', 'SubA')
        sfb = SubField('b', 'SubB')
        field = RecordField(100, sfa, sfb)
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
        field = RecordField(100, sfa, sfb)
        field -= (sfa, sfb)
        self.assertEqual(len(field.subfields), 0)
        field -= (sfa, sfb)
        self.assertEqual(len(field.subfields), 0)

    def test_getitem_1(self):
        sfa = SubField('a', 'SubA')
        sfb = SubField('b', 'SubB')
        field = RecordField(100, sfa, sfb)
        found = field['a']
        self.assertIs(found, sfa)
        found = field['b']
        self.assertIs(found, sfb)
        found = field['c']
        self.assertIsNone(found)

    def test_getitem_2(self):
        sfa = SubField('a', 'SubA')
        sfb = SubField('b', 'SubB')
        field = RecordField(100, sfa, sfb)
        found = field[0]
        self.assertIs(found, sfa)
        found = field[1]
        self.assertIs(found, sfb)

    def test_setitem_1(self):
        sfa = SubField('a', 'SubA')
        sfb = SubField('b', 'SubB')
        field = RecordField(100, sfa, sfb)
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
        field = RecordField(100, sfa, sfb)
        self.assertEqual(len(field.subfields), 2)
        field['a'] = None
        self.assertEqual(len(field.subfields), 1)
        field['b'] = None
        self.assertEqual(len(field.subfields), 0)
        field['c'] = None
        self.assertEqual(len(field.subfields), 0)

    def test_len_1(self):
        field = RecordField(100, SubField('a', 'SubA'), SubField('b', 'SubB'))
        self.assertEqual(len(field), 2)

    def test_len_2(self):
        field = RecordField()
        self.assertEqual(len(field), 0)

    def test_bool_1(self):
        field = RecordField(100, SubField('a', 'SubA'), SubField('b', 'SubB'))
        self.assertTrue(bool(field))

    def test_bool_2(self):
        field = RecordField(100, 'Value')
        self.assertTrue(bool(field))

    def test_bool_3(self):
        field = RecordField(100)
        self.assertFalse(bool(field))

    def test_bool_4(self):
        field = RecordField()
        field.value = 'Value'
        self.assertFalse(bool(field))


class TestMarcRecord(unittest.TestCase):

    def test_init_1(self):
        record = MarcRecord()
        self.assertIsNone(record.database)
        self.assertEqual(record.mfn, 0)
        self.assertEqual(record.version, 0)
        self.assertEqual(record.status, 0)
        self.assertEqual(len(record.fields), 0)

    def test_init_2(self):
        f100 = RecordField(100, 'Field 100')
        f200 = RecordField(200, 'Field 200')
        record = MarcRecord(f100, f200)
        self.assertEqual(len(record.fields), 2)
        self.assertEqual(record.fields[0].tag, 100)
        self.assertEqual(record.fields[1].tag, 200)

    def test_add_1(self):
        record = MarcRecord().add(100, 'Some value')
        self.assertEqual(len(record.fields), 1)

    def test_add_2(self):
        record = MarcRecord().add(100, SubField('a', 'SubA'),
                                  SubField('b', 'SubB'))
        self.assertEqual(len(record.fields), 1)
        self.assertEqual(len(record.fields[0].subfields), 2)

    def test_all_1(self):
        record = MarcRecord()
        record.add(100, 'Field100').add(200, 'Field200')\
            .add(300, 'Field300/1').add(300, 'Field300/2')
        self.assertEqual(len(record.fields), 4)
        self.assertEqual(len(record.all(100)), 1)
        self.assertEqual(len(record.all(200)), 1)
        self.assertEqual(len(record.all(300)), 2)
        self.assertEqual(len(record.all(400)), 0)

    def test_clear_1(self):
        record = MarcRecord().add(100, 'Some value')
        record.clear()
        self.assertEqual(len(record.fields), 0)

    def test_clone_1(self):
        original = MarcRecord().add(100, 'Some value')
        original.database = 'IBIS'
        clone = original.clone()
        self.assertEqual(original.database, clone.database)
        self.assertEqual(original.mfn, clone.mfn)
        self.assertEqual(original.status, clone.status)
        self.assertEqual(original.version, clone.version)
        self.assertEqual(len(original.fields), len(clone.fields))

    def test_encode_1(self):
        record = MarcRecord()
        record.mfn = 123
        record.version = 321
        record.status = LAST
        record.add(100, 'Field100').add(200, SubField('a', 'SubA'), SubField('b', 'SubB'))
        self.assertEqual(record.encode(), ['123#32', '0#321', '100#Field100', '200#^aSubA^bSubB'])

    def test_fm_1(self):
        record = MarcRecord().add(100, 'Field 100').add(200, 'Field 200')
        self.assertEqual('Field 100', record.fm(100))
        self.assertEqual('Field 200', record.fm(200))
        self.assertIsNone(record.fm(300))

    def test_fm_2(self):
        record = MarcRecord().add(100, '', SubField('a', '100A'), SubField('b', '100B'))
        record.add(200, '', SubField('b', '200B'), SubField('c', '200C'))
        self.assertEqual('100A', record.fm(100, 'a'))
        self.assertEqual('100B', record.fm(100, 'b'))
        self.assertIsNone(record.fm(100, 'c'))
        self.assertIsNone(record.fm(200, 'a'))
        self.assertEqual('200B', record.fm(200, 'b'))
        self.assertEqual('200C', record.fm(200, 'c'))

    def test_fma_1(self):
        record = MarcRecord().add(100, 'Field 100/1').add(100, 'Field 100/2')
        record.add(200, SubField('a', 'SubA/1'), SubField('b', 'SubB/1'))
        record.add(200, SubField('a', 'SubA/2'), SubField('b', 'SubB/2'))
        self.assertEqual(record.fma(100), ['Field 100/1', 'Field 100/2'])
        self.assertEqual(record.fma(200, 'a'), ['SubA/1', 'SubA/2'])
        self.assertEqual(record.fma(200, 'b'), ['SubB/1', 'SubB/2'])
        self.assertEqual(record.fma(200, 'c'), [])
        self.assertEqual(record.fma(300), [])
        self.assertEqual(record.fma(300, 'a'), [])

    def test_is_deleted_1(self):
        record = MarcRecord()
        self.assertFalse(record.is_deleted())
        record.status = LOGICALLY_DELETED
        self.assertTrue(record.is_deleted())
        record.status = PHYSICALLY_DELETED
        self.assertTrue(record.is_deleted())
        record.status = LAST
        self.assertFalse(record.is_deleted())

    def test_record_parse_1(self):
        record = MarcRecord()
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
        record = MarcRecord().add(100, 'Field 100')\
            .add(200, 'Field 200', SubField('a', 'Subfield A'))
        self.assertEqual('100#Field 100\n200#Field 200^aSubfield A', str(record))

    def test_iter_1(self):
        record = MarcRecord().add(100, 'Field 100')\
            .add(200, SubField('a', 'SubA'), SubField('b', 'SubB'))
        s = list(record)
        self.assertEqual(len(s), 2)
        self.assertEqual(s[0].tag, 100)
        self.assertEqual(s[1].tag, 200)

    def test_iter_2(self):
        record = MarcRecord().add(100, 'Field 100')\
            .add(200, SubField('a', 'SubA'), SubField('b', 'SubB'))
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
        record = MarcRecord()
        self.assertEqual(len(record.fields), 0)
        record += RecordField(100, 'Field 100')
        self.assertEqual(len(record.fields), 1)
        record += RecordField(200, SubField('a', 'SubA'))
        self.assertEqual(len(record.fields), 2)

    def test_iadd_2(self):
        record = MarcRecord()
        record += (RecordField(100, 'Field 100'), RecordField(200, 'Field 200'))
        self.assertEqual(len(record.fields), 2)

    def test_isub_1(self):
        f100 = RecordField(100, 'Field 100')
        f200 = RecordField(200, SubField('a', 'SubA'))
        record = MarcRecord(f100, f200)
        record -= (f100, f200)
        self.assertEqual(len(record.fields), 0)
        record -= (f100, f200)
        self.assertEqual(len(record.fields), 0)

    def test_isub_2(self):
        f100 = RecordField(100, 'Field 100')
        f200 = RecordField(200, SubField('a', 'SubA'))
        record = MarcRecord(f100, f200)
        record -= f100
        self.assertEqual(len(record.fields), 1)
        record -= f100
        self.assertEqual(len(record.fields), 1)
        record -= f200
        self.assertEqual(len(record.fields), 0)
        record -= f200
        self.assertEqual(len(record.fields), 0)

    def test_getitem_1(self):
        record = MarcRecord().add(100, 'Field 100')\
            .add(200, SubField('a', 'SubA'), SubField('b', 'SubB'))
        self.assertEqual(record[100], 'Field 100')
        self.assertIsNone(record[200])
        self.assertIsNone(record[300])

    def test_setitem_1(self):
        f100 = RecordField(100, 'Field 100')
        f200 = RecordField(200, SubField('a', 'SubA'), SubField('b', 'SubB'))
        record = MarcRecord()
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
        record[400] = RecordField().add('a', 'NewA').add('b', 'NewB')
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
        f100 = RecordField(100, 'Field 100')
        f200 = RecordField(200, SubField('a', 'SubA'), SubField('b', 'SubB'))
        record = MarcRecord()
        record.fields.append(f100)
        record.fields.append(f200)
        self.assertEqual(len(record.fields), 2)
        record[100] = None
        self.assertEqual(len(record.fields), 1)
        record[200] = None
        self.assertEqual(len(record.fields), 0)

    def test_len_1(self):
        record = MarcRecord()
        self.assertEqual(len(record), 0)
        record.add(100, 'Field 100')
        self.assertEqual(len(record), 1)
        record.add(200, 'Field 200')
        self.assertEqual(len(record), 2)

    def test_bool_1(self):
        record = MarcRecord()
        self.assertFalse(bool(record))
        record.add(100, 'Field 100')
        self.assertTrue(bool(record))


class TestFileSpecification(unittest.TestCase):

    def test_init_1(self):
        spec = FileSpecification(1, '', 'file.ext')
        self.assertEqual(spec.binary, False)
        self.assertEqual(spec.path, 1)
        self.assertEqual(spec.database, '')
        self.assertEqual(spec.filename, 'file.ext')
        self.assertEqual(spec.content, None)

    def test_str_1(self):
        spec = FileSpecification(1, '', 'file.ext')
        self.assertEqual(str(spec), '1..file.ext')

    def test_str_2(self):
        spec = FileSpecification(6, 'IBIS', 'file.ext')
        self.assertEqual(str(spec), '6.IBIS.file.ext')


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


class Iso2709Test(unittest.TestCase):

    def test_read_record(self):
        filename = relative_path('data/test1.iso')
        with open(filename, 'rb') as fh:
            record = iso.read_record(fh)
            self.assertEqual(len(record.fields), 16)
            self.assertEqual(record.fm(200, 'a'), 'Вып. 13.')

            record = iso.read_record(fh)
            self.assertEqual(len(record.fields), 15)
            self.assertEqual(record.fm(200, 'a'), 'Задачи и этюды')

            count = 0
            while True:
                record = iso.read_record(fh)
                if record is None:
                    break
                count += 1
            self.assertEqual(count, 79)
        print()


class TestExport(unittest.TestCase):

    def test_read_text_record(self):
        filename = relative_path('data/records.txt')
        with open(filename, 'rt', encoding='utf-8') as stream:
            record = read_text_record(stream)
            self.assertIsNotNone(record)
            self.assertEqual(len(record.fields), 20)
            self.assertEqual(record.fm(200, 'a'), 'Странные люди')
            record = read_text_record(stream)
            self.assertIsNotNone(record)
            self.assertEqual(len(record.fields), 23)
            self.assertEqual(record.fm(200, 'a'), 'Передовые охотники')
            record = read_text_record(stream)
            self.assertIsNotNone(record)
            self.assertEqual(len(record.fields), 26)
            self.assertEqual(record.fm(200, 'a'), 'Focus 5')
            record = read_text_record(stream)
            self.assertIsNone(record)

    def test_write_text_record(self):
        sf = SubField
        with random_text_file() as stream:
            for i in range(10):
                record = MarcRecord()
                record.add(700, sf('a', 'Миронов'), sf('b', 'А. В.'),
                           sf('g', 'Алексей Владимирович'))
                record.add(200, sf('a', f'Работа с ИРБИС64: версия {i}.0'),
                           sf('e', 'руководство пользователя'))
                record.add(210, sf('a', 'Иркутск'), SubField('c', 'ИРНИТУ'),
                           sf('d', '2018'))
                record.add(920, 'PAZK')
                write_text_record(stream, record)


class TestIrbisConnection(unittest.TestCase):

    def test_init_1(self):
        connection = IrbisConnection()
        self.assertEqual(connection.host, 'localhost')
        self.assertEqual(connection.port, 6666)
        self.assertIsNone(connection.username)
        self.assertIsNone(connection.password)
        self.assertEqual(connection.database, 'IBIS')
        self.assertEqual(connection.client_id, 0)
        self.assertEqual(connection.query_id, 0)
        self.assertEqual(connection.connected, False)


class TestMenuFile(unittest.TestCase):

    # noinspection PyMethodMayBeStatic
    def get_menu(self):
        result = MenuFile()
        result.add('ISTU', 'Учебники, монографии и продолжающиеся издания')
        result.add('PERIO', 'Периодические издания')
        result.add('HUDO', 'Художественная литература')
        result.add('NTD', 'Нормативно-техническая документация')
        result.add('WORKS', 'Труды сотрудников ИРНИТУ')
        return result

    def test_init_1(self):
        menu = MenuFile()
        self.assertEqual(len(menu.entries), 0)

    def test_add_1(self):
        menu = MenuFile()
        menu.add('a', 'Item A')
        self.assertEqual(len(menu.entries), 1)

    def test_get_entry(self):
        menu = self.get_menu()
        entry = menu.get_entry('istu')
        self.assertIsNotNone(entry)
        self.assertEqual(entry.code, 'ISTU')
        self.assertEqual(entry.comment, 'Учебники, монографии и продолжающиеся издания')

    def test_get_value(self):
        menu = self.get_menu()
        value = menu.get_value('istu')
        self.assertEqual(value, 'Учебники, монографии и продолжающиеся издания')

    def test_load_menu_1(self):
        filename = relative_path('data/dbnam1.mnu')
        menu = load_menu(filename)
        self.assertEqual(len(menu.entries), 39)

    def test_save_1(self):
        menu = self.get_menu()
        filename = random_file_name()
        menu.save(filename)
        self.assertTrue(os.path.isfile(filename))


class TestParFile(unittest.TestCase):

    def test_init_1(self):
        path = 'SomePath'
        par = ParFile(path)
        self.assertEqual(par.xrf, path)
        self.assertEqual(par.mst, path)
        self.assertEqual(par.cnt, path)
        self.assertEqual(par.n01, path)
        self.assertEqual(par.n02, path)
        self.assertEqual(par.l01, path)
        self.assertEqual(par.l02, path)
        self.assertEqual(par.ifp, path)
        self.assertEqual(par.any, path)
        self.assertEqual(par.pft, path)
        self.assertEqual(par.ext, path)

    def test_load_par_file_1(self):
        filename = relative_path('data/istu.par')
        expected = '.\\DATAI\\ISTU\\'
        par = load_par_file(filename)
        self.assertEqual(par.xrf, expected)
        self.assertEqual(par.mst, expected)
        self.assertEqual(par.cnt, expected)
        self.assertEqual(par.n01, expected)
        self.assertEqual(par.n02, expected)
        self.assertEqual(par.l01, expected)
        self.assertEqual(par.l02, expected)
        self.assertEqual(par.ifp, expected)
        self.assertEqual(par.any, expected)
        self.assertEqual(par.pft, expected)
        self.assertEqual(par.ext, '\\\\172.20.1.208\\cover\\')

    def test_save_1(self):
        par = ParFile('SomePath')
        filename = random_file_name()
        par.save(filename)
        self.assertTrue(os.path.isfile(filename))


class TestTreeFile(unittest.TestCase):

    # noinspection PyMethodMayBeStatic
    def get_tree(self):
        result = TreeFile()
        result.add('1 - First')
        result.add('2 - Second')
        result.roots[1].add('2.1 - Second first')
        result.roots[1].add('2.2 - Second second')
        result.roots[1].children[1].add('2.2.1 - Second second first')
        result.roots[1].add('2.3 - Second third')
        result.add('3 - Third')
        result.roots[2].add('3.1 - Third first')
        result.roots[2].children[0].add('3.1.1 - Third first first')
        result.add('4 - Fourth')
        return result

    def test_init_1(self):
        tree = TreeFile()
        self.assertEqual(len(tree.roots), 0)

    def test_load_1(self):
        filename = relative_path('data/test1.tre')
        tree = load_tree_file(filename)
        self.assertEqual(len(tree.roots), 4)

    def test_save_1(self):
        tree = self.get_tree()
        filename = random_file_name()
        tree.save(filename)
        os.path.isfile(filename)


class TestOptFile(unittest.TestCase):

    # noinspection PyMethodMayBeStatic
    def get_opt(self):
        result = OptFile()
        result.tag = 920
        result.length = 5
        result.lines.append(OptLine('PAZK', 'PAZK42'))
        result.lines.append(OptLine('PVK', 'PVK42'))
        result.lines.append(OptLine('SPEC', 'SPEC42'))
        result.lines.append(OptLine('J', '!RPJ51'))
        result.lines.append(OptLine('NJ', '!NJ31'))
        result.lines.append(OptLine('NJP', '!NJ31'))
        result.lines.append(OptLine('NJK', '!NJ31'))
        result.lines.append(OptLine('AUNTD', 'AUNTD42'))
        result.lines.append(OptLine('ASP', 'ASP42'))
        result.lines.append(OptLine('MUSP', 'MUSP'))
        result.lines.append(OptLine('SZPRF', 'SZPRF'))
        result.lines.append(OptLine('BOUNI', 'BOUNI'))
        result.lines.append(OptLine('IBIS', 'IBIS'))
        result.lines.append(OptLine('+++++', 'PAZK42'))
        return result

    def test_init(self):
        opt = OptFile()
        self.assertEqual(len(opt.lines), 0)

    def test_load_opt_file(self):
        filename = relative_path('data/ws31.opt')
        opt = load_opt_file(filename)
        self.assertEqual(len(opt.lines), 14)

    def test_save(self):
        filename = random_file_name()
        opt = self.get_opt()
        opt.save(filename)
        self.assertTrue(os.path.isfile(filename))


class TestAlphabetTable(unittest.TestCase):

    def test_load_alphabet_table_1(self):
        filename = relative_path('data/isisacw.tab')
        table = load_alphabet_table(filename)
        self.assertTrue(table.is_alpha('A'))
        self.assertFalse(table.is_alpha(' '))
        self.assertEqual(table.split_words('Не слышны в саду даже шорохи!'),
                         ['Не', 'слышны', 'в', 'саду', 'даже', 'шорохи'])
        self.assertEqual(table.trim('___Удаление лишних символов!!!'),
                         'Удаление лишних символов')

    def test_get_default_1(self):
        table = AlphabetTable.get_default()
        self.assertTrue(table.is_alpha('A'))
        self.assertFalse(table.is_alpha(' '))
        self.assertEqual(table.split_words('Не слышны в саду даже шорохи!'),
                         ['Не', 'слышны', 'в', 'саду', 'даже', 'шорохи'])
        self.assertEqual(table.trim('___Удаление лишних символов!!!'),
                         'Удаление лишних символов')


class TestUpperCaseTable(unittest.TestCase):

    def test_load_uppercase_table_1(self):
        filename = relative_path('data/isisucw.tab')
        table = load_uppercase_table(filename)
        self.assertEqual(table.upper('привет'), 'ПРИВЕТ')

    def test_get_default_1(self):
        table = UpperCaseTable.get_default()
        self.assertEqual(table.upper('привет'), 'ПРИВЕТ')


if __name__ == '__main__':
    unittest.main()

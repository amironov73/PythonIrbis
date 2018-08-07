# coding: utf-8

import unittest

from pyirbis.core import *
import os.path
import pyirbis.iso2709 as iso


def script_path():
    return os.path.dirname(os.path.realpath(__file__))


def relative_path(filename: str):
    return os.path.realpath(os.path.join(script_path(), filename))


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

    def test_add_1(self):
        record = MarcRecord().add(100, 'Some value')
        self.assertEqual(len(record.fields), 1)

    def test_add_2(self):
        record = MarcRecord().add(100, SubField('a', 'SubA'), SubField('b', 'SubB'))
        self.assertEqual(len(record.fields), 1)
        self.assertEqual(len(record.fields[0].subfields), 2)

    def test_all_1(self):
        record = MarcRecord()
        record.add(100, 'Field100').add(200, 'Field200').add(300, 'Field300/1').add(300, 'Field300/2')
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
        record = MarcRecord().add(100, 'Field 100').add(200, 'Field 200', SubField('a', 'Subfield A'))
        self.assertEqual('100#Field 100\n200#Field 200^aSubfield A', str(record))

    def test_iter_1(self):
        record = MarcRecord().add(100, 'Field 100').add(200, SubField('a', 'SubA'), SubField('b', 'SubB'))
        s = list(record)
        self.assertEqual(len(s), 2)
        self.assertEqual(s[0].tag, 100)
        self.assertEqual(s[1].tag, 200)

    def test_iter_2(self):
        record = MarcRecord().add(100, 'Field 100').add(200, SubField('a', 'SubA'), SubField('b', 'SubB'))
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

    def test_getitem_1(self):
        record = MarcRecord().add(100, 'Field 100').add(200, SubField('a', 'SubA'), SubField('b', 'SubB'))
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


class Iso2709Test(unittest.TestCase):

    def test_read_record(self):
        print('Read ISO file')
        filename = relative_path('data/test1.iso')
        with open(filename, 'rb') as fh:
            record = iso.read_record(fh)
            print()
            self.assertEqual(len(record.fields), 16)
            self.assertEqual(record.fm(200, 'a'), 'Вып. 13.')

            record = iso.read_record(fh)
            print()
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


if __name__ == '__main__':
    unittest.main()

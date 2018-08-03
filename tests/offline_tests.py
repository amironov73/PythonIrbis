import unittest

from pyirbis import *
from pyirbis.infrastructure import *


class TestSubField(unittest.TestCase):

    def test_init_1(self):
        sf = SubField()
        self.assertEqual(sf.code, '\0')
        self.assertIsNone(sf.value)

    def test_init_2(self):
        sf = SubField('a')
        self.assertEqual(sf.code, 'a')
        self.assertIsNone(sf.value)

    def test_init_3(self):
        sf = SubField('a', 'Some text')
        self.assertEqual(sf.code, 'a')
        self.assertEqual(sf.value, 'Some text')

    def test_clone(self):
        original = SubField('a', 'Some text')
        clone = original.clone()
        self.assertEqual(clone.code, original.code)
        self.assertEqual(clone.value, original.value)

    def test_str(self):
        sf = SubField('a', 'Some text')
        self.assertEqual(str(sf), '^aSome text')


class TestRecordField(unittest.TestCase):

    def test_init_1(self):
        field = RecordField()
        self.assertEqual(field.tag, 0)
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

    def test_str_1(self):
        field = RecordField(100, 'Some value')
        field.add('a', 'Some text')
        field.add('b', 'Other text')
        self.assertEqual('100#Some value^aSome text^bOther text', str(field))


class TestMarcRecord(unittest.TestCase):

    def test_init_1(self):
        record = MarcRecord()
        self.assertIsNone(record.database)
        self.assertEqual(record.mfn, 0)
        self.assertEqual(record.version, 0)
        self.assertEqual(record.status, 0)
        self.assertEqual(len(record.fields), 0)

    def test_add_1(self):
        record = MarcRecord()
        record.add(100, 'Some value')
        self.assertEqual(len(record.fields), 1)

    def test_add_2(self):
        record = MarcRecord()
        record.add(100, '', SubField('a', 'SubA'), SubField('b', 'SubB'))
        self.assertEqual(len(record.fields), 1)
        self.assertEqual(len(record.fields[0].subfields), 2)

    def test_all_1(self):
        pass

    def test_clear_1(self):
        record = MarcRecord()
        record.add(100, 'Some value')
        record.clear()
        self.assertEqual(len(record.fields), 0)

    def test_clone_1(self):
        original = MarcRecord()
        original.database = 'IBIS'
        original.add(100, 'Some value')
        clone = original.clone()
        self.assertEqual(original.database, clone.database)
        self.assertEqual(original.mfn, clone.mfn)
        self.assertEqual(original.status, clone.status)
        self.assertEqual(original.version, clone.version)
        self.assertEqual(len(original.fields), len(clone.fields))

    def test_fm_1(self):
        record = MarcRecord()
        record.add(100, 'Field 100')
        record.add(200, 'Field 200')
        self.assertEqual('Field 100', record.fm(100))
        self.assertEqual('Field 200', record.fm(200))
        self.assertIsNone(record.fm(300))

    def test_fm_2(self):
        record = MarcRecord()
        record.add(100, '', SubField('a', '100A'), SubField('b', '100B'))
        record.add(200, '', SubField('b', '200B'), SubField('c', '200C'))
        self.assertEqual('100A', record.fm(100, 'a'))
        self.assertEqual('100B', record.fm(100, 'b'))
        self.assertIsNone(record.fm(100, 'c'))
        self.assertIsNone(record.fm(200, 'a'))
        self.assertEqual('200B', record.fm(200, 'b'))
        self.assertEqual('200C', record.fm(200, 'c'))

    def test_str_1(self):
        record = MarcRecord()
        record.add(100, 'Field 100')
        record.add(200, 'Field 200', SubField('a', 'Subfield A'))
        self.assertEqual('100#Field 100\n200#Field 200^aSubfield A', str(record))


class TestFileSpecification(unittest.TestCase):

    def test_init_1(self):
        spec = FileSpecification(1, '', 'file.ext')
        self.assertEqual(spec.binary, False)
        self.assertEqual(spec.path, 1)
        self.assertEqual(spec.database, '')
        self.assertEqual(spec.filename, 'file.ext')
        self.assertEqual(spec.content, '')

    def test_str_1(self):
        spec = FileSpecification(1, '', 'file.ext')
        self.assertEqual(str(spec), '1..file.ext')

    def test_str_2(self):
        spec = FileSpecification(6, 'IBIS', 'file.ext')
        self.assertEqual(str(spec), '6.IBIS.file.ext')


class TestIrbisFormat(unittest.TestCase):

    def test_comments_1(self):
        self.assertEqual("", IrbisFormat.remove_comments(""))
        self.assertEqual(" ", IrbisFormat.remove_comments(" "))
        self.assertEqual("v100,/,v200", IrbisFormat.remove_comments("v100,/,v200"))
        self.assertEqual("\tv100\r\n", IrbisFormat.remove_comments("\tv100\r\n"))
        self.assertEqual("v100\r\nv200",
                         IrbisFormat.remove_comments("v100/* Comment\r\nv200"))
        self.assertEqual("v100, '/* Not comment', v200",
                         IrbisFormat.remove_comments("v100, '/* Not comment', v200"))
        self.assertEqual("v100, |/* Not comment|, v200",
                         IrbisFormat.remove_comments("v100, |/* Not comment|, v200"))
        self.assertEqual("v100, '/* Not comment', v200, \r\nv300",
                         IrbisFormat.remove_comments("v100, '/* Not comment', v200, /*comment\r\nv300"))

    def test_prepare_1(self):
        self.assertEqual("", IrbisFormat.prepare(""))
        self.assertEqual(" ", IrbisFormat.prepare(" "))
        self.assertEqual("", IrbisFormat.prepare("\r\n"))
        self.assertEqual("v100,/,v200", IrbisFormat.prepare("v100,/,v200"))
        self.assertEqual("v100", IrbisFormat.prepare("\tv100\r\n"))
        self.assertEqual("v100v200",
                         IrbisFormat.prepare("v100/*comment\r\nv200"))
        self.assertEqual("v100",
                         IrbisFormat.prepare("v100/*comment"))


class TestIrbisConnection(unittest.TestCase):

    def test_init_1(self):
        connection = IrbisConnection()
        self.assertEqual(connection.host, 'localhost')
        self.assertEqual(connection.port, 6666)
        self.assertEqual(connection.username, '')
        self.assertEqual(connection.password, '')
        self.assertEqual(connection.database, 'IBIS')
        self.assertEqual(connection.clientId, 0)
        self.assertEqual(connection.queryId, 0)
        self.assertEqual(connection.connected, False)


if __name__ == '__main__':
    unittest.main()

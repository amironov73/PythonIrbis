class SubField:

    def __init__(self, code='\0', value=''):
        self.code = code
        self.value = value

    def clone(self):
        return SubField(self.code, self.value)

    def __str__(self):
        return '^' + self.code + self.value


class RecordField:

    def __init__(self, tag=0, value=''):
        self.tag = tag
        self.value = value
        self.subfields = []

    def add(self, code, value):
        self.subfields.append(SubField(code, value))
        return self

    def clear(self):
        self.subfields = []
        return self

    def clone(self):
        result = RecordField(self.tag, self.value)
        for sf in self.subfields:
            result.subfields.append(sf.clone())
        return result

    def __str__(self):
        return ''


class MarcRecord:

    def __init__(self):
        self.database = ''
        self.mfn = 0
        self.version = 0
        self.status = 0
        self.fields = []

    def add(self, tag, value=''):
        self.fields.append(RecordField(tag, value))
        return self

    def clear(self):
        self.fields.clear()
        return self

    def clone(self):
        result = MarcRecord()
        result.database = self.database
        result.mfn = self.mfn
        result.status = self.status
        result.version = self.version
        for f in self.fields:
            result.fields.append(f.clone())
        return result

    def __str__(self):
        return ''


class FileSpecification:

    def __init__(self, path, database, filename):
        self.binary = False
        self.path = path
        self.database = database
        self.filename = filename
        self.content = ''

    def __str__(self):
        result = self.filename

        if self.binary:
            result = '@' + self.filename
        else:
            if self.content != '':
                result = '&' + self.filename

        if self.path == 0 or self.path == 1:
            result = str(self.path) + '..' + result
        else:
            result = str(self.path) + '.' + self.database + '.' + result

        if self.content != '':
            result = result + '&' + self.content

        return result


class IrbisEncoding:
    pass


class IrbisFormat:
    pass


class IrbisPath:
    pass


class IrbisText:
    pass


class IrbisVersion:

    def __init__(self):
        self.organization = ''
        self.version = ''
        self.max_clients = 0
        self.connected_clients = 0


class UserInfo:
    pass


class ClientQuery:

    def ansi(self, text):
        return self

    def utf(self, text):
        return self

    def encode(self):
        return []


class ServerResponse:
    pass


class IrbisConnection:

    def __init__(self):
        self.host = 'localhost'
        self.port = 6666
        self.username = ''
        self.password = ''
        self.database = 'IBIS'
        self.workstation = 'C'
        self.clientId = 0
        self.queryId = 0
        self.connected = False

    def actualize_record(self, mfn):
        pass

    def connect(self):
        pass

    def create_database(self, database, description, reader_access):
        pass

    def create_dictionary(self, database):
        pass

    def delete_database(self, database):
        pass

    def disconnect(self):
        pass

    def execute(self, query):
        pass

    def format_record(self, script, mfn):
        pass

    def get_server_stat(self):
        pass

    def get_server_version(self):
        pass

    def get_user_list(self):
        pass

    def list_files(self, specification):
        pass

    def list_processes(self):
        pass

    def nop(self):
        pass

    def read_binary_file(self, specification):
        pass

    def read_postings(self, parameters):
        pass

    def read_record(self, mfn):
        pass

    def read_terms(self, parameters):
        pass

    def read_text_file(self, specification):
        pass

    def reload_dictionary(self, database):
        pass

    def reload_master_file(self, database):
        pass

    def restart_server(self):
        pass

    def search(self, parameters):
        pass

    def truncate_database(self, database):
        pass

    def unlock_database(self, database):
        pass

    def unlock_records(self, records):
        pass

    def update_ini_file(self, lines):
        pass

    def write_record(self, record, lock, actualize, dont_parse):
        pass

    def write_text_file(self, specification):
        pass
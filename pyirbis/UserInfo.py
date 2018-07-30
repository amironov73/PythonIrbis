from pyirbis.ServerResponse import ServerResponse


class UserInfo:

    def __init__(self):
        self.number = ''
        self.name = ''
        self.password = ''
        self.cataloger = ''
        self.reader = ''
        self.circulation = ''
        self.acquisitions = ''
        self.provision = ''
        self.administrator = ''

    def parse(self, response: ServerResponse):
        pass

    def __str__(self):
        buffer = [self.number, self.name, self.password, self.cataloger,
                  self.reader, self.circulation, self.acquisitions,
                  self.provision, self.administrator]
        return '\n'.join(buffer)


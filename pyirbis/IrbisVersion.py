class IrbisVersion:
    """
    Информация о версии сервера, числе подключенных/разрешенных клиентов
    и организации, на которую зарегистрирован сервер.
    """

    def __init__(self):
        self.organization = ''
        self.version = ''
        self.max_clients = 0
        self.connected_clients = 0

    def __str__(self):
        buffer = [self.organization, self.version, str(self.connected_clients), str(self.max_clients)]
        return '\n'.join(buffer)


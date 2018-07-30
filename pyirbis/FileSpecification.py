class FileSpecification:
    """
    Путь на файл Αpath.Adbn.Afilename
    Αpath – код путей:
    0 – общесистемный путь.
    1 – путь размещения сведений о базах данных сервера ИРБИС64
    2 – путь на мастер-файл базы данных.
    3 – путь на словарь базы данных.
    10 – путь на параметрию базы данных.
    Adbn – имя базы данных
    Afilename – имя требуемого файла с расширением
    В случае чтения ресурса по пути 0 и 1 имя базы данных не задается.
    """


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


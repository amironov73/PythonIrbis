class SearchParameters:

    def __init__(self):
        self.database = ''
        self.first_record = 1
        self.format = ''
        self.max_mfn = 0
        self.min_mfn = 0
        self.number = 0
        self.expression = ''
        self.sequential = ''
        self.filter = ''
        self.utf = False

    def __str__(self):
        return  self.expression
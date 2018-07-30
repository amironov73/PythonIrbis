class SubField:
    """
    Подполе с кодом и значением.
    """

    def __init__(self, code='\0', value=''):
        self.code = code.lower()
        self.value = value

    def clone(self):
        return SubField(self.code, self.value)

    def __str__(self):
        return '^' + self.code + self.value

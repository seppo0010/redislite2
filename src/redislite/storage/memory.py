from . import BaseStorage


class Storage(BaseStorage):
    pages = {}

    def __init__(self, identifier, database):
        self.identifier = identifier
        self.database = database
        self.database.storage = self

    def read(self, page_num):
        return self.pages[page_num]

    def write(self, pages_data):
        for n, data in pages_data:
            self.pages[n] = data

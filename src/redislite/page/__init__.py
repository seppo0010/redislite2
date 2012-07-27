class BasePage(object):
    def __init__(self, database, page_number=None):
        self.database = database
        self.page_number = page_number

    def unserialize(self, data):
        raise NotImplementedError()

    def serialize(self):
        raise NotImplementedError()

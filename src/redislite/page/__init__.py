class BasePage(object):
    def __init__(self, database):
        self.database = database

    def unserialize(self, data):
        raise NotImplementedError()

    def serialize(self):
        raise NotImplementedError()

from random import randint

from redislite.page import BasePage


class DummyPage(BasePage):
    def __init__(self, database, data=None):
        super(DummyPage, self).__init__(database)
        self.data = data

    def serialize(self):
        return self.data or ''.ljust(self.database.page_size, "\0")

    def unserialize(self, data):
        self.data = data


def randomword(length):
    return ''.join([chr(randint(0, 255)) for i in xrange(0, length)])

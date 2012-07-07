import struct

from redislite.hasher.hashers import HASHERS

from . import BasePage


class DbinfoPage(BasePage):
    btree = None
    hasher = None
    page_size = None
    number_of_pages = None
    freelist_item = None

    def __init__(self, database, btree=None, hasher=None, page_size=None,
            number_of_pages=None, freelist_item=None):
        super(DbinfoPage, self).__init__(database)
        self.btree = btree or 0
        self.hasher = hasher or 'c'
        self.page_size = page_size or 0
        self.number_of_pages = number_of_pages or 0
        self.freelist_item = freelist_item or 0
        self.update_database()

    def serialize(self):
        return struct.pack('!isiii', self.btree, self.hasher, self.page_size,
                self.number_of_pages, self.freelist_item)

    def unserialize(self, data):
        (self.btree, self.hasher, self.page_size, self.number_of_pages,
         self.freelist_item) = struct.unpack('!isiii', data[0:17])
        self.update_database()

    def update_database(self):
        if self.hasher:
            self.database.hasher = HASHERS[self.hasher]

        for k in ('btree', 'page_size', 'number_of_pages', 'freelist_item'):
            if getattr(self, k) is not None:
                setattr(self.database, k, getattr(self, k))

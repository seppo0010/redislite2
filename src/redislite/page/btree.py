import struct
from math import floor

from . import BasePage


class RedislitePageBTree(BasePage):
    parent = None
    elements = None
    right_page = None

    def __init__(self, elements=None, right_page=None, *args, **kwargs):
        super(RedislitePageBTree, self).__init__(*args, **kwargs)
        self.elements = elements or []
        self.right_page = right_page or 0

    @property
    def max_elements(self):
        return int(floor((self.database.page_size - 8) /
                (2 * RedisliteBTreeElement.length(self.database)))) * 2

    def serialize(self):
        data = struct.pack('!ii', len(self.elements), self.right_page)
        for e in self.elements:
            data += e.serialize()
        return data.ljust(self.database.page_size, '\0')

    def unserialize(self, data):
        elements_len, self.right_page = struct.unpack('!ii', data[0:8])
        page_len = RedisliteBTreeElement.length(self.database)
        start = 8
        for i in range(0, elements_len):
            tree = RedisliteBTreeElement(database=self.database)
            tree.unserialize(data[start:(start + page_len)])
            self.elements.append(tree)
            start += page_len

    def search(self, changeset, hash):
        start, end = 0, len(self.elements)
        while start <= end:
            pos = int(floor((end - start) / 2)) + start
            el = self.elements[pos]
            if hash == el.hash:
                return el
            elif hash < el.hash:
                end = pos - 1
            else:
                start = pos + 1

        if el and el.left_page:
            return changeset.read(el.left_page, RedislitePageBTree).search(
                changeset, hash)
        return None


class RedisliteBTreeElement(object):
    database = None
    hash = None
    left_page = None
    page_number = None

    @classmethod
    def length(klass, database):
        return database.hasher.hashed_length + 8

    def __init__(self, database=None, hash=None, left_page=None,
            page_number=None):
        self.database = database
        self.hash = hash
        self.left_page = left_page or 0
        self.page_number = page_number or 0

    def serialize(self):
        return struct.pack('!ii', self.left_page, self.page_number) + self.hash

    def unserialize(self, data):
        self.left_page, self.page_number = struct.unpack('!ii', data[0:8])
        self.hash = data[8:(self.database.hasher.hashed_length + 8)]

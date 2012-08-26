import struct
from math import floor

from . import BasePage


class RedislitePageList(BasePage):
    left_page = None
    right_page = None
    elements = None
    root = None

    def __init__(self, elements=None, right_page=None, left_page=None,
            root=None, *args, **kwargs):
        super(RedislitePageList, self).__init__(*args, **kwargs)
        self.elements = elements or []
        self.left_page = left_page or 0
        self.right_page = right_page or 0
        self.root = root

    @property
    def max_elements(self):
        return int(floor((self.database.page_size - 12) /
                    RedisliteListElement.length(self.database)))

    def serialize(self):
        data = struct.pack('!iii', len(self.elements), self.left_page,
                self.right_page)
        for e in self.elements:
            data += e.serialize()
        return data.ljust(self.database.page_size, '\0')

    def unserialize(self, data):
        elements_len, self.left_page, self.right_page = struct.unpack('!iii',
                data[0:12])
        page_len = RedisliteListElement.length(self.database)
        start = 12
        for i in range(0, elements_len):
            page = RedisliteListElement(database=self.database)
            page.unserialize(data[start:(start + page_len)])
            self.elements.append(page)
            start += page_len

    def check_maximum(self, changeset):
        max_elements = self.max_elements
        if max_elements < len(self.elements):
            right_page = None
            if self.right_page > 0:
                right_page = changeset.read(self.right_page, RedislitePageList)
                if (len(right_page.elements) + len(self.elements) <=
                        max_elements + right_page.max_elements):
                    elements = self.elements + right_page.elements
                    self.elements = elements[:max_elements]
                    right_page.elements = elements[max_elements:]
                    changeset.add(self)
                    changeset.add(right_page)
                    return
            new_right_page = RedislitePageList(root=self.root,
                    left_page=self.page_number, right_page=self.right_page,
                    database=self.database)
            new_right_page.elements = self.elements[
                    -new_right_page.max_elements:]
            self.elements = self.elements[:-new_right_page.max_elements]
            self.right_page = changeset.add(new_right_page)
            if right_page is not None:
                right_page.left_page = self.right_page
                changeset.add(right_page)
            if self.page_number == self.root.left_page or self == self.root:
                self.root.left_page = self.right_page
            changeset.add(self)


class RedislitePageListRoot(RedislitePageList):
    list_size = None

    def __init__(self, list_size=None, *args, **kwargs):
        kwargs['root'] = self
        super(RedislitePageListRoot, self).__init__(*args, **kwargs)
        self.list_size = list_size or 0

    @property
    def max_elements(self):
        return int(floor((self.database.page_size - 16) /
                    RedisliteListElement.length(self.database)))

    def serialize(self):
        data = struct.pack('!i', self.list_size) + super(RedislitePageListRoot,
                self).serialize()
        return data[0:self.database.page_size]

    def unserialize(self, data):
        self.list_size = struct.unpack('!i', data[0:4])[0]
        super(RedislitePageListRoot, self).unserialize(data[4:])

    def lpush(self, changeset, element):
        self.elements.insert(0, element)
        self.list_size += 1
        self.check_maximum(changeset)
        changeset.add(self)

    def rpush(self, changeset, element):
        if self.left_page > 0:
            page = changeset.read(self.left_page, RedislitePageList)
            page.elements.append(element)
            page.check_maximum(changeset)
            changeset.add(page)
        else:
            self.elements.append(element)
            self.check_maximum(changeset)
            changeset.add(self)

    def search(self, changeset, hash):
        page = self
        offset = 0
        while 1:
            for e in page.elements:
                if e.hash == hash:
                    return offset + page.elements.index(e)
            offset += len(page.elements)
            if page.right_page > 0:
                page = changeset.read(page.right_page, RedislitePageList)
            else:
                break
        return -1


class RedisliteListElement(object):
    database = None
    hash = None
    page_number = None

    @classmethod
    def length(klass, database):
        return database.hasher.hashed_length + 4

    def __init__(self, database=None, hash=None, page_number=None):
        self.database = database
        self.hash = hash
        self.page_number = page_number or 0

    def serialize(self):
        return struct.pack('!i', self.page_number) + self.hash

    def unserialize(self, data):
        self.page_number = struct.unpack('!i', data[0:4])[0]
        self.hash = data[4:(self.database.hasher.hashed_length + 4)]

import struct
from math import floor

from . import BasePage


class RedislitePageBTree(BasePage):
    parent = None
    elements = None
    right_page = None

    def __init__(self, elements=None, right_page=None, parent=None, *args,
            **kwargs):
        super(RedislitePageBTree, self).__init__(*args, **kwargs)
        self.elements = elements or []
        self.right_page = right_page or 0
        self.parent = parent

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
            page = RedisliteBTreeElement(database=self.database)
            page.unserialize(data[start:(start + page_len)])
            self.elements.append(page)
            start += page_len

    def hash_location(self, hash):
        start, end = 0, len(self.elements)
        if end == 0:
            return None

        while start < end:
            pos = int(floor((end - start) / 2)) + start
            el = self.elements[pos]
            if hash == el.hash:
                break
            elif hash < el.hash:
                # update pos in case of a break, we need to return where the
                # hash should go
                pos -= 1
                end = pos
            else:
                pos += 1
                start = pos

        # Possible off-by-one. Since we are approaching from both sides we
        # could be left one position to the left of the desired position.
        if pos < len(self.elements) and self.elements[pos].hash < hash:
            pos += 1
        if pos < 0:
            pos = 0
        return pos

    def search(self, changeset, hash):
        location = self.hash_location(hash)
        if location is None:
            return None, self

        if location == len(self.elements):
            if self.right_page == 0:
                return None, self
            page = changeset.read(self.right_page, RedislitePageBTree)
            page.parent = self
            return page.search(changeset, hash)

        el = self.elements[location]
        if el.hash == hash:
            return el, self

        if el and el.left_page:
            page = changeset.read(el.left_page, RedislitePageBTree)
            page.parent = self
            return page.search(changeset, hash)
        return None, self

    def check_maximum(self, changeset):
        max_elements = self.max_elements
        if max_elements < len(self.elements):
            middle = max_elements / 2
            el = self.elements.pop(middle)
            parent = self.parent
            left_half = self.elements[:middle]
            right_half = self.elements[middle:]
            if parent:
                sibling = RedislitePageBTree(elements=left_half,
                        parent=parent, database=self.database)
                self.elements = right_half
                el.left_page = changeset.add(sibling)
                changeset.add(self, page_number=self.page_number)
                parent.add_element(changeset, el, force_page=True)
            else:
                children = (RedislitePageBTree(elements=left_half,
                            parent=self, database=self.database),
                        RedislitePageBTree(elements=right_half,
                            parent=self, database=self.database))
                pages = changeset.add(children[0]), changeset.add(children[1])
                self.elements = [el]
                el.left_page = pages[0]
                self.right_page = pages[1]
                changeset.add(self, page_number=self.page_number)

    def add_element(self, changeset, element, force_page=False):
        location = self.hash_location(element.hash)
        if location is None:
            self.elements.append(element)
        else:
            if not force_page:
                if location == len(self.elements):
                    if self.right_page > 0:
                        page = changeset.read(self.right_page,
                                RedislitePageBTree)
                        return page.add_element(changeset, element)
                elif self.elements[location].left_page > 0:
                    page = changeset.read(self.elements[location].left_page,
                            RedislitePageBTree)
                    return page.add_element(changeset, element)
            self.elements.insert(location, element)
        self.check_maximum(changeset)

    def insert(self, changeset, element, force_insert=False):
        element, page = self.search(changeset, element.hash)
        if element is not None:
            if force_insert:
                return False
            pos = page.elements.index(element)
            page.elements[pos] = element
        else:
            page.add_element(changeset, element)
        return True


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

from math import ceil
import struct

from . import BasePage


class StringPageIndex(BasePage):
    total_length = 0
    next_page = 0
    data = None

    def __init__(self, database, data=None, next_page=0, total_length=0, *args,
            **kwargs):
        super(StringPageIndex, self).__init__(database, *args, **kwargs)
        self.data = data
        self.next_page = next_page
        self.total_length = total_length

    def serialize(self):
        d = self.data.ljust(StringPageIndex.page_size(self.database), chr(0))
        return struct.pack('!iii', self.total_length, len(self.data),
                self.next_page) + d

    def unserialize(self, data):
        self.total_length, page_length, self.next_page = struct.unpack(
                '!iii', data[0:12])
        self.data = data[12:(12 + page_length)]

    @classmethod
    def page_size(klass, database):
        return database.page_size - 12

    @classmethod
    def create(klass, database, changeset, data):
        page_string_index_size = klass.page_size(database)
        extra_needed = len(data) - page_string_index_size
        next_page = 0
        if extra_needed > 0:
            page_string_size = StringPage.page_size(database)
            extra_pages = int(ceil(float(extra_needed) / page_string_size))
            for i in range(0, extra_pages):
                start = (((extra_pages - i - 1) * page_string_size) +
                        page_string_index_size)
                if i == 0:
                    end = start + (extra_needed % page_string_size)
                else:
                    end = start + page_string_size
                page = StringPage(database, data[start:end], next_page)
                next_page = changeset.add(page)
        return changeset.add(klass(database, data[0: page_string_index_size],
                    next_page, len(data)))


class StringPage(BasePage):
    next_page = 0
    data = None

    def __init__(self, database, data=None, next_page=0):
        super(StringPage, self).__init__(database)
        self.data = data
        self.next_page = next_page

    def serialize(self):
        d = self.data.ljust(StringPage.page_size(self.database), chr(0))
        return struct.pack('!ii', len(self.data), self.next_page) + d

    def unserialize(self, data):
        page_length, self.next_page = struct.unpack('!ii', data[0:8])
        self.data = data[8:(8 + page_length)]

    @classmethod
    def page_size(klass, database):
        return database.page_size - 8

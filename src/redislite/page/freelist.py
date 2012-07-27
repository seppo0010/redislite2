import struct

from . import BasePage


class FreelistPage(BasePage):
    next_page = 0

    def __init__(self, database, next_page=0, *args, **kwargs):
        super(FreelistPage, self).__init__(database, *args, **kwargs)
        self.next_page = next_page

    def serialize(self):
        return (struct.pack('!i', self.next_page) +
                ''.ljust(self.database.page_size - 4, "\0"))

    def unserialize(self, data):
        self.next_page, = struct.unpack('!i', data[0:4])

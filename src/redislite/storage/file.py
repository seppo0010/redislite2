import fcntl

from . import BaseStorage


class Storage(BaseStorage):
    def __init__(self, identifier, database):
        self.identifier = identifier
        self.database = database
        self.database.storage = self
        self.fp = open(identifier, 'w+')

    def read(self, page_num):
        self.fp.seek(page_num * self.database.page_size)
        return self.fp.read(self.database.page_size)

    def write(self, pages_data):
        try:
            fcntl.flock(self.fp, fcntl.LOCK_EX)
            for n, data in pages_data:
                self.fp.seek(n * self.database.page_size)
                self.fp.write(data)
            self.fp.flush()
        except Exception, e:
            raise e
        finally:
            fcntl.flock(self.fp, fcntl.LOCK_UN)

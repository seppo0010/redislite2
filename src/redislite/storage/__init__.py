class BaseStorage(object):
    def __init__(self, identifier, database):
        raise NotImplementedError()

    def read(self, page_num):
        raise NotImplementedError()

    def write(self, page_num, data):
        raise NotImplementedError()

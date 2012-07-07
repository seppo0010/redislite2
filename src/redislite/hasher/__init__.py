class BaseHasher(object):
    def __init__(self, identifier):
        self.identifier = identifier

    def hash(self, string):
        raise NotImplementedError()

    @property
    def hashed_length(self):
        raise NotImplementedError()

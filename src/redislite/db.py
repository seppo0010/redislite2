class DB(object):
    storage = None
    hasher = None
    info = None
    btree = None
    page_size = 512
    number_of_pages = 0
    freelist_item = 0

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

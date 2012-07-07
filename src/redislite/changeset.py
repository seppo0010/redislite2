class Changeset(object):
    freelist_item = 0
    number_of_pages = 0
    read_pages = {}
    pages_to_write = []

    def __init__(self, database):
        self.database = database

    def read(self, page_number, klass):
        data = self.database.storage.read(page_number)
        obj = klass(self.database)
        obj.unserialize(data)
        self.read_pages[page_number] = obj
        return obj

    def get_number_of_pages(self):
        if self.number_of_pages > 0:
            return self.number_of_pages
        return self.database.number_of_pages

    def next_freelist_item(self):
        page_number = 0
        if self.freelist_item is not None:
            page_number = self.freelist_item

        if page_number == 0:
            page_number = self.database.freelist_item

        if page_number == 0:
            page_number = self.get_number_of_pages()
            self.number_of_pages = page_number + 1

        return page_number

    def add(self, obj):
        page_number = self.next_freelist_item()
        if page_number == 0:
            page_number = 1

        self.write(page_number, obj)
        return page_number

    def write(self, page_number, obj):
        self.pages_to_write.append((page_number, obj.serialize()))

    def close(self):
        self.database.freelist_item = self.freelist_item
        self.database.number_of_pages = self.number_of_pages
        # TODO: update db info page
        self.database.storage.write(self.pages_to_write)
        self.pages_to_write = []
        self.read_pages = {}

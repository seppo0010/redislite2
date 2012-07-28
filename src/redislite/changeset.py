from math import floor


class Changeset(object):
    freelist_item = 0
    number_of_pages = 0
    read_pages = None
    pages_to_write = None

    def __init__(self, database):
        self.database = database
        self.read_pages = []
        self.pages_to_write = []

    def search_page(self, pages, page):
        start, end = 0, len(pages)
        if end == 0:
            return None

        while start < end:
            pos = int(floor((end - start) / 2)) + start
            el = pages[pos][0]
            if page == el:
                break
            elif page < el:
                # update pos in case of a break, we need to return where the
                # hash should go
                pos -= 1
                end = pos
            else:
                pos += 1
                start = pos

        # Possible off-by-one. Since we are approaching from both sides we
        # could be left one position to the left of the desired position.
        if pos < len(pages) and pages[pos][0] < page:
            pos += 1
        if pos < 0:
            pos = 0
        return pos

    def read(self, page_number, klass):
        pos = self.search_page(self.pages_to_write, page_number)
        if pos is None or self.pages_to_write[pos][0] != page_number:
            pos = self.search_page(self.read_pages, page_number)
            if (pos is not None and len(self.read_pages) > pos and
                    self.read_pages[pos][0] == page_number):
                obj = self.read_pages[pos][1]
            else:
                data = self.database.storage.read(page_number)
                obj = klass(self.database, page_number=page_number)
                obj.unserialize(data)
                if pos is None:
                    self.read_pages.append((page_number, obj))
                else:
                    self.read_pages.insert(pos, (page_number, obj))
        else:
            obj = self.pages_to_write[pos][1]
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

    def add(self, obj, page_number=None):
        if page_number is None:
            page_number = self.next_freelist_item()
            if page_number == 0:
                page_number = 1
            obj.page_number = page_number

        self.write(page_number, obj)
        return page_number

    def write(self, page_number, obj):
        pos = self.search_page(self.pages_to_write, page_number)
        if pos is None:
            self.pages_to_write.append((page_number, obj))
        elif (len(self.pages_to_write) > pos and
                self.pages_to_write[pos][0] == page_number):
            self.pages_to_write[pos] = (page_number, obj)
        else:
            self.pages_to_write.insert(pos, (page_number, obj))

    def close(self):
        self.database.freelist_item = self.freelist_item
        self.database.number_of_pages = self.number_of_pages
        # TODO: update db info page
        self.database.storage.write([(n, p.serialize()) for n, p in
                self.pages_to_write])
        self.pages_to_write = []
        self.read_pages = []

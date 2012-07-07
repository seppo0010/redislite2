from unittest import TestCase

from redislite.db import DB
from redislite.changeset import Changeset
from redislite.storage.memory import Storage
from redislite.page.string import StringPage, StringPageIndex

from . import randomword, DummyPage


class TestPageString(TestCase):
    def setUp(self):
        self.database = DB()
        self.storage = Storage(None, self.database)
        self.changeset = Changeset(self.database)
        self.changeset.add(DummyPage(self.database))  # fill page 0

    def test_encode_decode_single_page_index(self):
        word = randomword(100)
        page = StringPageIndex(self.database, word, total_length=len(word))
        page_copy = StringPageIndex(self.database)
        page_copy.unserialize(page.serialize())
        self.assertEqual((page.total_length, page.next_page, page.data),
                (page_copy.total_length, page_copy.next_page, page_copy.data))

    def test_encode_decode_single_page_noindex(self):
        word = randomword(100)
        page = StringPage(self.database, word)
        page_copy = StringPage(self.database)
        page_copy.unserialize(page.serialize())
        self.assertEqual((page.next_page, page.data),
                (page_copy.next_page, page_copy.data))

    def test_create_single_page(self):
        word = randomword(100)
        page_number = StringPageIndex.create(self.database, self.changeset,
                word)
        self.changeset.close()
        page = StringPageIndex(self.database)
        page.unserialize(self.storage.read(page_number))
        self.assertEqual((page.total_length, page.next_page, page.data),
                (100, 0, word))

    def test_create_multi_page(self):
        word = randomword(1000)
        page_number = StringPageIndex.create(self.database, self.changeset,
                word)
        self.changeset.close()
        page = StringPageIndex(self.database)
        page.unserialize(self.storage.read(page_number))
        self.assertEqual((page.total_length, page.next_page), (1000, 1))

        data = page.data
        next_page = page.next_page
        while next_page > 0:
            page = StringPage(self.database)
            page.unserialize(self.storage.read(next_page))
            data += page.data
            next_page = page.next_page
        self.assertEqual(len(data), len(word))
        self.assertEqual(data, word)

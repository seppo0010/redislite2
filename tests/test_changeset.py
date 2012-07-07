from unittest import TestCase

from redislite.db import DB
from redislite.changeset import Changeset
from redislite.storage.memory import Storage

from . import randomword, DummyPage


class TestChangeset(TestCase):
    def setUp(self):
        self.database = DB()
        self.storage = Storage(None, self.database)
        self.changeset = Changeset(self.database)

    def test_get_page(self):
        data = {}
        for i in range(0, 1):
            word = randomword(512)
            self.storage.write(((i, word), ))
            data[i] = word

        for i in range(0, 1):
            page = self.changeset.read(i, DummyPage)
            self.assertEqual(page.data, data[i])

    def test_write_page(self):
        data = {}
        for i in range(0, 1):
            word = randomword(512)
            self.changeset.write(i, DummyPage(self.database, word))
            data[i] = word

        self.changeset.close()

        for i in range(0, 1):
            page = self.storage.read(i)
            self.assertEqual(page, data[i])

    def test_add(self):
        data = {}
        for i in range(1, 2):
            word = randomword(512)
            self.changeset.add(DummyPage(self.database, word))
            data[i] = word

        self.changeset.close()

        for i in range(1, 2):
            page = self.storage.read(i)
            self.assertEqual(page, data[i])

    def test_add_db_freelist1(self):
        self.do_test_add_db_freelist(1)

    def test_add_db_freelist2(self):
        self.do_test_add_db_freelist(1)

    def test_add_db_freelist3(self):
        self.do_test_add_db_freelist(1)

    def do_test_add_db_freelist(self, freelist_key):
            data = {}
            for i in range(0, 3):
                word = randomword(512)
                self.changeset.add(DummyPage(self.database, word))
                data[i] = word

            self.database.freelist_item = freelist_key
            word = randomword(512)
            self.changeset.add(DummyPage(self.database, word))
            data[freelist_key] = word

            self.changeset.close()

            for i in range(1, 3):
                page = self.storage.read(i)
                self.assertEqual(page, data[i])

    def test_add_changeset_freelist1(self):
        self.do_test_add_changeset_freelist(1)

    def test_add_changeset_freelist2(self):
        self.do_test_add_changeset_freelist(2)

    def do_test_add_changeset_freelist(self, freelist_key):
        data = {}
        for i in range(0, 3):
            word = randomword(512)
            self.changeset.add(DummyPage(self.database, word))
            data[i] = word

        self.changeset.freelist_item = freelist_key
        word = randomword(512)
        self.changeset.add(DummyPage(self.database, word))
        data[freelist_key] = word

        self.changeset.close()

        for i in range(1, 3):
            page = self.storage.read(i)
            self.assertEqual(page, data[i])

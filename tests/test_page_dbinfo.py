from unittest import TestCase

from redislite.db import DB
from redislite.page.dbinfo import DbinfoPage


class TestPageString(TestCase):
    def setUp(self):
        self.database = DB()

    def test_btree(self):
        page = DbinfoPage(self.database, btree=1)
        self.assertEqual(page.btree, self.database.btree)

    def test_btree_unserialize(self):
        page = DbinfoPage(self.database, btree=1)
        new_page = DbinfoPage(self.database)
        self.database.btree = 2
        new_page.unserialize(page.serialize())
        self.assertEqual(page.btree, new_page.btree)
        self.assertEqual(page.btree, self.database.btree)

    def test_page_size(self):
        page = DbinfoPage(self.database, page_size=100)
        self.assertEqual(page.page_size, self.database.page_size)

    def test_page_size_unserialize(self):
        page = DbinfoPage(self.database, page_size=100)
        new_page = DbinfoPage(self.database)
        self.database.page_size = 200
        new_page.unserialize(page.serialize())
        self.assertEqual(page.page_size, new_page.page_size)
        self.assertEqual(page.page_size, self.database.page_size)

    def test_number_of_pages(self):
        page = DbinfoPage(self.database, number_of_pages=1)
        self.assertEqual(page.number_of_pages, self.database.number_of_pages)

    def test_number_of_pages_unserialize(self):
        page = DbinfoPage(self.database, number_of_pages=1)
        new_page = DbinfoPage(self.database)
        self.database.number_of_pages = 2
        new_page.unserialize(page.serialize())
        self.assertEqual(page.number_of_pages, new_page.number_of_pages)
        self.assertEqual(page.number_of_pages, self.database.number_of_pages)

    def test_freelist_item(self):
        page = DbinfoPage(self.database, freelist_item=1)
        self.assertEqual(page.freelist_item, self.database.freelist_item)

    def test_freelist_item_unserialize(self):
        page = DbinfoPage(self.database, freelist_item=1)
        new_page = DbinfoPage(self.database)
        self.database.freelist_item = 2
        new_page.unserialize(page.serialize())
        self.assertEqual(page.freelist_item, new_page.freelist_item)
        self.assertEqual(page.freelist_item, self.database.freelist_item)

    def test_hasher(self):
        page = DbinfoPage(self.database, hasher='c')
        h = self.database.hasher.hash('test')
        new_page = DbinfoPage(self.database)
        self.database.hasher = None
        new_page.unserialize(page.serialize())
        self.assertEqual(h, self.database.hasher.hash('test'))
        self.assertNotEqual(h, self.database.hasher.hash('test2'))

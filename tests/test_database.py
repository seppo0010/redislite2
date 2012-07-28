from unittest import TestCase

from redislite.db import DB
from redislite.hasher.crc32 import Hasher


class TestDatabase(TestCase):
    def create_database(self, **kwargs):
        return DB(**kwargs)

    def test_hasher(self, **kwargs):
        obj = Hasher('c')
        self.assertEqual(self.create_database(hasher=obj).hasher, obj)

    def test_info(self, **kwargs):
        obj = {}
        self.assertEqual(self.create_database(info=obj).info, obj)

    def test_page_size(self, **kwargs):
        obj = 100
        self.assertEqual(self.create_database(page_size=obj).page_size, obj)

    def test_number_of_pages(self, **kwargs):
        obj = 10
        self.assertEqual(self.create_database(number_of_pages=obj
                    ).number_of_pages, obj)

    def test_freelist_item(self, **kwargs):
        obj = 5
        self.assertEqual(self.create_database(freelist_item=obj
                    ).freelist_item, obj)

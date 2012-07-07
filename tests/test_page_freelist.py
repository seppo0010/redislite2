from unittest import TestCase

from redislite.db import DB
from redislite.page.freelist import FreelistPage


class TestPageString(TestCase):
    def setUp(self):
        self.database = DB()

    def test_encode_decode_single_page(self):
        page = FreelistPage(self.database, 5)
        new_page = FreelistPage(self.database)
        new_page.unserialize(page.serialize())
        self.assertEqual(page.next_page, new_page.next_page)

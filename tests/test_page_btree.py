from unittest import TestCase

from redislite.db import DB
from redislite.changeset import Changeset
from redislite.hasher.hashers import HASHERS
from redislite.storage.memory import Storage
from redislite.page.btree import RedislitePageBTree, RedisliteBTreeElement

from . import randomword, DummyPage


class TestPageBTree(TestCase):
    def setUp(self):
        self.database = DB()
        self.database.hasher = HASHERS['c']
        self.storage = Storage(None, self.database)
        self.changeset = Changeset(self.database)
        self.changeset.add(DummyPage(self.database))  # fill page 0
        self.hlength = self.database.hasher.hashed_length
        self.page = RedislitePageBTree(database=self.database)

    def test_btree_max_elements(self):
        self.assertEqual(self.page.max_elements, 42)

    def test_serialize_unserialize(self):
        for i in range(0, self.page.max_elements):
            element = RedisliteBTreeElement(database=self.database,
                    hash=randomword(self.hlength))
            self.page.elements.append(element)
        serialized = self.page.serialize()
        new_page = RedislitePageBTree(database=self.database)
        new_page.unserialize(serialized)
        self.assertEqual(new_page.serialize(), serialized)
        self.assertEqual(len(new_page.elements), self.page.max_elements)

    def test_search_ok(self):
        words = []
        for i in range(0, self.page.max_elements):
            w = randomword(self.hlength)
            words.append(w)
        words.sort()

        for w in words:
            element = RedisliteBTreeElement(database=self.database,
                    hash=w)
            self.page.elements.append(element)

        for w in words:
            self.assertIsNot(self.page.search(None, w), None)

        self.assertIs(self.page.search(None, randomword(self.hlength)), None)
        self.assertIs(self.page.search(None, randomword(self.hlength)), None)
        self.assertIs(self.page.search(None, randomword(self.hlength)), None)

    def test_search_multipage(self):
        pass

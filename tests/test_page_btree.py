from unittest import TestCase

from redislite.db import DB
from redislite.changeset import Changeset
from redislite.hasher.hashers import HASHERS
from redislite.storage.memory import Storage
from redislite.page.btree import RedislitePageBTree, RedisliteBTreeElement

from . import randomword, DummyPage


def print_page_recursive(page, changeset):
    print (page.page_number, [e.__dict__ for e in page.elements],
            page.right_page)
    for e in page.elements:
        if e.left_page:
            print_page_recursive(changeset.read(e.left_page,
                        RedislitePageBTree), changeset)
    if page.right_page:
        print_page_recursive(changeset.read(page.right_page,
                    RedislitePageBTree), changeset)


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

    def test_search_empty(self):
        self.assertIs(self.page.search(None, randomword(self.hlength))[0],
                None)

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

        self.assertIs(self.page.search(None, randomword(self.hlength))[0],
                None)
        self.assertIs(self.page.search(None, randomword(self.hlength))[0],
                None)
        self.assertIs(self.page.search(None, randomword(self.hlength))[0],
                None)

    def test_search_edges(self):
        words = []
        for i in range(0, self.page.max_elements + 2):
            w = randomword(self.hlength)
            words.append(w)
        words.sort()

        for w in words[1:-1]:
            element = RedisliteBTreeElement(database=self.database,
                    hash=w)
            self.page.elements.append(element)

        self.assertIs(self.page.search(None, words[0])[0], None)
        self.assertIs(self.page.search(None, words[-1])[0], None)

    def test_insert_multipage(self):
        old_max_elements = RedislitePageBTree.max_elements
        try:
            # kids, don't do this at home
            RedislitePageBTree.max_elements = 2
            words = []
            for i in range(0, 6):
                w = randomword(self.hlength)
                w = str(i)
                words.append(w)
                element = RedisliteBTreeElement(database=self.database, hash=w,
                        page_number=1)
                self.page.insert(self.changeset, element)

            for w in words:
                self.assertIsNot(self.page.search(self.changeset, w)[0], None)

            self.assertEqual(4, len([item for item in
                        self.changeset.pages_to_write
                        if item[1].__class__ == RedislitePageBTree]))
        finally:
            RedislitePageBTree.max_elements = old_max_elements

    def test_update(self):
        words = set()
        for i in range(0, self.page.max_elements * 2):
            w = randomword(self.hlength)
            words.add(w)

        for w in words:
            element = RedisliteBTreeElement(database=self.database, hash=w,
                    page_number=1)
            self.page.insert(self.changeset, element)

        for w in words:
            element = RedisliteBTreeElement(database=self.database, hash=w,
                    page_number=2)
            self.page.insert(self.changeset, element)

        for w in words:
            self.assertEqual(self.page.search(self.changeset, w
                        )[0].page_number, 2)

    def test_force_insert(self):
        words = set()
        for i in range(0, self.page.max_elements * 2):
            w = randomword(self.hlength)
            words.add(w)

        for w in words:
            element = RedisliteBTreeElement(database=self.database, hash=w,
                    page_number=1)
            self.page.insert(self.changeset, element)

        for w in words:
            element = RedisliteBTreeElement(database=self.database, hash=w,
                    page_number=2)
            self.assertFalse(self.page.insert(self.changeset, element,
                        force_insert=True))

        for w in words:
            self.assertEqual(self.page.search(self.changeset, w
                        )[0].page_number, 1)

    def test_insert_multipage_fuzzy(self):
        words = set()
        for i in range(0, self.page.max_elements * 10):
            w = randomword(self.hlength)
            words.add(w)
            element = RedisliteBTreeElement(database=self.database, hash=w,
                    page_number=1)
            self.page.add_element(self.changeset, element)

        for w in words:
            self.assertIsNot(self.page.search(self.changeset, w)[0], None)

        for i in range(0, self.page.max_elements * 10):
            w = randomword(self.hlength)
            self.assertIs(self.page.search(self.changeset, w)[0], None)

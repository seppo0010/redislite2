from unittest import TestCase
from random import seed, randint

from redislite.db import DB
from redislite.changeset import Changeset
from redislite.hasher.hashers import HASHERS
from redislite.storage.memory import Storage
from redislite.page.list import (RedislitePageList, RedislitePageListRoot,
        RedisliteListElement)

from . import randomword, DummyPage


class TestPageList(TestCase):
    def setUp(self):
        self.database = DB()
        self.database.hasher = HASHERS['c']
        self.storage = Storage(None, self.database)
        self.changeset = Changeset(self.database)
        self.changeset.add(DummyPage(self.database))  # fill page 0
        self.hlength = self.database.hasher.hashed_length
        self.page = RedislitePageListRoot(database=self.database)

    def test_serialize_unserialize(self):
        page = RedislitePageList(database=self.database, left_page=123,
                right_page=45)
        for i in range(0, page.max_elements):
            element = RedisliteListElement(database=self.database,
                    hash=randomword(self.hlength))
            page.elements.append(element)
        serialized = page.serialize()
        new_page = RedislitePageList(database=self.database)
        new_page.unserialize(serialized)
        self.assertEqual(new_page.serialize(), serialized)
        self.assertEqual(len(new_page.elements), page.max_elements)
        for attr in ('left_page', 'right_page'):
            self.assertEqual(getattr(new_page, attr), getattr(page, attr))

    def test_serialize_unserialize_root(self):
        self.page.left_page = 124589102
        self.page.right_page = 12904
        self.page.list_size = 123
        for i in range(0, self.page.max_elements):
            element = RedisliteListElement(database=self.database,
                    hash=randomword(self.hlength), page_number=i)
            self.page.elements.append(element)
        serialized = self.page.serialize()
        new_page = RedislitePageListRoot(database=self.database)
        new_page.unserialize(serialized)
        self.assertEqual(new_page.serialize(), serialized)
        self.assertEqual(len(new_page.elements), self.page.max_elements)

        for attr in ('left_page', 'right_page', 'list_size'):
            self.assertEqual(getattr(new_page, attr), getattr(self.page, attr))

    def test_lpush(self):
        words = []
        m = self.page.max_elements
        for i in range(0, m * 3):
            w = randomword(self.hlength)
            element = RedisliteListElement(database=self.database,
                    hash=w, page_number=i)
            self.page.lpush(self.changeset, element)
            words.insert(0, w)

        for i in range(0, m):
            self.assertEqual(words[i], self.page.elements[i].hash)

        right_page = self.changeset.read(self.page.right_page,
                RedislitePageList)
        for i in range(0, m):
            self.assertEqual(words[i + m], right_page.elements[i].hash)

        right_page = self.changeset.read(right_page.right_page,
                RedislitePageList)
        for i in range(0, m):
            self.assertEqual(words[i + m * 2],
                    right_page.elements[i].hash)

    def test_rpush(self):
        words = []
        m = self.page.max_elements * 3
        for i in range(0, m):
            w = randomword(self.hlength)
            element = RedisliteListElement(database=self.database,
                    hash=w, page_number=i)
            self.page.rpush(self.changeset, element)
            words.append(w)

        page = self.page
        start = 0
        for i in range(0, m):
            self.assertEqual(words[i], page.elements[i - start].hash)
            if i - start + 1 == len(page.elements) and i < m - 1:
                start = i + 1
                page = self.changeset.read(page.right_page, RedislitePageList)

    def test_rpush_lpush(self):
        seed(0)
        words = []
        m = self.page.max_elements * 3

        for i in range(0, m):
            w = randomword(self.hlength)
            element = RedisliteListElement(database=self.database,
                    hash=w, page_number=i)
            if randint(0, 1) == 0:
                self.page.rpush(self.changeset, element)
                words.append(w)
            else:
                self.page.lpush(self.changeset, element)
                words.insert(0, w)

        page = self.page
        start = 0
        for i in range(0, m):
            self.assertEqual(words[i], page.elements[i - start].hash)
            if i - start + 1 == len(page.elements) and i < m - 1:
                start = i + 1
                page = self.changeset.read(page.right_page, RedislitePageList)

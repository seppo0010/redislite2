from unittest import TestCase

from redislite.db import DB
from redislite.storage.memory import Storage

from . import randomword


class TestStorageFile(TestCase):
    def setUp(self):
        self.database = DB()
        self.storage = Storage(None, self.database)

    def test_read(self):
        data = []
        for i in range(0, 1):
            word = randomword(512)
            self.storage.pages[i] = word
            data.append(word)

        for i in range(0, 1):
            self.assertEqual(self.storage.read(i), data[i])

    def test_write(self):
        data = []
        for i in range(0, 4):
            d = randomword(512)
            data.append((i, d))
        self.storage.write(data)
        self.assertEqual(''.join(self.storage.pages.values()),
                ''.join(d[1] for d in data))

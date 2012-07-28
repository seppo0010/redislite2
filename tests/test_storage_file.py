import os
from unittest import TestCase
from tempfile import NamedTemporaryFile

from redislite.db import DB
from redislite.storage.file import Storage

from . import randomword


class TestStorageFile(TestCase):
    def setUp(self):
        with NamedTemporaryFile(delete=False) as fp:
            self.filename = fp.name
        self.database = DB()
        self.storage = Storage(self.filename, self.database)

    def tearDown(self):
        try:
            os.unlink(self.filename)
        except os.OSError:  # pragma: no cover
            pass  # pragma: no cover

    def test_read(self):
        data = randomword(1024)
        with open(self.filename, 'w') as fp:
            fp.write(data)

        for i in range(0, 1):
            self.assertEqual(self.storage.read(i),
                    data[(i * 512):((i + 1) * 512)])

    def test_write(self):
        data = []
        for i in range(0, 4):
            d = randomword(512)
            data.append((i, d))
        self.storage.write(data)
        with open(self.filename, 'r') as fp:
            read = fp.read()
        self.assertEqual(read, ''.join(d[1] for d in data))

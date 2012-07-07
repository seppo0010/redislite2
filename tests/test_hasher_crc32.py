from random import randint
from struct import unpack
from unittest import TestCase
from zlib import crc32

from redislite.hasher.crc32 import Hasher

from . import randomword


class TestHasherCRC32(TestCase):
    def setUp(self):
        self.hasher = Hasher('c')

    def test_length(self):
        self.assertEqual(self.hasher.hashed_length, 4)

    def test_fuzz(self):
        for i in range(0, 20):
            word = randomword(randint(1, 200))
            hashed = self.hasher.hash(word)
            self.assertEqual(len(hashed), 4)
            self.assertEqual(crc32(word), unpack('!i', hashed)[0])

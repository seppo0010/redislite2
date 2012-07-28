from unittest import TestCase

from redislite.hasher import BaseHasher


class TestHasher(TestCase):
    def setUp(self):
        self.hasher = BaseHasher('\0')

    def test_hash_str(self):
        self.assertRaises(NotImplementedError, self.hasher.hash, 'myStr')

    def test_hashed_length(self):
        try:
            self.hasher.hashed_length  # should throw exception
            self.assertTrue(False)
        except NotImplementedError:
            pass

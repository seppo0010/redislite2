from unittest import TestCase

from redislite.storage import BaseStorage


class TestStorage(TestCase):
    def create_instance(self):
        old_init = BaseStorage.__init__

        def tmp_init(obj, identifier, database):
            pass

        BaseStorage.__init__ = tmp_init
        storage = BaseStorage('\0', None)
        BaseStorage.__init__ = old_init
        return storage

    def test_init(self):
        try:
            BaseStorage('\0', None)
            self.assertTrue(False)
        except NotImplementedError:
            pass

    def test_read(self):
        self.assertRaises(NotImplementedError, self.create_instance().read, 1)

    def test_write(self):
        self.assertRaises(NotImplementedError, self.create_instance().write,
                1, 'fake data')

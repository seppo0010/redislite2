from unittest import TestCase

from redislite.page import BasePage


class TestPage(TestCase):
    def setUp(self):
        self.page = BasePage(None)

    def test_unserialize(self):
        self.assertRaises(NotImplementedError, self.page.unserialize, 'myStr')

    def test_serialize(self):
        self.assertRaises(NotImplementedError, self.page.serialize)

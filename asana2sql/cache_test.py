import unittest
import mock

from asana2sql.cache import Cache
from asana2sql.test_fixtures import row

class CacheTestCase(unittest.TestCase):
    def setUp(self):
        self.seed_fn = mock.Mock()
        self.insert_fn = mock.Mock()

        self.cache = Cache(self.seed_fn, self.insert_fn)

    def test_add(self):
        self.seed_fn.return_value = [row(id=1), row(id=2)]

        self.assertIsNone(self.cache.get(3))

        self.cache.add({"id": 3})

        self.assertEqual(self.cache.get(3), {"id": 3})

        self.seed_fn.assert_called_once()
        self.insert_fn.assert_called_once_with({"id": 3})

    def test_get(self):
        self.seed_fn.return_value = [row(id=1), row(id=2)]

        self.assertIsNone(self.cache.get(3))

        self.assertEqual(self.cache.get(1), {"id": 1})
        self.assertEqual(self.cache.get(2), {"id": 2})
        self.assertEqual(self.cache.get(1), {"id": 1})
        self.assertEqual(self.cache.get(2), {"id": 2})

        self.seed_fn.assert_called_once()
        self.insert_fn.assert_not_called()

    def test_custom_key(self):
        self.seed_fn.return_value = [row(foo=1), row(foo=2)]
        self.cache = Cache(self.seed_fn, self.insert_fn, key_name="foo")

        self.assertEqual(self.cache.get(1), {"foo": 1})
        self.assertIsNone(self.cache.get(3))

        self.cache.add({"foo": 3})

        self.assertEqual(self.cache.get(3), {"foo": 3})

        self.seed_fn.assert_called_once()
        self.insert_fn.assert_called_once_with({"foo": 3})

if __name__ == '__main__':
    unittest.main()

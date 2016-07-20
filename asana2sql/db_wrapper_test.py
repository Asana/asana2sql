import unittest
import mock

from asana2sql.db_wrapper import DatabaseWrapper

TEST_SQL = "Test SQL statement"
PARAM1 = "Param 1"
PARAM2 = "Param 2"

class DatabaseWrapperTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = mock.Mock()

    def test_read(self):
        self.conn.cursor().fetchall.return_value = [0, 1]
        self.conn.reset_mock() # Ignore the call above.

        db_wrapper = DatabaseWrapper(self.conn)

        self.assertEqual(db_wrapper.num_reads, 0)
        self.assertEqual(db_wrapper.num_executed, 0)

        self.assertEqual(db_wrapper.read(TEST_SQL, PARAM1, PARAM2), [0, 1])

        self.assertEqual(db_wrapper.num_reads, 1)
        self.assertEqual(db_wrapper.num_executed, 1)

        self.assertEqual(self.conn.mock_calls, [
            mock.call.cursor(),
            mock.call.cursor().execute(TEST_SQL, PARAM1, PARAM2),
            mock.call.cursor().fetchall(),
            ])

    def test_dry_read(self):
        self.conn.cursor().fetchall.return_value = [0, 1]
        self.conn.reset_mock() # Ignore the call above.

        db_wrapper = DatabaseWrapper(self.conn, dry=True)

        self.assertEqual(db_wrapper.num_reads, 0)
        self.assertEqual(db_wrapper.num_executed, 0)

        self.assertEqual(db_wrapper.read(TEST_SQL, PARAM1, PARAM2), [0, 1])

        self.assertEqual(db_wrapper.num_reads, 1)
        self.assertEqual(db_wrapper.num_executed, 1)

        self.assertEqual(self.conn.mock_calls, [
            mock.call.cursor(),
            mock.call.cursor().execute(TEST_SQL, PARAM1, PARAM2),
            mock.call.cursor().fetchall(),
            ])

    def test_write(self):
        db_wrapper = DatabaseWrapper(self.conn)

        self.assertEqual(db_wrapper.num_writes, 0)
        self.assertEqual(db_wrapper.num_executed, 0)

        db_wrapper.write(TEST_SQL, PARAM1, PARAM2)

        self.assertEqual(db_wrapper.num_writes, 1)
        self.assertEqual(db_wrapper.num_executed, 1)

        self.assertEqual(self.conn.mock_calls, [
            mock.call.cursor(),
            mock.call.cursor().execute(TEST_SQL, PARAM1, PARAM2),
            ])

    def test_dry_write(self):
        db_wrapper = DatabaseWrapper(self.conn, dry=True)

        self.assertEqual(db_wrapper.num_writes, 0)
        self.assertEqual(db_wrapper.num_executed, 0)

        db_wrapper.write(TEST_SQL, PARAM1, PARAM2)

        self.assertEqual(db_wrapper.num_writes, 1)
        self.assertEqual(db_wrapper.num_executed, 0)

        self.assertEqual(self.conn.mock_calls, [])


if __name__ == '__main__':
    unittest.main()

import unittest

from asana2sql.field import (SqlType, Field)


class FieldTestCase(unittest.TestCase):
    def test_simple_derived_sql_name(self):
        simple_field = Field("test", SqlType.string)
        self.assertEquals(simple_field.sql_name(), "test")

    def test_complex_sql_name(self):
        simple_field = Field("A test field.", SqlType.string)
        self.assertEquals(simple_field.sql_name(), "a_test_field",
                          "Derived field names should strip punctuation and convert spaces to underscores.")


if __name__ == '__main__':
    unittest.main()

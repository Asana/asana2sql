import unittest

from asana2sql.field import SqlType, Field, SimpleField


class FieldTestCase(unittest.TestCase):
    def test_field_definition(self):
        simple_field = Field("test", SqlType.INTEGER)
        self.assertEquals(simple_field.field_definition_sql(),
                '"test" INTEGER')


class SimpleFieldTestCase(unittest.TestCase):
    def test_required_fields(self):
        simple_field = SimpleField("test", SqlType.INTEGER)
        self.assertSetEqual(simple_field.required_fields(), set(["test"]))

    def test_get_data_from_task(self):
        task = {"test": 123}
        simple_field = SimpleField("test", SqlType.INTEGER)
        self.assertEquals(
                simple_field.get_data_from_task(task), 123)

    def test_field_definition(self):
        simple_field = SimpleField("test", SqlType.INTEGER)
        self.assertEquals(
                simple_field.field_definition_sql(),
                '"test" INTEGER')

    def test_primary_key(self):
        simple_field = SimpleField("test", SqlType.INTEGER, primary_key=True)
        self.assertEquals(
                simple_field.field_definition_sql(),
                '"test" INTEGER NOT NULL PRIMARY KEY')

    def test_default_value(self):
        task = {}
        simple_field = SimpleField("test", SqlType.INTEGER, default=123)
        self.assertEquals(simple_field.get_data_from_task(task), 123)


if __name__ == '__main__':
    unittest.main()

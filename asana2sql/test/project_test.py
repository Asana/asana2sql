import unittest
from mock import Mock

from asana2sql.project import Project
from asana2sql.field import Field
from asana2sql.test import fixtures


class ProjectTestCase(unittest.TestCase):
    def test_derived_table_name(self):
        asana_client = Mock()

        proj = fixtures.project(id=1234, name="Test Table")
        asana_client.projects.find_by_id.return_value = proj

        project = Project(asana_client, 1234, None, [])

        self.assertEquals(project.table_name(), "Test_Table")

    def test_create_empty_table(self):
        asana_client = Mock()
        db_wrapper = Mock()

        project = Project(asana_client, 1234, "test_table", [])

        self.assertEquals(project.table_name(), "test_table")

        project.create_table(db_wrapper)

        db_wrapper.write.assert_called_with(
            '''CREATE TABLE IF NOT EXISTS "test_table" ();''')

    def test_create_table_with_fields(self):
        asana_client = Mock()
        db_wrapper = Mock()

        project = Project(asana_client, 1234, "test_table",
                          [Field("task_id", "BIGINT NOT NULL PRIMARY KEY"),
                           Field("field1", "BIGINT"),
                           Field("Complex and invalid field name.", "VARCHAR(1024)"),
                           Field("a_different_field_name", "FLOAT")])

        self.assertEquals(project.table_name(), "test_table")
        project.create_table(db_wrapper)

        db_wrapper.write.assert_called_with(
                '''CREATE TABLE IF NOT EXISTS "test_table" ('''
                '''"task_id" BIGINT NOT NULL PRIMARY KEY,'''
                '''"field1" BIGINT,'''
                '''"Complex_and_invalid_field_name" VARCHAR(1024),'''
                '''"a_different_field_name" FLOAT);''')

if __name__ == '__main__':
    unittest.main()

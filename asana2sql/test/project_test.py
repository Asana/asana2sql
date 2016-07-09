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

        self.assertEquals(project.table_name(), "test_table")

    def test_create_empty_table(self):
        asana_client = Mock()

        project = Project(asana_client, 1234, "test_table", [])

        self.assertEquals(project.table_name(), "test_table")
        self.assertEquals(project.create_table_sql(),
            '''CREATE TABLE "test_table" (task_id BIGINT NOT NULL,PRIMARY KEY task_id)''')

    def test_create_table_with_fields(self):
        asana_client = Mock()

        project = Project(asana_client, 1234, "test_table",
                          [Field("asana1", "BIGINT", "field1"),
                           Field("asana2", "VARCHAR(1024)", "Complex and invalid field name."),
                           Field("asana3", "FLOAT", "a_different_field_name")])

        self.assertEquals(project.table_name(), "test_table")

        self.assertEquals(
                project.create_table_sql(),
                '''CREATE TABLE "test_table" (task_id BIGINT NOT NULL,'''
                '''"field1" BIGINT,'''
                '''"complex_and_invalid_field_name" VARCHAR(1024),'''
                '''"a_different_field_name" FLOAT,'''
                '''PRIMARY KEY task_id)''')

if __name__ == '__main__':
    unittest.main()

import unittest
import mock

from asana2sql.project import Project
from asana2sql.field import Field, SimpleField, SqlType
from asana2sql import fixtures


class ProjectTestCase(unittest.TestCase):
    def setUp(self):
        self.asana_client = mock.Mock()
        self.db_client = mock.Mock()
        self.config = mock.Mock()
        self.config.project_id = 1234
        self.config.table_name = "test_table"
        self.workspace = mock.Mock()

    def test_derived_table_name(self):
        proj = fixtures.project(id=1234, name="Test Table")
        self.asana_client.projects.find_by_id.return_value = proj
        self.config.table_name = None

        project = Project(self.asana_client, self.db_client, self.workspace, self.config, [])

        self.assertEquals(project.table_name(), "Test_Table")

    def test_create_empty_table(self):
        project = Project(self.asana_client, self.db_client, self.workspace, self.config, [])

        project.create_table()

        self.db_client.write.assert_called_with(
            '''CREATE TABLE IF NOT EXISTS "test_table" ();''')

    def test_create_table_with_fields(self):
        project = Project(self.asana_client, self.db_client, self.workspace, self.config,
                          [Field("task_id", "BIGINT NOT NULL PRIMARY KEY"),
                           Field("field1", "BIGINT"),
                           Field("Complex field name.", "VARCHAR(1024)"),
                           Field("a_different_field_name", "FLOAT")])

        project.create_table()

        self.db_client.write.assert_called_with(
                '''CREATE TABLE IF NOT EXISTS "test_table" ('''
                '''"task_id" BIGINT NOT NULL PRIMARY KEY,'''
                '''"field1" BIGINT,'''
                '''"Complex field name." VARCHAR(1024),'''
                '''"a_different_field_name" FLOAT);''')

    def test_export(self):
        self.asana_client.tasks.find_by_project.return_value = [
                fixtures.task(id=1), fixtures.task(id=2), fixtures.task(id=3)]

        project = Project(self.asana_client, self.db_client, self.workspace, self.config,
                          [SimpleField("id", SqlType.INTEGER)])
        project.export()

        self.asana_client.tasks.find_by_project.assert_called_with(
                1234, fields="id")
        self.db_client.read.assert_not_called()
        self.db_client.write.assert_has_calls([
                mock.call('INSERT OR REPLACE INTO "test_table" (id) VALUES (?);', 1),
                mock.call('INSERT OR REPLACE INTO "test_table" (id) VALUES (?);', 2),
                mock.call('INSERT OR REPLACE INTO "test_table" (id) VALUES (?);', 3)])

    def test_synchronize(self):
        existing_rows = [fixtures.row(id=1), fixtures.row(id=2), fixtures.row(id=3)]
        self.db_client.read.return_value = existing_rows

        self.asana_client.tasks.find_by_project.return_value = [
                fixtures.task(id=2), fixtures.task(id=3), fixtures.task(id=4)]

        project = Project(self.asana_client, self.db_client, self.workspace, self.config,
                          [SimpleField("id", SqlType.INTEGER)])
        project.synchronize()

        self.asana_client.tasks.find_by_project.assert_called_with(
                1234, fields="id")
        self.db_client.read.assert_called_with('SELECT id FROM "test_table";')
        self.db_client.write.assert_called_with(
                'DELETE FROM "test_table" WHERE id = ?;', 1)
        self.db_client.write.assert_has_calls([
                mock.call('INSERT OR REPLACE INTO "test_table" (id) VALUES (?);', 2),
                mock.call('INSERT OR REPLACE INTO "test_table" (id) VALUES (?);', 3),
                mock.call('INSERT OR REPLACE INTO "test_table" (id) VALUES (?);', 4)])


if __name__ == '__main__':
    unittest.main()

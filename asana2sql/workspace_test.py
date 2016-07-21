import unittest
import mock

from asana2sql.workspace import Workspace
from asana2sql import workspace
from asana2sql import test_fixtures as fixtures


class WorkspaceTestCase(unittest.TestCase):
    def setUp(self):
        self.client = mock.Mock()
        self.db_client = mock.Mock()
        self.config = mock.Mock()

        self.config.projects_table_name = None
        self.config.project_memberships_table_name = None
        self.config.users_table_name = None
        self.config.followers_table_name = None
        self.config.custom_fields_table_name = None
        self.config.custom_field_enum_values_table_name = None
        self.config.custom_field_values_table_name = None

    def test_default_table_names(self):
        ws = Workspace(self.client, self.db_client, self.config)

        self.assertEqual(ws.projects_table_name(),
                workspace.PROJECTS_TABLE_NAME)
        self.assertEqual(ws.project_memberships_table_name(),
                workspace.PROJECT_MEMBERSHIPS_TABLE_NAME)
        self.assertEqual(ws.users_table_name(), workspace.USERS_TABLE_NAME)
        self.assertEqual(ws.followers_table_name(),
                workspace.FOLLOWERS_TABLE_NAME)
        self.assertEqual(ws.custom_fields_table_name(),
                workspace.CUSTOM_FIELDS_TABLE_NAME)
        self.assertEqual(ws.custom_field_enum_values_table_name(),
                workspace.CUSTOM_FIELD_ENUM_VALUES_TABLE_NAME)
        self.assertEqual(ws.custom_field_values_table_name(),
                workspace.CUSTOM_FIELD_VALUES_TABLE_NAME)

    def test_custom_table_name(self):
        self.config.projects_table_name = "custom projects"
        self.config.project_memberships_table_name = "custom project_memberships"
        self.config.users_table_name = "custom users"
        self.config.followers_table_name = "custom followers"
        self.config.custom_fields_table_name = "custom custom_fields"
        self.config.custom_field_enum_values_table_name = "custom custom_field_enum_values"
        self.config.custom_field_values_table_name = "custom custom_field_values"
        ws = Workspace(self.client, self.db_client, self.config)

        self.assertEqual(ws.projects_table_name(), "custom projects")
        self.assertEqual(ws.project_memberships_table_name(), "custom project_memberships")
        self.assertEqual(ws.users_table_name(), "custom users")
        self.assertEqual(ws.followers_table_name(), "custom followers")
        self.assertEqual(ws.custom_fields_table_name(), "custom custom_fields")
        self.assertEqual(ws.custom_field_enum_values_table_name(), "custom custom_field_enum_values")
        self.assertEqual(ws.custom_field_values_table_name(), "custom custom_field_values")

    def test_create_tables(self):
        ws = Workspace(self.client, self.db_client, self.config)

        ws.create_tables()

        self.db_client.assert_has_calls([
            mock.call.write(
                workspace.CREATE_PROJECTS_TABLE.format(
                    table_name=workspace.PROJECTS_TABLE_NAME)),
            mock.call.write(
                workspace.CREATE_PROJECT_MEMBERSHIPS_TABLE.format(
                    table_name=workspace.PROJECT_MEMBERSHIPS_TABLE_NAME)),
            mock.call.write(
                workspace.CREATE_USERS_TABLE.format(
                    table_name=workspace.USERS_TABLE_NAME)),
            mock.call.write(
                workspace.CREATE_FOLLOWERS_TABLE.format(
                    table_name=workspace.FOLLOWERS_TABLE_NAME)),
            mock.call.write(
                workspace.CREATE_CUSTOM_FIELDS_TABLE.format(
                    table_name=workspace.CUSTOM_FIELDS_TABLE_NAME)),
            mock.call.write(
                workspace.CREATE_CUSTOM_FIELD_ENUM_VALUES_TABLE.format(
                    table_name=workspace.CUSTOM_FIELD_ENUM_VALUES_TABLE_NAME)),
            mock.call.write(
                workspace.CREATE_CUSTOM_FIELD_VALUES_TABLE.format(
                    table_name=workspace.CUSTOM_FIELD_VALUES_TABLE_NAME)),
        ], any_order=True)

    def test_add_new_user(self):
        self.db_client.read.return_value = [fixtures.row(id=1, name="foo")]

        ws = Workspace(self.client, self.db_client, self.config)

        ws.add_user(fixtures.user(id=2, name="bar"))

        self.db_client.write.assert_called_once_with(
                workspace.INSERT_USER.format(
                    table_name=workspace.USERS_TABLE_NAME),
                2, "bar")

    def test_add_same_user(self):
        self.db_client.read.return_value = [fixtures.row(id=1, name="foo")]

        ws = Workspace(self.client, self.db_client, self.config)

        ws.add_user(fixtures.user(id=1, name="foo"))

        self.db_client.write.assert_not_called()

    def test_add_existing_user(self):
        self.db_client.read.return_value = [fixtures.row(id=1, name="foo")]

        ws = Workspace(self.client, self.db_client, self.config)

        ws.add_user(fixtures.user(id=1, name="bar"))

        self.db_client.write.assert_called_once_with(
                workspace.INSERT_USER.format(
                    table_name=workspace.USERS_TABLE_NAME),
                1, "bar")

    def test_add_new_project(self):
        self.db_client.read.return_value = [fixtures.row(id=1, name="foo")]

        ws = Workspace(self.client, self.db_client, self.config)

        ws.add_project(fixtures.project(id=2, name="bar"))

        self.db_client.write.assert_called_once_with(
                workspace.INSERT_PROJECT.format(
                    table_name=workspace.PROJECTS_TABLE_NAME),
                2, "bar")

    def test_add_same_project(self):
        self.db_client.read.return_value = [fixtures.row(id=1, name="foo")]

        ws = Workspace(self.client, self.db_client, self.config)

        ws.add_project(fixtures.project(id=1, name="foo"))

        self.db_client.write.assert_not_called()

    def test_add_existing_project(self):
        self.db_client.read.return_value = [fixtures.row(id=1, name="foo")]

        ws = Workspace(self.client, self.db_client, self.config)

        ws.add_project(fixtures.project(id=1, name="bar"))

        self.db_client.write.assert_called_once_with(
                workspace.INSERT_PROJECT.format(
                    table_name=workspace.PROJECTS_TABLE_NAME),
                1, "bar")


if __name__ == '__main__':
    unittest.main()
